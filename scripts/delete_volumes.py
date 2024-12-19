from methods.file_methods import import_csv_file
from methods.ec2_methods import create_snapshot
from methods.aws_methods import get_credentials


def main():
    
    aws_profile = ""
    file_path = ""
    tags = [{'Key': 'delete_after', 'Value': '2025-01-31'}]
    description = ""

    volume_rows = import_csv_file(file_path)

    for row in volume_rows:
        region = row[0]
        volume = row[1]
        vol_backups = create_snapshot(aws_profile, region, volume, description, tags)
        
        print("Region: {} Volume: {}  Snapshot_ID_Created: {}".format(vol_backups[0], vol_backups[1], vol_backups[2]))

        #Delete the volumes
        ec2_client = get_credentials(aws_profile, region)

        print(volume, "deleted test")

        # response  = ec2_client.delete_volume(
        #     VolumeId=volume,
        #     DryRun=False #Set to True for deletion
        # )
        
        # print(response)

if __name__ == "__main__":
    main()
