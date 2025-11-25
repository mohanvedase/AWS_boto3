import boto3
from datetime import datetime, timedelta, timezone

def delete_old_snapshots():
    # Create the EC2 client
    ec2 = boto3.client('ec2', region_name='ap-south-1')

    # Get current timestamp in UTC
    current_time = datetime.now(timezone.utc)

    # Calculate the timestamp for 30 days ago
    thirty_days_ago = current_time - timedelta(days=30)

    # Retrieve all snapshots
    try:
        response = ec2.describe_snapshots(OwnerIds=['self'])
    except boto3.exceptions.ClientError as e:
        print("Error calling AWS API: ", e)
        return

    snapshots = response['Snapshots']

    # Iterate through each snapshot and delete if older than 30 days
    for snapshot in snapshots:
        snapshot_time = snapshot['StartTime'].replace(tzinfo=timezone.utc)

        if snapshot_time < thirty_days_ago:
            try:
                print(f"Deleting snapshot {snapshot['SnapshotId']} created at {snapshot_time}")
                ec2.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
            except boto3.exceptions.ClientError as e:
                print("Error calling AWS API: ", e)

if __name__ == "__main__":
    delete_old_snapshots()
