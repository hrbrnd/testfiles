"""
.DATE_CREATED
2024-11-19

.DESCRIPTION
This script serves as an automated tool for gathering EC2 instance details across multiple AWS regions, 
including instance-specific tags and the total size of EBS volumes attached to each instance. It uses 
AWS Boto3 SDK to interact with AWS EC2 resources, collects relevant metadata, and generates a CSV report 
containing this information for further analysis or auditing.

The script performs the following steps:
1. Uses a specified AWS profile to authenticate and access resources.
2. Retrieves a list of all AWS regions available for the EC2 service.
3. Iterates through each region to gather EC2 instance information, including:
   - Instance details (e.g., Instance ID, Type, State, Launch Time, etc.)
   - The total size of all attached EBS volumes for each instance
   - Instance tags (including custom tag keys)
4. Compiles this data into a structured format and exports it to a CSV file with a dynamically generated filename that includes the current date.
5. The final CSV report includes instance details along with associated tags and the total EBS volume size for each EC2 instance.

The generated report can be used for tracking resource usage, auditing, or managing AWS EC2 instances.

.CHANGE_LOG
- [2024-11-19] Initial version created.

"""

import boto3
import boto3.session
from datetime import datetime
import csv

def get_credentials(aws_profile, region = "us-east-1", service = "ec2"):
    """
    Get the AWS credentials for local runs
    
    :param profile_name: The AWS CLI profile name to use.
    :param region: region to use.
    :param service: client service to connect to.
    :return: List of region names (e.g., ['us-east-1', 'us-west-2']).
    """
    aws_con = boto3.session.Session(profile_name = aws_profile, region_name = region)
    ec2_client = aws_con.client(service)

    return ec2_client

def get_all_regions(ec2_client):
    """
    Get the list of all available AWS regions.
    
    :param profile_name: The AWS CLI profile name to use.
    :return: List of region names (e.g., ['us-east-1', 'us-west-2']).
    """
    region_response = ec2_client.describe_regions()
    regions = [region["RegionName"] for region in region_response["Regions"]]

    return regions

def get_instance_details(aws_profile, regions, tag_keys):
    """
    Retrieve details of all EC2 instances including tags, across multiple regions.
    
    :param aws_con: The boto3 session object.
    :param regions: List of region names to query.
    :param tag_keys: List of tag keys to extract from instances.
    :return: List of rows with instance details and corresponding tag values.
    """    
    instance_details = []

    for region in regions:
        ec2_client = get_credentials(aws_profile, region)
        paginator = ec2_client.get_paginator("describe_instances")

        for page in paginator.paginate():
            for reservation in page['Reservations']:
                for instance in reservation['Instances']:

                   # Start with the basic instance details
                    row = [
                        region,
                        instance["InstanceId"],
                        instance["InstanceType"],
                        instance["State"]["Name"],
                        instance["LaunchTime"].strftime('%Y-%m-%d %H:%M:%S'),  # Formatting LaunchTime
                        instance.get("ImageId", ""),
                        instance.get("VpcId", ""),
                        instance.get("SubnetId", ""),
                        instance.get("PrivateIpAddress", ""),
                        instance.get("PublicIpAddress", "")
                    ]

                    # Step to calculate the total size of all EBS volumes attached to this instance
                    total_ebs_size = calculate_total_ebs_size(ec2_client, instance["InstanceId"])
                    row.append(total_ebs_size)

                    # Create a dictionary of tags for easy lookup
                    tags_dict = {tag['Key']: tag['Value'] for tag in instance.get("Tags", [])}

                    # Add tag values to the row; if tag doesn't exist, leave it empty
                    row.extend(tags_dict.get(key, '') for key in tag_keys)                    

                    instance_details.append(row)

    return instance_details

def generate_output_filename(base_filename):
    """
    Generate a file name with the current date appended.
    
    :param base_filename: The base file name (without date).
    :return: The full file name with the current date appended (e.g., "instance_tags_with_details_2024-11-19.csv").
    """
    current_date = datetime.now().strftime('%Y-%m-%d')
    return f"{base_filename}_{current_date}.csv"  

def write_to_csv(file_path, header, rows):
    """
    Write the instance details and tags to a CSV file.
    
    :param file_path: Path where the CSV file will be saved.
    :param header: The header row to write in the CSV file.
    :param rows: The rows of data to write in the CSV file.
    """
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)  # Write the header row
        writer.writerows(rows)  # Write the data rows

def main():
    #set aws profile
    aws_profile = ""
    base_output_filename = ""

    ec2_client = get_credentials(aws_profile)
    regions  = get_all_regions(ec2_client)

    tag_keys = get_instance_tags(aws_profile, regions)

    header = [
        "Region", "InstanceId", "InstanceType", "Instance_State", "LaunchTime", "ImageId", "VpcId",
        "SubnetId", "PrivateIpAddress", "PublicIpAddress", "Total_EBS_Size_GiB"
    ] + tag_keys
    
    instance_rows = get_instance_details(aws_profile, regions, tag_keys)

    output_file = generate_output_filename(base_output_filename)

    write_to_csv(output_file, header, instance_rows)

    print(f"CSV file '{output_file}' created successfully.")


if __name__ == "__main__":
    main()
