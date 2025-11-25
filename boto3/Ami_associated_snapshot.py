import boto3

# Initialize a boto3 client for EC2 in the Mumbai region
ec2_client = boto3.client('ec2', region_name='ap-south-1')

def list_ami_snapshots():
    # Get a list of all AMIs for your account in the Mumbai region
    amis = ec2_client.describe_images(Owners=['self'])['Images']
    
    total_snapshots_count = 0
    ami_snapshot_counts = []

    for ami in amis:
        ami_id = ami['ImageId']
        snapshot_count = 0
        # Check each block device mapping for snapshots
        for device in ami.get('BlockDeviceMappings', []):
            if 'Ebs' in device and 'SnapshotId' in device['Ebs']:
                snapshot_count += 1
        
        ami_snapshot_counts.append((ami_id, snapshot_count))
        total_snapshots_count += snapshot_count

    return ami_snapshot_counts, total_snapshots_count

# Get AMI snapshot counts and the total snapshot count
ami_snapshot_counts, total_snapshots_count = list_ami_snapshots()

# Print snapshot counts for each AMI
for ami_id, snapshot_count in ami_snapshot_counts:
    print(f"AMI ID: {ami_id}, Number of Snapshots: {snapshot_count}")

# Print the grand total of all snapshots
print(f"Total number of snapshots associated with all AMIs: {total_snapshots_count}")
