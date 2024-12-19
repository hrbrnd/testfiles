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

def get_ebs_tags(aws_profile, regions, vol_filter):

    tag_keys = set()

    for region in regions:
        ec2_client = get_credentials(aws_profile, region)
        paginator = ec2_client.get_paginator("describe_volumes")

        for page in paginator.paginate(Filters=[vol_filter]):
            for vol in page["Volumes"]:
                for tags in vol.get("Tags", []):
                    tag_keys.add(tags["Key"])
    
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

def get_ebs_details(aws_profile, regions, tag_keys):
    """
    Retrieve details of all EBS volumes including tags, across multiple regions.
    
    :param aws_con: The boto3 session object.
    :param regions: List of region names to query.
    :param tag_keys: List of tag keys to extract from instances.
    :return: List of rows with ebs details and corresponding tag values.
    """    

    vol_filter = {'Name': 'status','Values': ['available']}

    ebs_details = []

    for region in regions:
        ec2_client = get_credentials(aws_profile, region)
        paginator = ec2_client.get_paginator("describe_volumes")

        for page in paginator.paginate(Filters=[vol_filter]):
            for vol in page["Volumes"]:
                row = [
                    region,
                    vol["VolumeId"],
                    vol["VolumeType"],
                    vol["Size"],                    
                    vol["Encrypted"],
                    vol["State"],
                    vol.get("SnapshotId", ""),
                    vol["CreateTime"].strftime('%Y-%m-%d %H:%M:%S')
                ]

                tags_dict = { tag['Key']: tag['Value'] for tag in vol.get("Tags", [])}

                row.extend(tags_dict.get(key, '') for key in tag_keys)               

                ebs_details.append(row)

    return ebs_details

def calculate_total_ebs_size(aws_profile, region_id, instance_id):
    """
    Calculate the total sum of all EBS volumes attached to an EC2 instance.
    
    :param instance_id: The ID of the EC2 instance.
    :param region: The AWS region where the instance is located.
    :return: The total size of all attached EBS volumes in GiB.
    """
    ec2_client = get_credentials(aws_profile, region_id)
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
    import re

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


def get_instance_details_from_file(aws_profile, tag_keys, file_path):
    instance_details = []

    # Read region and instance IDs from the text file
    with open(file_path, mode='r') as file:
        region_instance_pairs = [line.strip().split(',') for line in file]

    # Group instance IDs by region
    instances_by_region = {}
    for region, instance_id in region_instance_pairs:
        if region not in instances_by_region:
            instances_by_region[region] = []
        instances_by_region[region].append(instance_id)

    for region, instance_ids in instances_by_region.items():
        ec2_client = get_credentials(aws_profile, region)
        paginator = ec2_client.get_paginator("describe_instances")

        for page in paginator.paginate(InstanceIds=instance_ids):
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

