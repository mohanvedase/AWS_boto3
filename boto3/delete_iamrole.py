import boto3
from datetime import datetime, timezone, timedelta

# ---------------------------
# 🕒 Time setup
# ---------------------------
now = datetime.now(timezone.utc)
two_months_ago = now - timedelta(days=60)
twenty_days_ago = now - timedelta(days=20)

# ---------------------------
# ⚙️ IAM client
# ---------------------------
iam_client = boto3.client('iam')

# ---------------------------
# 🧪 Safety flag (set to False to actually delete)
# ---------------------------
DRY_RUN = True  # Change to False after reviewing output


def cleanup_and_delete_role(role_name, iam_client):
    """Detach policies, remove from profiles, and delete a user-created IAM role."""
    try:
        # Detach managed policies
        attached_policies = iam_client.list_attached_role_policies(RoleName=role_name)
        for policy in attached_policies['AttachedPolicies']:
            print(f"Detaching policy {policy['PolicyName']} from role {role_name}")
            iam_client.detach_role_policy(
                RoleName=role_name,
                PolicyArn=policy['PolicyArn']
            )

        # Delete inline policies
        inline_policies = iam_client.list_role_policies(RoleName=role_name)
        for policy_name in inline_policies['PolicyNames']:
            print(f"Deleting inline policy {policy_name} from role {role_name}")
            iam_client.delete_role_policy(
                RoleName=role_name,
                PolicyName=policy_name
            )

        # Remove role from instance profiles
        profiles = iam_client.list_instance_profiles_for_role(RoleName=role_name)
        for profile in profiles['InstanceProfiles']:
            profile_name = profile['InstanceProfileName']
            print(f"Removing role {role_name} from instance profile {profile_name}")
            iam_client.remove_role_from_instance_profile(
                InstanceProfileName=profile_name,
                RoleName=role_name
            )

        # Delete the role
        print(f"Deleting role: {role_name}")
        iam_client.delete_role(RoleName=role_name)

    except Exception as e:
        print(f"❌ Error cleaning up role {role_name}: {str(e)}")


# ---------------------------
# 🚀 Process all roles
# ---------------------------
if __name__ == '__main__':
    paginator = iam_client.get_paginator('list_roles')
    for page in paginator.paginate():
        for role in page['Roles']:
            role_name = role['RoleName']
            role_path = role['Path']
            create_date = role['CreateDate']

            # Skip AWS-managed roles and service-linked roles
            if role_path.startswith("/aws-service-role/") or role_name.startswith("AWSServiceRoleFor"):
                print(f"⏩ Skipping AWS-managed role: {role_name}")
                continue

            # Skip roles created within the last 2 months
            if create_date > two_months_ago:
                print(f"⏩ Skipping {role_name} — created within the last 2 months.")
                continue

            print(f"\n🔍 Checking role: {role_name} (Created: {create_date})")

            try:
                role_info = iam_client.get_role(RoleName=role_name)
                last_used = role_info['Role'].get('RoleLastUsed', {}).get('LastUsedDate')

                # Skip recently used roles
                if last_used and last_used > twenty_days_ago:
                    print(f"🕒 Skipping role {role_name} — used in last 20 days.")
                    continue

                # Eligible for deletion
                if DRY_RUN:
                    print(f"[DRY RUN] Would delete role: {role_name}")
                else:
                    cleanup_and_delete_role(role_name, iam_client)

            except Exception as e:
                print(f"⚠️ Error processing role {role_name}: {str(e)}")

    print("\n✅ Script execution completed.")
    if DRY_RUN:
        print("💡 DRY_RUN mode is ON — no roles were actually deleted.")
    else:
        print("🧹 Roles eligible for deletion have been cleaned up.")
