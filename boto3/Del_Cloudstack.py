import boto3
from datetime import datetime, timezone, timedelta

# Change this to your region
region_name = "eu-west-1"

# Initialize CloudFormation client in specific region
cf = boto3.client("cloudformation", region_name=region_name)

# Set threshold (30 days)
days_threshold = 20
cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_threshold)

def delete_old_stacks():
    paginator = cf.get_paginator('list_stacks')
    page_iterator = paginator.paginate(
        StackStatusFilter=[
            'CREATE_COMPLETE',
            'ROLLBACK_COMPLETE',
            'UPDATE_COMPLETE',
            'UPDATE_ROLLBACK_COMPLETE'
        ]
    )

    for page in page_iterator:
        for stack in page['StackSummaries']:
            stack_name = stack['StackName']
            creation_time = stack['CreationTime']

            if creation_time < cutoff_date:
                print(f"Deleting stack: {stack_name}, Created on: {creation_time}, Region: {region_name}")
                try:
                    cf.delete_stack(StackName=stack_name)
                except Exception as e:
                    print(f"❌ Could not delete stack {stack_name}: {str(e)}")

if __name__ == "__main__":
    delete_old_stacks()
