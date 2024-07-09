## Download an specific amount of auctions based on an initial block_id, and increments of 10
## Counts UIDs in multiple json files in orders

import os
import requests
import json
import csv
from collections import Counter

# Function to create directory if it does not exist
def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Function to download JSON data
def download_json_files(start_id, increment, max_files, base_url, output_folder):
    current_id = start_id
    successful_downloads = 0

    create_directory(output_folder)

    while successful_downloads < max_files:
        url = base_url.format(id=current_id)
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Save the JSON data to a file
            file_path = os.path.join(output_folder, f"auction_{current_id}.json")
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)

            print(f"Successfully downloaded JSON for ID {current_id}")
            successful_downloads += 1

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred for ID {current_id}: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred for ID {current_id}: {req_err}")
        except json.JSONDecodeError as json_err:
            print(f"JSON decode error occurred for ID {current_id}: {json_err}")

        # Increment the ID for the next request
        current_id += increment

# Function to extract UIDs from JSON data
def extract_uids_from_json(json_data):
    uids = []
    try:
        orders = json_data.get("auction", {}).get("orders", [])
        for order in orders:
            uids.append(order)
    except Exception as e:
        print(f"Error extracting UIDs: {e}")
    return uids

# Function to read JSON files and count UIDs
def count_uids_in_folder(folder_path, file_prefix):
    uid_counter = Counter()

    for filename in os.listdir(folder_path):
        if filename.startswith(file_prefix) and filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r') as file:
                    json_data = json.load(file)
                    uids = extract_uids_from_json(json_data)
                    uid_counter.update(uids)
            except Exception as e:
                print(f"Error reading file {filename}: {e}")

    return uid_counter

# Function to save UIDs count to CSV
def save_uids_to_csv(uid_counter, output_csv):
    sorted_uids = uid_counter.most_common()

    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = ['uid', 'count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for uid, count in sorted_uids:
            writer.writerow({'uid': uid, 'count': count})

# Generate 100 JSON auction data starting from initial ID and incrementing by 10

# Parameters
start_id = 9060612
increment = 10
max_files = 100
base_url = "https://api.cow.fi/mainnet/api/v1/solver_competition/{id}"
output_folder = "auction_data"

# Download JSON files
# download_json_files(start_id, increment, max_files, base_url, output_folder)

# Counts shared UIDs from auction JSON files in an specific folder then save it to a csv

# Parameters
folder_path = "auction_data"
file_prefix = "auction_"
output_csv = "uids_count.csv"

# Count UIDs and save to CSV
uid_counter = count_uids_in_folder(folder_path, file_prefix)
save_uids_to_csv(uid_counter, output_csv)