def get_stopped_instances_grt_90days(aws_profile, regions, stopped_days = 90):
    from datetime import datetime, timedelta, timezone
    
    current_time = datetime.now(timezone.utc)
    stopped_filter = {'Name': 'instance-state-name', 'Values': ['stopped']}
    instance_details = []

    for region in regions:
        ec2_client = get_credentials(aws_profile, region)
        paginator = ec2_client.get_paginator("describe_instances")

        # Loop through all reservations and instances
        for page in paginator.paginate(Filters=[stopped_filter]):
            for reservation in page['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    state_transition_reason = instance.get('StateTransitionReason', '')
                try:
                    # The state transition reason will look like: "User initiated (yyyy-mm-dd hh:mm:ss GMT)"
                    # Extract the stop time from the reason string
                    if state_transition_reason:
                            stop_time_str = state_transition_reason.split('(')[-1].strip(')')  # Extract time inside parentheses
                            stop_time = datetime.strptime(stop_time_str, "%Y-%m-%d %H:%M:%S GMT")

                            # Make stop_time format the same UTC format as current time
                            stop_time = stop_time.replace(tzinfo=timezone.utc)

                            # Calculate how long the instance has been stopped
                            time_diff = current_time - stop_time
                            
                            # Make time_diff more readable for output
                            days = time_diff.days
                            hours, remainder = divmod(time_diff.seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            readable_time_diff = f"{days} days, {hours} hours, {minutes} minutes"

                            # Get Tags for instance
                            tags = {tag["Key"].lower(): tag["Value"] for tag in instance.get("Tags", [])}

                            if time_diff >= timedelta(days = stopped_days):  # 90 days in timedelta
                                row = [
                                    region,
                                    instance["InstanceId"],
                                    tags.get("name", ""),
                                    tags.get("nextgen.cost-center", ""),                                    
                                    instance["InstanceType"],
                                    instance["State"]["Name"],
                                    instance["LaunchTime"].strftime('%Y-%m-%d %H:%M:%S'),  # Formatting LaunchTime
                                    instance.get("PrivateIpAddress", ""),
                                    state_transition_reason, 
                                    current_time.strftime('%Y-%m-%d %H:%M:%S'),
                                    str(readable_time_diff),
                                    ""
                                ]

                                instance_details.append(row)
                                # print(f"Instance {instance_id} has been stopped for more than 90 days (Stopped on {stop_time_str})")                        
                except Exception as e:
                    # Error instances are outputted with error code
                    print(f"Error parsing stop time for instance {instance_id}")
                    row = [
                            region,
                            instance["InstanceId"],
                            tags.get("name", ""),
                            tags.get("nextgen.cost-center", ""),                            
                            instance["InstanceType"],
                            instance["State"]["Name"],
                            instance["LaunchTime"].strftime('%Y-%m-%d %H:%M:%S'),  # Formatting LaunchTime
                            instance.get("PrivateIpAddress", ""),
                            state_transition_reason, 
                            current_time.strftime('%Y-%m-%d %H:%M:%S'),
                            "",                      
                            e
                        ]
                                                                
                    instance_details.append(row)
    
    return instance_details

def get_ebs_snapshots(resource, aws_profile, region_id):
    """
    Retrieve all snapshots for a specified resource. This function can be extended in the future to support additional AWS resources.

    :param instance_id: The resource ID (Instance id, volume ID, ...) for which to find the snapshots.
    :param aws_profile: The AWS profile to use for credentials.
    :return: A tuple containing:
             - A list of snapshot IDs
    """
    # Create a session with the specified AWS profile
    ec2_client = get_credentials(aws_profile, region_id)

    # Initialize lists for snapshot IDs and snapshot sizes
    snapshot_ids = []

    if resource.startswith("i-"):
        instance_id = resource
        response = ec2_client.describe_instances(InstanceIds=[instance_id])

        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                # Check for the 'BlockDeviceMappings' field (attached volumes)
                if 'BlockDeviceMappings' in instance:
                    for block_device in instance['BlockDeviceMappings']:
                        # Get the volume ID from the block device mapping
                        volume_id = block_device['Ebs']['VolumeId']
                        
                        # Fetch snapshots for this volume
                        snapshots_response = ec2_client.describe_snapshots(Filters=[
                            {'Name': 'volume-id', 'Values': [volume_id]}
                        ])
                        
                        for snapshot in snapshots_response['Snapshots']:
                            snapshot_ids.append(snapshot['SnapshotId'])    
    elif resource.startswith("vol-"):
        volume_id = resource

        # Fetch snapshots for this volume
        snapshots_response = ec2_client.describe_snapshots(Filters=[
            {'Name': 'volume-id', 'Values': [volume_id]}
        ])
        
        for snapshot in snapshots_response['Snapshots']:
            snapshot_ids.append(snapshot['SnapshotId'])  
    
    return snapshot_ids


def calculate_storage_costs(size_in_gb, cost_per_gb_per_month):
    """
    Calculate the storage cost based on size and cost rate.

    :param size_in_gb: The size of the storage in GB.
    :param cost_per_gb_per_month: The cost per GB per month.
    :return: The total cost of the storage.
    """
    cost = size_in_gb * cost_per_gb_per_month

    return round(cost, 2)

def estimate_snapshot_cost(total_ebs_gb, utilization_percentage=.5, calculate_incremental = False, change_rate_per_day=0.03, days=30, backup_price_per_gb=0.05):
    """
    Estimate the cost of EBS snapshots considering full and incremental snapshots.
    
    :param total_ebs_gb: Total size of EBS volume in GB
    :param utilization_percentage: Fraction of the volume that is actively used (e.g., 0.5 for 50%)
    :param calculate_incremental: Dictates if incremental cost estimate will be done
    :param change_rate_per_day: Percentage of data that changes per day (e.g., 3% as 0.03)
    :param days: Number of days to consider for the estimate (typically 30 for monthly)
    :param backup_price_per_gb: Cost per GB per month for backup storage
    
    :return: Estimated cost for snapshots
    """
    # Calculate the used data (total * utilization percentage)
    used_data = total_ebs_gb * utilization_percentage
    
    # First snapshot cost (charged only for the used data)
    first_snapshot_cost = used_data * backup_price_per_gb
    
    # Incremental snapshot cost: we estimate the data that changes over the given period
    changed_data = used_data * change_rate_per_day * days
    
    incremental_snapshot_cost = 0
    if calculate_incremental:
        # Incremental snapshots store only the changed data, so we estimate the cost for that
        incremental_snapshot_cost = changed_data * backup_price_per_gb
    
    # Total estimated cost: full snapshot cost + incremental snapshot costs
    total_cost = first_snapshot_cost + incremental_snapshot_cost
    
    return round(total_cost, 2)

def create_snapshot(aws_profile, region, volume_id, description, tags):
    
    resources = [] 
    ec2_client = get_credentials(aws_profile, region)
    
    # Create the snapshot
    snapshot = ec2_client.create_snapshot(
        VolumeId=volume_id,
        Description=description
    )
    
    # Extract the snapshot ID
    snapshot_id = snapshot['SnapshotId']
    
    # Wait for the snapshot to be completed
    waiter = ec2_client.get_waiter('snapshot_completed')
    try:
        waiter.wait(SnapshotIds=[snapshot_id])
    except Exception as e:
        print(f"Snapshot creation failed in {region}: {e}")
        return None
    
    # Add tags to the snapshot
    ec2_client.create_tags(
        Resources=[snapshot_id],
        Tags=tags
    )
    
    resources.append(region)
    resources.append(volume_id)
    resources.append(snapshot_id)

    return resources