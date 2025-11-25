import boto3

s3 = boto3.client('s3')
s3_resource = boto3.resource('s3')

buckets = s3.list_buckets()['Buckets']

for bucket in buckets:
    bucket_name = bucket['Name']
    objects = list(s3_resource.Bucket(bucket_name).objects.all())
    if not objects:
        print(f"Deleting empty bucket: {bucket_name}")
        s3.delete_bucket(Bucket=bucket_name)
