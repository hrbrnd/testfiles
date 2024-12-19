from methods.aws_methods import get_credentials

def get_vpcs(aws_profile, regions):
    """Get all VPCs in the specified region."""
    
    vpc_details = []

    for region in regions:
        ec2_client = get_credentials(aws_profile, region)
        paginator = ec2_client.get_paginator("describe_vpcs")
        for page in paginator.paginate():
            for vpc in page['Vpcs']:
                row = [
                    region,
                    vpc['VpcId'],
                    vpc.get('CidrBlock', 'N/A'),
                    vpc.get('IsDefault', 'N/A'),
                    vpc.get('Tags', [])
                ]
                vpc_details.append(row)
    return vpc_details

def get_route_tables(aws_profile, regions):
    """Get all VPCs in the specified region."""
    
    rt_tables_details = []

    for region in regions:
        ec2_client = get_credentials(aws_profile, region)
        paginator = ec2_client.get_paginator("describe_route_tables")
        for page in paginator.paginate():
            for tables in page['RouteTables']:
                main_route_table = "N/A"  # Default value
                subnets = []  # List to hold all associated subnets for the route table

                # Loop through Associations to check for Main route table and gather subnet info
                for association in tables.get('Associations', []):
                    if association.get("Main"):
                        main_route_table = "Yes"  # Mark as main route table
                    subnet = association.get("SubnetId")
                    if subnet:
                        subnets.append(subnet)  # Collect associated subnets

                # Process each route for the route table
                for routes in tables['Routes']:
                    destination = (
                        routes.get("DestinationCidrBlock") or
                        routes.get("DestinationIpv6CidrBlock") or
                        routes.get("DestinationPrefixListId") or
                        "N/A"
                    )

                    # Getting target with OR conditions
                    target = (
                        routes.get("EgressOnlyInternetGatewayId") or
                        routes.get("GatewayId") or
                        routes.get("InstanceId") or
                        routes.get("NatGatewayId") or
                        routes.get("TransitGatewayId") or
                        routes.get("LocalGatewayId") or
                        routes.get("CarrierGatewayId") or
                        routes.get("NetworkInterfaceId") or
                        routes.get("VpcPeeringConnectionId") or
                        routes.get("CoreNetworkArn") or
                        "N/A"
                    )

                    state = routes.get("State", "N/A")

                    # Add a new row for each route
                    row = [
                        region,
                        tables["VpcId"],
                        tables["RouteTableId"],
                        destination,
                        target,
                        state,
                        tables.get("OwnerId", "N/A"),  # AWS Account Owner
                        main_route_table,  # Whether it's the main route table for the VPC
                        ",".join(subnets) if subnets else "N/A"  # Associated Subnets (comma-separated)
                    ]
                    rt_tables_details.append(row)

    return rt_tables_details

def get_load_balancers(aws_profile, regions):
    """Get all load balancers (ALB and NLB) in the specified region."""
    elb_details = []

    for region in regions:
        elb_client = get_credentials(aws_profile, region, service="elbv2")
        paginator = elb_client.get_paginator("describe_load_balancers")
        for page in paginator.paginate():
            for lb in page['LoadBalancers']:
                row = [
                    region,
                    lb['LoadBalancerName'],
                    lb['DNSName'],
                    lb['CreatedTime'],
                    lb['Type'],
                    lb['State']['Code'],
                    lb.get('Tags', [])
                ]
                elb_details.append(row)
    return elb_details

def get_security_groups(aws_profile, regions):
    """Get all security groups in the specified region."""
    sg_details = []

    for region in regions:
        ec2_client = get_credentials(aws_profile, region)
        paginator = ec2_client.get_paginator("describe_security_groups")
        for page in paginator.paginate():
            for sg in page['SecurityGroups']:
                row = [
                    region,
                    sg['GroupId'],
                    sg['GroupName'],
                    sg['Description'],
                    sg.get('Tags', [])
                ]
            sg_details.append(row)
    return sg_details