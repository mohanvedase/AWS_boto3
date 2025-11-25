import boto3
from datetime import datetime, timezone, timedelta

# Define regions
PRIVATE_REGION = "us-west-2"   # Oregon
PUBLIC_REGION = "us-west-2"    # Public ECR always lives here

# Clients for both private and public ECR
ecr_client = boto3.client('ecr', region_name=PRIVATE_REGION)        
ecr_public_client = boto3.client('ecr-public', region_name=PUBLIC_REGION)  

# Time threshold (2 months ≈ 60 days)
now = datetime.now(timezone.utc)
age_limit = now - timedelta(days=60)


def delete_old_private_repos():
    print(f"\n[Checking Private ECR Repositories in {PRIVATE_REGION}]")
    paginator = ecr_client.get_paginator('describe_repositories')

    for page in paginator.paginate():
        for repo in page["repositories"]:
            repo_name = repo["repositoryName"]
            created_at = repo["createdAt"]

            if created_at < age_limit:
                print(f"[INFO] Deleting PRIVATE repo: {repo_name} "
                      f"(Created: {created_at}, Region: {PRIVATE_REGION})")
                try:
                    ecr_client.delete_repository(repositoryName=repo_name, force=True)
                    print(f"[SUCCESS] Deleted private repo: {repo_name} (Region: {PRIVATE_REGION})")
                except Exception as e:
                    print(f"[ERROR] Could not delete {repo_name} in {PRIVATE_REGION}: {e}")
            else:
                print(f"[SKIP] Private repo {repo_name} in {PRIVATE_REGION} is not older than 2 months.")


def delete_old_public_repos():
    print(f"\n[Checking Public ECR Repositories in {PUBLIC_REGION}]")
    paginator = ecr_public_client.get_paginator('describe_repositories')

    for page in paginator.paginate():
        for repo in page["repositories"]:
            repo_name = repo["repositoryName"]
            created_at = repo["createdAt"]

            if created_at < age_limit:
                print(f"[INFO] Deleting PUBLIC repo: {repo_name} "
                      f"(Created: {created_at}, Region: {PUBLIC_REGION})")
                try:
                    ecr_public_client.delete_repository(repositoryName=repo_name, force=True)
                    print(f"[SUCCESS] Deleted public repo: {repo_name} (Region: {PUBLIC_REGION})")
                except Exception as e:
                    print(f"[ERROR] Could not delete {repo_name} in {PUBLIC_REGION}: {e}")
            else:
                print(f"[SKIP] Public repo {repo_name} in {PUBLIC_REGION} is not older than 2 months.")


if __name__ == "__main__":
    delete_old_private_repos()
    delete_old_public_repos()
