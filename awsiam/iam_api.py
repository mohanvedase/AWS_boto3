import boto3
import datetime

# Initialize AWS services
ce = boto3.client('ce', region_name='us-east-1')  # Specify your AWS region
iam = boto3.client('iam')

# Specify the IAM group name you want to check
group_name = 'herovired'

# Get the list of IAM users in the group
response = iam.get_group(GroupName=group_name)
users_in_group = response['Users']

# Define the start and end dates for the analysis (September 1st to 30th, 2023)
start_date = '2023-09-01'
end_date = '2023-09-30'

# List of metrics to check (in order of preference)
metrics_to_check = ['UnblendedCost', 'AmortizedCost', 'BlendedCost']

# Initialize a dictionary to store cost data for each user
user_costs = {}

# Iterate through IAM users in the group
for user in users_in_group:
    username = user['UserName']
    account_id = user['Arn'].split(":")[4]
    
    # Get the account's billing information for the specified time period
    try:
        results = ce.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='DAILY',
            Metrics=metrics_to_check,
            Filter={
                'Dimensions': {
                    'Key': 'LINKED_ACCOUNT',
                    'Values': [account_id]
                }
            }
        )

        # Calculate the total cost for the user if available
        if 'ResultsByTime' in results:
            total_cost = 0
            for result in results.get('ResultsByTime', []):
                total_cost += float(result.get('Total', {}).get('UnblendedCost', {}).get('Amount', 0))

            user_costs[username] = total_cost
        else:
            user_costs[username] = 0.0
    except Exception as e:
        user_costs[username] = 0.0

# Print the cost utilization for each IAM user
for username, cost in user_costs.items():
    print(f"IAM User: {username}")
    print(f"Cost: ${cost:.2f}")
    print()