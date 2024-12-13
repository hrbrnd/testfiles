from methods.ec2_methods import get_all_regions, get_stopped_instances_grt_90days, get_ebs_snapshots_for_instance, calculate_storage_costs, calculate_total_ebs_size
from methods.file_methods import write_to_csv, generate_output_filename


from datetime import datetime, timedelta, timezone

#minimum costs, might vary slightly per region
SNAPSHOT_COST_PER_GB_PER_MONTH = 0.05  
VOLUME_COST_PER_GB_PER_MONTH = 0.08  

def main():
    aws_profile = ""
    base_output_filename = ""
    
    header = [
        "Region", "InstanceId", "Name", "CostCenter", "InstanceType", "Instance_State", 
        "LaunchTime", "PrivateIpAddress", "State_Transition", "Report_RunTime", "Time_Since_Last_Started", 
        "Error", "Snapshots", "Total_EBS_Size", "Total_Snapshot_Sizes", "Snapshot_Cost", "Volume_Cost"
    ]
    
    regions = get_all_regions(aws_profile)

    # Get stopped instances that have been stopped for more than 90 days
    instance_rows = get_stopped_instances_grt_90days(aws_profile, regions, days = 90)
    
    # Loop through the instance rows to calculate snapshot and volume costs
    for row in instance_rows:
        instance_id = row[1]
        region_id = row[0]

        # Fetch snapshots and snapshot sizes
        snapshots, snapshot_sizes = get_ebs_snapshots_for_instance(instance_id, aws_profile, region_id)
        
        # Calculate snapshot cost (using generalized method)
        snapshot_cost = calculate_storage_costs(sum(snapshot_sizes), SNAPSHOT_COST_PER_GB_PER_MONTH)
        
        # Calculate the total EBS volume size (you can use the existing calculate_total_ebs_size method)
        total_ebs_size = calculate_total_ebs_size(aws_profile, region_id, instance_id)  
        volume_cost = calculate_storage_costs(total_ebs_size, VOLUME_COST_PER_GB_PER_MONTH)
        
        # Append snapshot and volume data to the row
        row.append(snapshots)  # Add the snapshots
        row.append(total_ebs_size)
        row.append(snapshot_sizes)  # Add snapshot sizes
        row.append(snapshot_cost)  # Add snapshot cost
        row.append(volume_cost)  # Add volume cost (EBS size cost)

    # Generate the output filename for the CSV
    output_file = generate_output_filename(base_output_filename)

    # Write the header and instance rows to the CSV file
    write_to_csv(output_file, header, instance_rows)

    print(f"CSV file '{output_file}' created successfully.")


if __name__ == "__main__":
    main()