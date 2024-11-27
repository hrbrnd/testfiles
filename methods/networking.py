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
