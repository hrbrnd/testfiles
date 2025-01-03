"""
.DATE_CREATED
2024-11-19

.DESCRIPTION
1. Get AWS credentials via boto3 (using a specific profile).
2. Retrieve a list of all AWS regions.
3. For each region:
   - List all EC2 instances.
   - Filter instances whose 'cost code' tag value is either:
      - Longer than 6 characters.
4. Extract only the numeric portion from the cost code.
5. Update the EC2 instance's tag with the new cost code value.
6. Output the instance ID and its new cost code tag for review.

This script is useful for standardizing EC2 cost code tags across regions.

.CHANGE_LOG
- [2024-11-19] Initial version created.
"""

import boto3
import boto3.session
import re

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

def get_invalid_ec2_costcodes(aws_profile, regions):

    # Compiles a list of instances that have a costcode longer than 6 characters

    instances_info = []

    for region in regions:
        ec2_client = get_credentials(aws_profile, region)
        paginator = ec2_client.get_paginator("describe_instances")

        for page in paginator.paginate():
            for reservation in page['Reservations']:
                for instance in reservation['Instances']:
                    tags = {tag['Key'].lower(): tag['Value'] for tag in instance.get('Tags', [])}                    
                    
                    costcode_value = tags.get("costcode", "")

                    if len(costcode_value) > 6:

                        instances_info.append({
                            "instanceId": instance['InstanceId'],
                            "region": region,
                            "invalid_costcode": costcode_value
                })
    return instances_info

def determine_costcode_values(invalid_costcode):

    #Extracts the numeric costcode from invalid tags
    
    costcode_pattern = r'\d{6}'
        
    match = re.search(costcode_pattern, invalid_costcode)

    if match:
        return match.group(0)
    else:
        return None

def assign_costcodes(ec2_client, instanceId, valid_costcode):

    #Updates the extracted costcode to each flagged instance

    if valid_costcode:
        ec2_client.create_tags(
            DryRun=False,
            Resources=[
                instanceId,
            ],
            Tags=[
                {
                    'Key': 'costcode',
                    'Value': valid_costcode
                },
            ]
        )

def main():
    #set aws profile
    aws_profile = "hbm"

    ec2_client = get_credentials(aws_profile) 
    regions  = get_all_regions(ec2_client)

    instances_info = get_invalid_ec2_costcodes(aws_profile, regions)
    print(instances_info)

    for instance in instances_info:
        valid_costcode = determine_costcode_values(instance["invalid_costcode"])
        print(valid_costcode)
        if valid_costcode:

            assign_costcodes(ec2_client, instance["instanceId"], valid_costcode)
            print("InstanceId {} costcode was modified to {} from {}".format(instance["instanceId"], valid_costcode, instance["invalid_costcode"]))
        else:
            print("Error not able to update. InstanceId {} in region {} cost code remains {} ".format(instance["instanceId"], instance["region"], instance["invalid_costcode"]))


if __name__ == "__main__":
    main()





