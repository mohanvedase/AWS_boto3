import boto3
import csv

def get_load_balancers():
    elb_client = boto3.client('elbv2', region_name='ap-south-1')
    response = elb_client.describe_load_balancers(PageSize=400)  # Maximum allowed page size
    return response['LoadBalancers']

def get_target_groups(load_balancer_arn):
    elb_client = boto3.client('elbv2', region_name='ap-south-1')
    response = elb_client.describe_target_groups(LoadBalancerArn=load_balancer_arn)
    return response['TargetGroups']

def describe_target_health(target_group_arn):
    elb_client = boto3.client('elbv2', region_name='ap-south-1')
    response = elb_client.describe_target_health(TargetGroupArn=target_group_arn)
    return response['TargetHealthDescriptions']

def main():
    load_balancers = get_load_balancers()
    count_no_targets = 0
    count_one_target = 0
    
    with open('elb_report.csv', mode='w', newline='') as file:
        fieldnames = ['Load Balancer Name', 'Load Balancer Type', 'Target Group Name', 'Registered Targets', 'Creation Time']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for lb in load_balancers:
            lb_name = lb['LoadBalancerName']
            lb_arn = lb['LoadBalancerArn']
            lb_type = lb['Type']
            lb_creation_time = lb['CreatedTime']
            
            # Skip if not an Application Load Balancer
            if lb_type != 'application':
                continue
            
            target_groups = get_target_groups(lb_arn)
            
            for tg in target_groups:
                target_group_arn = tg['TargetGroupArn']
                target_health = describe_target_health(target_group_arn)
                registered_targets = len(target_health) if target_health else 0
                
                writer.writerow({'Load Balancer Name': lb_name,
                                 'Load Balancer Type': lb_type,
                                 'Target Group Name': tg['TargetGroupName'],
                                 'Registered Targets': registered_targets,
                                 'Creation Time': lb_creation_time})
                
                if not target_health:
                    count_no_targets += 1
                elif len(target_health) == 1:
                    count_one_target += 1
    
    print(f"Total number of application load balancers without registered targets: {count_no_targets}")
    print(f"Total number of application load balancers with only one registered target: {count_one_target}")
    
if __name__ == "__main__":
    main()
