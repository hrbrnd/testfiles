"""
Script to fetch and process EC2 instances that have been stopped for more than 90 days across all AWS regions.
The script retrieves the instance details (including state, tags, and stop time) and writes them to a CSV file.

Created by: [Your Name]
Date Created: [Creation Date]
Last Modified: [Last Modified Date]
Version: 1.0.0

Synopsis:
    - Fetches EC2 instances that are in the "stopped" state across all regions.
    - Extracts the stop time from the state transition reason.
    - Filters instances that have been stopped for more than 90 days.
    - Collects relevant instance data and writes it to a CSV file.

Dependencies:
    - Boto3 (AWS SDK for Python)
    - Python 3.x (with standard library datetime, csv, etc.)
    - AWS credentials configured (using profile_name)

Change Log:
    - Version 1.0.0: Initial version. Fetches stopped EC2 instances and writes data to CSV.
    
License: [Insert License Information, e.g., MIT License, if applicable]
"""
