import boto3

# Initialize the boto3 IAM client
iam = boto3.client('iam')

# Function to list all IAM users with pagination
def list_users():
    users = []
    response = iam.list_users()
    users.extend(response['Users'])
    
    while 'Marker' in response:
        response = iam.list_users(Marker=response['Marker'])
        users.extend(response['Users'])
    
    return users

# Function to list access keys for a user with pagination
def list_access_keys(username):
    access_keys = []
    response = iam.list_access_keys(UserName=username)
    access_keys.extend(response['AccessKeyMetadata'])
    
    while 'Marker' in response:
        response = iam.list_access_keys(UserName=username, Marker=response['Marker'])
        access_keys.extend(response['AccessKeyMetadata'])
    
    return access_keys

# Function to delete an access key for a user
def delete_access_key(username, access_key_id):
    iam.delete_access_key(UserName=username, AccessKeyId=access_key_id)
    print(f"Deleted access key {access_key_id} for user {username}")

# Main execution
if __name__ == "__main__":
    # Define your username to exclude it from key deletion
    your_username = 'kandikuppa.krishna@herovired.com'  # Replace with your actual IAM username

    users = list_users()

    for user in users:
        username = user['UserName']
        
        # Skip deleting access keys for your own account
        if username == your_username:
            print(f"Skipping access key deletion for {username}")
            continue
        
        access_keys = list_access_keys(username)
        
        for access_key in access_keys:
            access_key_id = access_key['AccessKeyId']
            delete_access_key(username, access_key_id)

    print("Access keys for all users (except yours) have been deleted.")
