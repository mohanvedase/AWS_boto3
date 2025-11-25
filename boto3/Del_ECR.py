import boto3
from datetime import datetime, timezone, timedelta

# ECR client for Oregon region
ecr_client = boto3.client('ecr', region_name='ap-south-1')

# Get today's date
now = datetime.now(timezone.utc)

# Define age threshold (1 month = ~30 days)
age_limit = now - timedelta(days=60)

def delete_old_repositories():
    try:
        # Get all repositories
        response = ecr_client.describe_repositories()
        repos = response.get("repositories", [])

        for repo in repos:
            repo_name = repo["repositoryName"]
            created_at = repo["createdAt"]

            if created_at < age_limit:
                print(f"[INFO] Deleting repository: {repo_name}, CreatedAt: {created_at}")

                try:
                    ecr_client.delete_repository(
                        repositoryName=repo_name,
                        force=True  # deletes repo even if images exist
                    )
                    print(f"[SUCCESS] Deleted repository: {repo_name}")
                except Exception as e:
                    print(f"[ERROR] Could not delete {repo_name}: {e}")
            else:
                print(f"[SKIP] Repository {repo_name} is not older than 2 months.")

    except Exception as e:
        print(f"[ERROR] Failed to fetch repositories: {e}")


if __name__ == "__main__":
    delete_old_repositories()
