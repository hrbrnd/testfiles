from methods.aws_methods import get_credentials
def get_s3_buckets(aws_profile):
    """Get S3 buckets in a given region"""

    s3_client = get_credentials(aws_profile, service="s3")
    s3_data = []
    
    # List all buckets in the account
    buckets = s3_client.list_buckets()["Buckets"]
    
    for bucket in buckets:
        region = bucket.get("BucketRegion")
        bucket_name = bucket.get("Name", '')
        creation_date = bucket.get("CreationDate", '')

        
        # Get tags associated with each bucket
        try:
            tags = s3_client.get_bucket_tagging(Bucket=bucket_name)["TagSet"]
            tags_dict = {tag["Key"]: tag["Value"] for tag in tags}
            tags_str = ', '.join(f"{key}={value}" for key, value in tags_dict.items())
        except s3_client.exceptions.ClientError as e:
            tags_str = "No tags available"

        s3_data.append([region, bucket_name, creation_date, tags_str])
    
    return s3_data