import boto3
import boto3.session

def get_credentials(aws_profile, region = "us-east-1", service = "ec2"):
    """
    Get the AWS credentials for local runs
    
    :param profile_name: The AWS CLI profile name to use.
    :param region: region to use.
    :param service: client service to connect to.
    :return: List of region names (e.g., ['us-east-1', 'us-west-2']).
    """
    aws_con = boto3.session.Session(profile_name = aws_profile, region_name = region)
    service_client = aws_con.client(service)

    return service_client
