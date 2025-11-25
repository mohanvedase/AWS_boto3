import boto3
from datetime import datetime, timedelta
import pandas as pd
import pytz

# Ensure you're using the correct AWS region
ec2_client = boto3.client('ec2', region_name='ap-south-1')

# Fetch all EBS snapshots for your account in the specified region
response = ec2_client.describe_snapshots(OwnerIds=['self'])

# Initialize a list to store snapshot information
snapshots_info = []

# Get the local time zone
local_tz = pytz.timezone('Asia/Kolkata')  # Adjust to your local time zone

# Get the current time in the local time zone
now_local = datetime.now(local_tz)

# Calculate the date 30 days ago in the local time zone
thirty_days_ago_local = now_local - timedelta(days=30)

# Loop through each snapshot in the response
for snapshot in response['Snapshots']:
    # Get the start time of the snapshot and convert it to the local time zone
    start_time = snapshot['StartTime'].astimezone(local_tz)
    
    # Check if the start time is older than 30 days, excluding those exactly 30 days old
    if start_time < thirty_days_ago_local:
        snapshot_info = {
            'Snapshot ID': snapshot['SnapshotId'],
            'Size (GiB)': snapshot['VolumeSize'],
            'Volume ID': snapshot['VolumeId'],
            'State': snapshot['State'],
            'Start Time': start_time.strftime("%Y-%m-%d %H:%M:%S"),
            'Description': snapshot.get('Description', 'N/A'),
            'Encrypted': snapshot['Encrypted']
        }
        snapshots_info.append(snapshot_info)

# Convert the filtered snapshot information into a pandas DataFrame
df_snapshots = pd.DataFrame(snapshots_info)

# Define the path for the output Excel file
excel_path = r'D:\awspythonscripts\boto3\ebs_snapshots_info_older_than_30_days.xlsx'

# Export the DataFrame to an Excel file
df_snapshots.to_excel(excel_path, index=False, engine='openpyxl')

print(f"Exported EBS snapshots older than 30 days to {excel_path}")
