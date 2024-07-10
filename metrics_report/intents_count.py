import os
import json

def count_orders_in_auction_files(directory):
    total_orders = 0
    auction_files_count = 0

    for filename in os.listdir(directory):
        if filename.startswith("auction") and filename.endswith(".json"):
            with open(os.path.join(directory, filename), 'r') as file:
                data = json.load(file)
                if "auction" in data and "orders" in data["auction"]:
                    total_orders += len(data["auction"]["orders"])
                    auction_files_count += 1

    if auction_files_count == 0:
        return 0

    average_orders = total_orders / auction_files_count
    return average_orders

# Directory containing the JSON files
directory_path = 'auction_data'

# Calculate and print the average number of orders
average_orders = count_orders_in_auction_files(directory_path)
print(f"Average number of orders in auction files: {average_orders}")
