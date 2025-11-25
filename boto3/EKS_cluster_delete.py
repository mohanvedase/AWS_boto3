import boto3
import time
from botocore.exceptions import ClientError

REGION = "us-west-2"  # Change to your desired AWS region
CLUSTER_NAME = "learnerreport"

eks = boto3.client("eks", region_name=REGION)
ec2 = boto3.client("ec2", region_name=REGION)
elb = boto3.client("elb", region_name=REGION)
elbv2 = boto3.client("elbv2", region_name=REGION)
autoscaling = boto3.client("autoscaling", region_name=REGION)

def wait_for_deletion(list_func, list_args, key, value):
    """Wait until the resource with the given name is no longer in the list."""
    print(f"Waiting for {key} '{value}' to be deleted...")
    while True:
        response = list_func(**list_args)
        items = response.get(key, [])
        # Handle if the items are strings (e.g., list_clusters)
        if items and isinstance(items[0], str):
            if value not in items:
                print(f"{key.capitalize()} '{value}' deleted successfully.")
                break
        else:
            # For dictionary-based items
            if not any(item.get("ClusterName", "") == value for item in items):
                print(f"{key.capitalize()} '{value}' deleted successfully.")
                break
        time.sleep(10)

def delete_nodegroups(cluster_name):
    response = eks.list_nodegroups(clusterName=cluster_name)
    for nodegroup in response["nodegroups"]:
        print(f"Deleting managed node group: {nodegroup}")
        eks.delete_nodegroup(clusterName=cluster_name, nodegroupName=nodegroup)
        waiter = eks.get_waiter("nodegroup_deleted")
        waiter.wait(clusterName=cluster_name, nodegroupName=nodegroup)
        print(f"Deleted managed node group: {nodegroup}")

def delete_asgs():
    response = autoscaling.describe_auto_scaling_groups()
    for asg in response['AutoScalingGroups']:
        name = asg['AutoScalingGroupName']
        print(f"Deleting ASG: {name}")
        autoscaling.update_auto_scaling_group(AutoScalingGroupName=name, MinSize=0, DesiredCapacity=0)
        time.sleep(5)
        autoscaling.delete_auto_scaling_group(AutoScalingGroupName=name, ForceDelete=True)

def delete_launch_templates():
    ec2_client = boto3.client("ec2", region_name=REGION)
    response = ec2_client.describe_launch_templates()
    for lt in response["LaunchTemplates"]:
        try:
            print(f"Deleting Launch Template: {lt['LaunchTemplateName']}")
            ec2_client.delete_launch_template(LaunchTemplateId=lt["LaunchTemplateId"])
        except ClientError as e:
            print(f"Could not delete Launch Template: {e}")

def get_cluster_vpc_id(cluster_name):
    response = eks.describe_cluster(name=cluster_name)
    return response["cluster"]["resourcesVpcConfig"]["vpcId"]

