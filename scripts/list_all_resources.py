from methods.aws_methods import get_credentials
from methods.ec2_methods import get_all_regions
from methods.s3_methods import get_s3_buckets
from methods.file_methods import write_to_csv, generate_output_filename
from methods.networking import get_vpcs, get_security_groups, get_load_balancers

def main():
    #set aws profile
    aws_profile = ""
    base_s3_file = ""
    base_vpc_file = ""
    base_sg_file = ""
    base_elb_file = ""

    #headers
    s3_headers = ["Region", "BucketName", "CreationDate", "Tags"]
    vpc_headers = ["Region", "VPCId", "CidrBlock", "IsDefault", "Tags"]
    sg_headers = ["Region", "GroupId", "GroupName", "Description", "Tags"]
    lb_headers = ["Region", "LoadBalancerName", "DNSName", "CreatedTime", "Type", "State", "Tags"]    

    regions  = get_all_regions(aws_profile)

    # for region in regions:
        
    # Get S3 Buckets
    s3_buckets = get_s3_buckets(aws_profile)

    # Get VPCs
    vpc_rows = get_vpcs(aws_profile, regions)

    # Get Security Groups
    sg_rows = get_security_groups(aws_profile, regions)

    # Get Load Balancers
    elb_rows = get_load_balancers(aws_profile, regions)
           
    if s3_buckets:
        output_file = generate_output_filename(base_s3_file)    
        write_to_csv(output_file, s3_headers, s3_buckets)

    if vpc_rows:
        output_file = generate_output_filename(base_vpc_file)
        write_to_csv(output_file, vpc_headers, vpc_rows)

    if sg_rows:
        output_file = generate_output_filename(base_sg_file)
        write_to_csv(output_file, sg_headers, sg_rows)

    if elb_rows:
        output_file = generate_output_filename(base_elb_file)
        write_to_csv(output_file, lb_headers, elb_rows)                 

if __name__ == "__main__":
    main()
