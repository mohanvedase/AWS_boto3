import boto3
import pandas as pd

# Ensure you're using the correct AWS region
ec2_client = boto3.client('ec2', region_name='ap-south-1')

# Fetch all EBS snapshots for your account in the specified region
response = ec2_client.describe_snapshots(OwnerIds=['self'])

# Initialize a list to store snapshot information
snapshots_info = []

# Loop through each snapshot in the response
for snapshot in response['Snapshots']:
    snapshot_info = {
        'Snapshot ID': snapshot['SnapshotId'],
        # The 'VolumeSize' field represents the size of the original volume, in GiB
        'Size (GiB)': snapshot['VolumeSize'],
        'Volume ID': snapshot['VolumeId'],
        'State': snapshot['State'],
        'Start Time': snapshot['StartTime'].strftime("%Y-%m-%d %H:%M:%S"),
        'Description': snapshot.get('Description', 'N/A'),
        'Encrypted': snapshot['Encrypted']
    }
    snapshots_info.append(snapshot_info)

# Convert the snapshot information into a pandas DataFrame
df_snapshots = pd.DataFrame(snapshots_info)

# Define the path for the output Excel file
# Specify the desired path along with the file name
excel_path = r'D:\awspythonscripts\boto3\ebs_snapshots_info_with_sizes_ap_south_1.xlsx'

# Export the DataFrame to an Excel file
df_snapshots.to_excel(excel_path, index=False, engine='openpyxl')

print(f"Exported EBS snapshots information with sizes to {excel_path}")
