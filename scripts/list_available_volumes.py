from methods.ec2_methods import get_all_regions, get_ebs_snapshots, calculate_storage_costs, estimate_snapshot_cost, get_ebs_tags, get_ebs_details
from methods.file_methods import write_to_csv, generate_output_filename


def main():
    
    aws_profile = ""
    base_output_filename = ""
    
    #minimum costs, might vary slightly per region
    VOLUME_COST_PER_GB_PER_MONTH = 0.08  
     
    vol_filter = {'Name': 'status','Values': ['available']}

    regions = get_all_regions(aws_profile)

    tag_keys = get_ebs_tags(aws_profile, regions, vol_filter)

    header = ["Region", "Volume_ID", "Volume_Type", "Size", "Encrypted", "State", "Snapshot_Id", "CreateTime", "Snapshots", "Total_EBS_Size_GB", "Estimate_Snapshot_Cost", "Estimate_Volume_Cost"] + tag_keys

    volume_rows = get_ebs_details(aws_profile, regions, tag_keys)

    for row in volume_rows:
        region_id = row[0]
        volume_id = row[1]
        volume_size = row[3]

        # Fetch snapshots
        snapshots = get_ebs_snapshots(volume_id, aws_profile, region_id)
        
        snapshot_cost = ""
        if snapshots:
            snapshot_cost = estimate_snapshot_cost(volume_size)

        volume_cost = calculate_storage_costs(volume_size, VOLUME_COST_PER_GB_PER_MONTH)
        
        # Append snapshot and volume data to the row
        row.insert(8, snapshots)  
        row.insert(9, volume_size)
        row.insert(10, snapshot_cost)  
        row.insert(11, volume_cost)  

    # Generate the output filename for the CSV
    output_file = generate_output_filename(base_output_filename)

    # Write the header and instance rows to the CSV file
    write_to_csv(output_file, header, volume_rows)

    print(f"CSV file '{output_file}' created successfully.")


if __name__ == "__main__":
    main()