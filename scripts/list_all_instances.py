"""
Date Created


.DESCRIPTION


.CHANGE_LOG

"""

from methods.aws_methods import get_credentials, get_all_regions, get_instance_tags, get_instance_details
from methods.file_methods import write_to_csv, generate_output_filename

def main():
    #set aws profile
    aws_profile = ""
    base_output_filename = ""

    ec2_client = get_credentials(aws_profile)
    regions  = get_all_regions(ec2_client)

    tag_keys = get_instance_tags(aws_profile, regions)

    header = [
        "Region", "InstanceId", "InstanceType", "Instance_State", "LaunchTime", "ImageId", "VpcId",
        "SubnetId", "PrivateIpAddress", "PublicIpAddress", "Total_EBS_Size_GiB"
    ] + tag_keys
    
    instance_rows = get_instance_details(aws_profile, regions, tag_keys)

    output_file = generate_output_filename(base_output_filename)

    write_to_csv(output_file, header, instance_rows)

    print(f"CSV file '{output_file}' created successfully.")


if __name__ == "__main__":
    main()
