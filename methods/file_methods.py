from datetime import datetime
import csv

def write_to_csv(file_path, header, rows):
    """
    Write the instance details and tags to a CSV file.
    
    :param file_path: Path where the CSV file will be saved.
    :param header: The header row to write in the CSV file.
    :param rows: The rows of data to write in the CSV file.
    """
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)  # Write the header row
        writer.writerows(rows)  # Write the data rows

def generate_output_filename(base_filename):
    """
    Generate a file name with the current date appended.
    
    :param base_filename: The base file name (without date).
    :return: The full file name with the current date appended (e.g., "instance_tags_with_details_2024-11-19.csv").
    """
    current_date = datetime.now().strftime('%Y-%m-%d')
    return f"{base_filename}_{current_date}.csv"  
