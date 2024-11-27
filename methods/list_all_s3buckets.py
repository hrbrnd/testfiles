from aws_methods import get_credentials
from ec2_methods import get_all_regions
from s3_methods import get_s3_buckets
from file_methods import write_to_csv, generate_output_filename


def main():
    #set aws profile
    aws_profile = "hbm"
    base_output_filename = "D:\\HBM\\Documents\\Personal\\CertsLearning\\boto3-AWS-oreilly\\pythonProject\\Output\\list_all_s3buckets.csv"
    
    ec2_client = get_credentials(aws_profile)
    s3_client = get_credentials(aws_profile, service="s3")
    regions  = get_all_regions(ec2_client)

    #headers
    s3_headers = ["Region", "BucketName", "CreationDate", "Tags"]

    for region in regions:
        s3_buckets = get_s3_buckets(s3_client, region)
        if s3_buckets:
            output_file = generate_output_filename(base_output_filename)    
            write_to_csv(output_file, s3_headers, s3_buckets)



if __name__ == "__main__":
    main()