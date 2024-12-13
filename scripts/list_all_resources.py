from methods.aws_methods import get_credentials
from methods.ec2_methods import get_all_regions
from methods.s3_methods import get_s3_buckets
from methods.file_methods import write_to_csv, generate_output_filename
from methods.networking_methods import get_vpcs, get_security_groups, get_load_balancers, get_route_tables
from methods.serverless_methods import get_lambda

def main():
    #set aws profile
    aws_profile = "hbm"
    base_s3_file = "D:\\HBM\\Documents\\Personal\\CertsLearning\\boto3-AWS-oreilly\\pythonProject\\Output\\list_all_s3buckets"
    base_vpc_file = "D:\\HBM\\Documents\\Personal\\CertsLearning\\boto3-AWS-oreilly\\pythonProject\\Output\\list_all_vpcs"
    base_sg_file = "D:\\HBM\\Documents\\Personal\\CertsLearning\\boto3-AWS-oreilly\\pythonProject\\Output\\list_all_sgs"
    base_elb_file = "D:\\HBM\\Documents\\Personal\\CertsLearning\\boto3-AWS-oreilly\\pythonProject\\Output\\list_all_elbs"
    base_rt_tables_file = "D:\\HBM\\Documents\\Personal\\CertsLearning\\boto3-AWS-oreilly\\pythonProject\\Output\\list_all_route_tables"

    #headers
    s3_headers = ["Region", "BucketName", "CreationDate", "Tags"]
    vpc_headers = ["Region", "VPCId", "CidrBlock", "IsDefault", "Tags"]
    sg_headers = ["Region", "GroupId", "GroupName", "Description", "Tags"]
    lb_headers = ["Region", "LoadBalancerName", "DNSName", "CreatedTime", "Type", "State", "Tags"]  
    rt_headers = ["Region", "VpcId", "RouteTableId", "destination", "target", "State", "RTable_Owner", "Main", "Linked_Subnets"]   

    regions  = get_all_regions(aws_profile)

    # # for region in regions:
        
    # # Get S3 Buckets
    # s3_buckets = get_s3_buckets(aws_profile)

    # # Get VPCs
    # vpc_rows = get_vpcs(aws_profile, regions)

    # # Get Security Groups
    # sg_rows = get_security_groups(aws_profile, regions)

    # # Get Load Balancers
    # elb_rows = get_load_balancers(aws_profile, regions)

    # Get Load Balancers
    rt_tables_rows = get_route_tables(aws_profile, regions)    

    #Get Lambda
    # lambda_rows = get_lambda(aws_profile, regions)
           
    # if s3_buckets:
    #     output_file = generate_output_filename(base_s3_file)    
    #     write_to_csv(output_file, s3_headers, s3_buckets)

    # if vpc_rows:
    #     output_file = generate_output_filename(base_vpc_file)
    #     write_to_csv(output_file, vpc_headers, vpc_rows)

    # if sg_rows:
    #     output_file = generate_output_filename(base_sg_file)
    #     write_to_csv(output_file, sg_headers, sg_rows)

    # if elb_rows:
    #     output_file = generate_output_filename(base_elb_file)
    #     write_to_csv(output_file, lb_headers, elb_rows)                 

    if rt_tables_rows:
        output_file = generate_output_filename(base_rt_tables_file)
        write_to_csv(output_file, rt_headers, rt_tables_rows)   

if __name__ == "__main__":
    main()