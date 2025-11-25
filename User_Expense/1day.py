import boto3
import pandas as pd
import awswrangler as wr
from datetime import datetime, timezone, timedelta

# AWS Clients
ce_client = boto3.client('ce')  # Cost Explorer
s3_client = boto3.client('s3')  # S3 Client
ec2_client = boto3.client('ec2')  # EC2 Client

# CloudTrail S3 Path
s3_bucket = "aws-cloudtrail-logs-975050024946-388b075e"
s3_prefix = "AWSLogs/975050024946/CloudTrail/"

# Get Running Resources
def get_running_resources():
    instances = ec2_client.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    running_instances = []
    
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            running_instances.append({
                'InstanceId': instance['InstanceId'],
                'Type': instance['InstanceType'],
                'LaunchTime': instance['LaunchTime'].strftime('%Y-%m-%d %H:%M:%S'),
                'State': instance['State']['Name']
            })
    
    return running_instances

# Get Current and Expected Bill (Last 7 Days)
def get_billing():
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    start_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
    
    response = ce_client.get_cost_and_usage(
        TimePeriod={'Start': start_date, 'End': today},
        Granularity='DAILY',
        Metrics=['UnblendedCost']
    )
    
    total_cost = sum(float(day['Total']['UnblendedCost']['Amount']) for day in response['ResultsByTime'])
    daily_average = total_cost / len(response['ResultsByTime'])
    expected_end_of_day_bill = total_cost + daily_average
    
    return total_cost, expected_end_of_day_bill

# Get User Expenses from CloudTrail Logs (Last 7 Days)
def analyze_cloudtrail():
    last_7_days = [(datetime.now(timezone.utc) - timedelta(days=i)).strftime('%Y/%m/%d') for i in range(7)]
    user_costs = {}
    
    for day in last_7_days:
        try:
            logs = wr.s3.read_json(f"s3://{s3_bucket}/{s3_prefix}{day}/")
            for log in logs['Records']:
                user = log.get('userIdentity', {}).get('userName', 'Unknown')
                if user != 'Unknown':
                    user_costs[user] = user_costs.get(user, 0) + 1  # Assuming usage counts towards cost
        except Exception as e:
            print(f"No logs found for {day} or error occurred: {e}")
    
    return user_costs

# Save to CSV
def save_to_csv(user_costs):
    df = pd.DataFrame(user_costs.items(), columns=['User', 'Usage Count'])
    df.to_csv("aws_user_expenses.csv", index=False)
    print("AWS User Expenses saved to aws_user_expenses.csv")

if __name__ == "__main__":
    running_resources = get_running_resources()
    total_cost, expected_bill = get_billing()
    user_expenses = analyze_cloudtrail()
    save_to_csv(user_expenses)
    
    print("Running Resources:", running_resources)
    print(f"Current Bill (Last 7 Days): ${total_cost:.2f}")
    print(f"Expected End of Day Bill: ${expected_bill:.2f}")
