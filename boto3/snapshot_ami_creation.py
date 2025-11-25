import boto3
import csv

# Define the AWS region and instance names
region = 'ap-south-1'  # Mumbai region
instance_names = ['instance1', 'instance2']  # Replace with your instance names
csv_file = 'instances_info.csv'

# Create a boto3 client for EC2
ec2_client = boto3.client('ec2', region_name=region)

def create_snapshot(instance_id, instance_name):
    # Create snapshot
    response = ec2_client.create_snapshot(
        Description=f'Snapshot for {instance_name}',
        VolumeId=instance_id
    )
    snapshot_id = response['SnapshotId']
    snapshot_name = f'{instance_name}_snapshot'
    # Add name tag to the snapshot
    ec2_client.create_tags(
        Resources=[snapshot_id],
        Tags=[
            {'Key': 'Name', 'Value': snapshot_name}
        ]
    )
    print(f'Snapshot created: {snapshot_id}')
    return snapshot_id

def create_image(instance_id, instance_name):
    # Create image
    response = ec2_client.create_image(
        Description=f'Image for {instance_name}',
        InstanceId=instance_id,
        Name=instance_name
    )
    image_id = response['ImageId']
    print(f'Image created: {image_id}')
    return image_id

def write_to_csv(instance_name, snapshot_id, image_id):
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([instance_name, snapshot_id, image_id])

def main():
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Instance Name', 'Snapshot ID', 'Image ID'])

    # Iterate over instance names
    for instance_name in instance_names:
        # Describe instances to get instance id
        response = ec2_client.describe_instances(
            Filters=[
                {'Name': 'tag:Name', 'Values': [instance_name]}
            ]
        )
        # Extract instance id
        instance_id = response['Reservations'][0]['Instances'][0]['InstanceId']
        
        # Create snapshot and image
        snapshot_id = create_snapshot(instance_id, instance_name)
        image_id = create_image(instance_id, instance_name)

        # Write instance info to CSV file
        write_to_csv(instance_name, snapshot_id, image_id)

if __name__ == "__main__":
    main()