def clean_vpc_dependencies(vpc_id):
    print(f"Cleaning resources in VPC: {vpc_id}")
    filters = [{"Name": "vpc-id", "Values": [vpc_id]}]

    # EC2 instances
    ec2_instances = ec2.describe_instances(Filters=filters)
    for reservation in ec2_instances["Reservations"]:
        for instance in reservation["Instances"]:
            print(f"Terminating instance: {instance['InstanceId']}")
            ec2.terminate_instances(InstanceIds=[instance["InstanceId"]])
    time.sleep(10)

    # ENIs
    enis = ec2.describe_network_interfaces(Filters=filters)
    for eni in enis["NetworkInterfaces"]:
        try:
            print(f"Deleting ENI: {eni['NetworkInterfaceId']}")
            ec2.delete_network_interface(NetworkInterfaceId=eni["NetworkInterfaceId"])
        except ClientError as e:
            print(f"Could not delete ENI: {e}")

    # Classic ELB
    elbs = elb.describe_load_balancers()
    for elb_desc in elbs["LoadBalancerDescriptions"]:
        if elb_desc["VPCId"] == vpc_id:
            print(f"Deleting ELB: {elb_desc['LoadBalancerName']}")
            elb.delete_load_balancer(LoadBalancerName=elb_desc["LoadBalancerName"])

    # ALB/NLB
    elbv2s = elbv2.describe_load_balancers()
    for lb in elbv2s["LoadBalancers"]:
        if lb["VpcId"] == vpc_id:
            print(f"Deleting ELBV2: {lb['LoadBalancerArn']}")
            elbv2.delete_load_balancer(LoadBalancerArn=lb["LoadBalancerArn"])

    # NAT Gateway
    nat_gws = ec2.describe_nat_gateways(Filters=filters)
    for nat in nat_gws["NatGateways"]:
        print(f"Deleting NAT Gateway: {nat['NatGatewayId']}")
        ec2.delete_nat_gateway(NatGatewayId=nat["NatGatewayId"])
    time.sleep(20)

    # EIPs
    addresses = ec2.describe_addresses()
    for addr in addresses["Addresses"]:
        if addr.get("AssociationId"):
            try:
                print(f"Disassociating and releasing EIP: {addr['AllocationId']}")
                ec2.disassociate_address(AssociationId=addr["AssociationId"])
            except Exception: pass
        if addr.get("AllocationId"):
            try:
                ec2.release_address(AllocationId=addr["AllocationId"])
            except Exception: pass

    # IGWs
    igws = ec2.describe_internet_gateways(Filters=filters)
    for igw in igws["InternetGateways"]:
        for attachment in igw["Attachments"]:
            if attachment["VpcId"] == vpc_id:
                print(f"Detaching and deleting IGW: {igw['InternetGatewayId']}")
                ec2.detach_internet_gateway(InternetGatewayId=igw["InternetGatewayId"], VpcId=vpc_id)
                ec2.delete_internet_gateway(InternetGatewayId=igw["InternetGatewayId"])

    # Route Tables
    route_tables = ec2.describe_route_tables(Filters=filters)
    for rt in route_tables["RouteTables"]:
        main = any(assoc.get("Main") for assoc in rt.get("Associations", []))
        if not main:
            print(f"Deleting route table: {rt['RouteTableId']}")
            ec2.delete_route_table(RouteTableId=rt["RouteTableId"])

    # Subnets
    subnets = ec2.describe_subnets(Filters=filters)
    for subnet in subnets["Subnets"]:
        try:
            print(f"Deleting subnet: {subnet['SubnetId']}")
            ec2.delete_subnet(SubnetId=subnet["SubnetId"])
        except ClientError as e:
            print(f"Could not delete subnet: {e}")

    # Security Groups (except default)
    sgs = ec2.describe_security_groups(Filters=filters)
    for sg in sgs["SecurityGroups"]:
        if sg["GroupName"] != "default":
            try:
                print(f"Deleting security group: {sg['GroupId']}")
                ec2.delete_security_group(GroupId=sg["GroupId"])
            except ClientError as e:
                print(f"Could not delete SG: {e}")

def delete_vpc(vpc_id):
    default_vpcs = ec2.describe_vpcs(Filters=[{"Name": "isDefault", "Values": ["true"]}])
    default_ids = [v["VpcId"] for v in default_vpcs["Vpcs"]]
    if vpc_id in default_ids:
        print("Skipping default VPC.")
        return

    clean_vpc_dependencies(vpc_id)

    try:
        print(f"Deleting VPC: {vpc_id}")
        ec2.delete_vpc(VpcId=vpc_id)
    except ClientError as e:
        print(f"Could not delete VPC: {e}")

def main():
    print(f"Starting deletion for EKS Cluster: {CLUSTER_NAME}")
    delete_nodegroups(CLUSTER_NAME)
    eks.delete_cluster(name=CLUSTER_NAME)
    print("Waiting for EKS cluster to be deleted...")
    wait_for_deletion(eks.list_clusters, {}, "clusters", CLUSTER_NAME)
    print("EKS Cluster deleted successfully.")

    delete_asgs()
    delete_launch_templates()

    eks_vpc_id = get_cluster_vpc_id(CLUSTER_NAME)
    delete_vpc(eks_vpc_id)
    print(f"Cleanup completed for cluster: {CLUSTER_NAME}")

if __name__ == "__main__":
    main()
