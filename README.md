"""
Script to fetch and process EC2 instances that have been stopped for more than 90 days across all AWS regions.
The script retrieves the instance details (including state, tags, and stop time) and writes them to a CSV file.

Created by: [Your Name]
Date Created: [Creation Date]
Last Modified: [Last Modified Date]
Version: 1.0.0

.SYNOPSIS
    Fetches EC2 instances that are in the "stopped" state across all regions.
    Extracts the stop time from the state transition reason and filters instances
    that have been stopped for more than 90 days. Outputs data to CSV.

.DESCRIPTION
    This script connects to all AWS regions, retrieves EC2 instances that are stopped,
    and calculates how long they have been stopped. If the instance has been stopped
    for more than 90 days, it collects relevant information (tags, IP address, stop time, etc.)
    and writes it to a CSV file for reporting and auditing purposes.

.DEPENDENCIES
    - Boto3 (AWS SDK for Python)
    - Python 3.x
    - AWS credentials configured (via AWS CLI profile)

.CHANGELOG
    Version 1.0.0: Initial version. Fetches stopped EC2 instances and writes data to CSV.

.LICENSE
    MIT License (or other license)
"""
