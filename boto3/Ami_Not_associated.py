import boto3

# Initialize a boto3 client for EC2 in the Mumbai region
ec2_client = boto3.client('ec2', region_name='ap-south-1')

def get_snapshots_associated_with_amis():
    # Get a list of all AMIs for your account in the Mumbai region
    amis = ec2_client.describe_images(Owners=['self'])['Images']
    
    associated_snapshot_ids = set()

    for ami in amis:
        # Check each block device mapping for snapshots
        for device in ami.get('BlockDeviceMappings', []):
            if 'Ebs' in device and 'SnapshotId' in device['Ebs']:
                associated_snapshot_ids.add(device['Ebs']['SnapshotId'])

    return associated_snapshot_ids

def find_unassociated_snapshots():
    # Get all snapshot IDs associated with AMIs
    associated_snapshot_ids = get_snapshots_associated_with_amis()
    
    # Get all snapshots in the account
    all_snapshots = ec2_client.describe_snapshots(OwnerIds=['self'])['Snapshots']
    
    # Find snapshots not associated with any AMI
    unassociated_snapshots = [snapshot['SnapshotId'] for snapshot in all_snapshots if snapshot['SnapshotId'] not in associated_snapshot_ids]
    
    return unassociated_snapshots

# Find and print snapshots not associated with any AMI
unassociated_snapshots = find_unassociated_snapshots()
print(f"Snapshots not associated with any AMI: {unassociated_snapshots}")
