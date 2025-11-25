import boto3
import csv

def get_load_balancers():
    elb_client = boto3.client('elbv2', region_name='ap-south-1')
    response = elb_client.describe_load_balancers(PageSize=400)  # Maximum allowed page size
    return response['LoadBalancers']

def main():
    load_balancers = get_load_balancers()
    
    with open('elb_report.csv', mode='w', newline='') as file:
        fieldnames = ['Load Balancer Name', 'Load Balancer Status', 'Load Balancer Type', 'Creation Time']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for lb in load_balancers:
            lb_name = lb['LoadBalancerName']
            lb_status = lb['State']['Code']
            lb_type = lb['Type']
            lb_creation_time = lb['CreatedTime'].strftime("%Y-%m-%d %H:%M:%S")
            
            writer.writerow({'Load Balancer Name': lb_name,
                             'Load Balancer Status': lb_status,
                             'Load Balancer Type': lb_type,
                             'Creation Time': lb_creation_time})
            print(f"Name: {lb_name}, Status: {lb_status}, Type: {lb_type}, Creation Time: {lb_creation_time}")
    
if __name__ == "__main__":
    main()
