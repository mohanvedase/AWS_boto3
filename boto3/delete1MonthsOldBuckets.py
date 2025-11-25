import boto3
from datetime import datetime, timezone, timedelta

# Initialize S3 client
s3 = boto3.client('s3')
s3_resource = boto3.resource('s3')

# Buckets to skip
skip_buckets = {
    "billpurpose119",
    "aws-cloudtrail-logs-975050024946-56287e95",
    "aws-cloudtrail-logs-975050024946-3e1dc43f",
    "aws-cloudtrail-logs-975050024946-388b075e",
    "aws-cloudtrail-logs-975050024946-2402dadd",
    "findmyfaculty",
    "buildpropk",
    "herov-automation-reports"
}

# Time thresholds
now = datetime.now(timezone.utc)
one_months_ago = now - timedelta(days=30)
twenty_days_ago = now - timedelta(days=15)

def is_frequently_updated(bucket_name):
    try:
        bucket = s3_resource.Bucket(bucket_name)
        for obj in bucket.objects.all():
            if obj.last_modified >= twenty_days_ago:
                return True
        return False
    except Exception as e:
        print(f"Error checking updates in {bucket_name}: {e}")
        return True  # assume updated to be safe

def delete_bucket(bucket_name):
    try:
        bucket = s3_resource.Bucket(bucket_name)
        # Delete all objects
        bucket.objects.all().delete()
        # Delete all versioned objects if versioning is enabled
        try:
            bucket.object_versions.all().delete()
        except Exception:
            pass
        # Delete bucket
        bucket.delete()
        print(f"Deleted bucket: {bucket_name}")
    except Exception as e:
        print(f"Failed to delete bucket {bucket_name}: {e}")

# Main logic
response = s3.list_buckets()
for bucket in response['Buckets']:
    name = bucket['Name']
    creation_date = bucket['CreationDate']

    if name in skip_buckets:
        print(f"Skipping bucket: {name}")
        continue

    if creation_date < one_months_ago:
        print(f"Bucket {name} is older than 1 months.")
        if not is_frequently_updated(name):
            print(f"Bucket {name} is not frequently updated. Deleting...")
            delete_bucket(name)
        else:
            print(f"Bucket {name} is frequently updated. Skipping deletion.")
    else:
        print(f"Bucket {name} is not older than 1 months. Skipping.")
