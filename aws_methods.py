import boto3
import boto3.session

def get_credentials(aws_profile, region = "us-east-1"):
    aws_con = boto3.session.Session(profile_name = aws_profile, region_name = region)
    ec2_client = aws_con.client("ec2")

    return ec2_client


def get_all_regions(ec2_client):

    region_response = ec2_client.describe_regions()
    regions = [region["RegionName"] for region in region_response["Regions"]]

    return regions