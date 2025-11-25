import boto3

def get_unattached_amis():
    ec2 = boto3.client('ec2', region_name='ap-south-1')
    
    # Get a list of all AMIs
    amis_response = ec2.describe_images(Owners=['self'])
    all_amis = amis_response['Images']
    
    # Get a list of all EBS volumes
    volumes_response = ec2.describe_volumes()
    all_volumes = volumes_response['Volumes']
    attached_amis = set()
    
    # Get AMIs attached to EBS volumes
    for volume in all_volumes:
        if 'Attachments' in volume:
            for attachment in volume['Attachments']:
                if 'InstanceId' in attachment:
                    instance_id = attachment['InstanceId']
                    instance_response = ec2.describe_instances(InstanceIds=[instance_id])
                    instance = instance_response['Reservations'][0]['Instances'][0]
                    if 'ImageId' in instance:
                        attached_amis.add(instance['ImageId'])
    
    # Find unattached AMIs
    unattached_amis = [ami for ami in all_amis if ami['ImageId'] not in attached_amis]
    
    return unattached_amis

def main():
    unattached_amis = get_unattached_amis()
    if unattached_amis:
        print("Unattached AMIs:")
        for ami in unattached_amis:
            print(f"AMI ID: {ami['ImageId']}")
    else:
        print("No unattached AMIs found.")

if __name__ == "__main__":
    main()
