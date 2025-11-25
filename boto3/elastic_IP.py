import boto3
import csv

def get_elastic_ips():
    ec2_client = boto3.client('ec2', region_name='ap-south-1')
    response = ec2_client.describe_addresses()
    return response['Addresses']

def main():
    elastic_ips = get_elastic_ips()
    
    with open('elastic_ips_report.csv', mode='w', newline='') as file:
        fieldnames = ['Name', 'Elastic IP', 'Associated Instance ID']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for ip in elastic_ips:
            name = ip.get('Tags', [{'Key': 'Name', 'Value': ''}])[0]['Value']
            elastic_ip = ip['PublicIp']
            instance_id = ip.get('InstanceId', '')
            
            writer.writerow({'Name': name,
                             'Elastic IP': elastic_ip,
                             'Associated Instance ID': instance_id})
    
if __name__ == "__main__":
    main()
