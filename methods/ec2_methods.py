from methods.aws_methods import *

def get_all_regions(aws_profile):
    """
    Get the list of all available AWS regions.
    
    :param profile_name: The AWS CLI profile name to use.
    :return: List of region names (e.g., ['us-east-1', 'us-west-2']).
    """
    ec2_client = get_credentials(aws_profile)
    region_response = ec2_client.describe_regions()
    regions = [region["RegionName"] for region in region_response["Regions"]]

    return regions

def get_instance_tags(aws_profile, regions):
    """
    Collect all unique tag keys across all EC2 instances in the provided regions.
    
    :param aws_con: The boto3 session object.
    :param regions: List of region names to query.
    :return: Sorted list of unique tag keys.
    """
    # Prepare to collect all unique tag keys across all instances
    tag_keys = set()

    # First pass to collect unique tag keys
    for region in regions:
        ec2_client = get_credentials(aws_profile, region)
        paginator = ec2_client.get_paginator("describe_instances")

        for page in paginator.paginate():
            for each_item in page["Reservations"]:
                for instance in each_item["Instances"]:
                    for each_tag in instance.get("Tags", []):
                        tag_keys.add(each_tag['Key'])
    tag_keys = sorted(tag_keys)
    return tag_keys

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

def calculate_total_ebs_size(ec2_client, instance_id):
    """
    Calculate the total sum of all EBS volumes attached to an EC2 instance.
    
    :param instance_id: The ID of the EC2 instance.
    :param region: The AWS region where the instance is located.
    :return: The total size of all attached EBS volumes in GiB.
    """

    # Get the list of volumes attached to the EC2 instance
    response = ec2_client.describe_instances(InstanceIds=[instance_id])

    # Initialize total size variable
    total_size = 0

    # Iterate over each instance to get the attached volumes
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            # Check for the 'BlockDeviceMappings' field (attached volumes)
            if 'BlockDeviceMappings' in instance:
                for block_device in instance['BlockDeviceMappings']:
                    # Get the volume ID from the block device mapping
                    volume_id = block_device['Ebs']['VolumeId']
                    
                    # Get the volume's size
                    volume_response = ec2_client.describe_volumes(VolumeIds=[volume_id])
                    for volume in volume_response['Volumes']:
                        total_size += volume['Size']  # Add the size of this volume

    return total_size

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
            DryRun=True,
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

