import boto3
import pandas as pd
import awswrangler as wr
from datetime import datetime, timezone, timedelta

# AWS Clients
ce_client = boto3.client('ce')  # Cost Explorer
s3_client = boto3.client('s3')  # S3 Client
ec2_client = boto3.client('ec2')  # EC2 Client

# CloudTrail S3 Path
s3_bucket = "aws-cloudtrail-logs-975050024946-388b075e" #s3://aws-cloudtrail-logs-975050024946-388b075e/AWSLogs/975050024946/CloudTrail/
s3_prefix = "AWSLogs/975050024946/CloudTrail/"

# Get CloudTrail Logs from S3
def list_s3_objects(prefix):
    response = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=prefix)
    if "Contents" in response:
        return [obj["Key"] for obj in response["Contents"]]
    return []

# Get User Expenses from CloudTrail Logs (Last 7 Days)
def analyze_cloudtrail():
    last_7_days = [(datetime.now(timezone.utc) - timedelta(days=i)).strftime('%Y/%m/%d') for i in range(7)]
    user_costs = {}

    for day in last_7_days:
        day_prefix = f"{s3_prefix}{day}/"
        objects = list_s3_objects(day_prefix)

        if not objects:
            print(f"No logs found for {day} in {day_prefix}")
            continue

        for obj_key in objects:
            if obj_key.endswith(".json.gz") or obj_key.endswith(".json"):  # Ensure we only process JSON logs
                try:
                    logs = wr.s3.read_json(f"s3://{s3_bucket}/{obj_key}")
                    for log in logs['Records']:
                        user = log.get('userIdentity', {}).get('userName', 'Unknown')
                        if user != 'Unknown':
                            user_costs[user] = user_costs.get(user, 0) + 1  # Count API usage
                except Exception as e:
                    print(f"Error reading {obj_key}: {e}")

    return user_costs

# Save to CSV
def save_to_csv(user_costs):
    df = pd.DataFrame(user_costs.items(), columns=['User', 'Usage Count'])
    df.to_csv("aws_user_expenses.csv", index=False)
    print("AWS User Expenses saved to aws_user_expenses.csv")

if __name__ == "__main__":
    user_expenses = analyze_cloudtrail()
    save_to_csv(user_expenses)
    print("User Expense Analysis Completed.")
