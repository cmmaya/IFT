import pandas as pd
from utils import get_token_symbol, get_token_price_usd
import json
import time

# Read JSON data from a text file
file_path = "JSON_data.txt"

with open(file_path, "r") as file:
    data = json.load(file)

# Extract the orders
orders = data.get("orders", [])

# Prepare the list to hold the extracted data
data_list = []

# Loop through each order and extract the required fields
for order in orders:
    tx_from = order.get("uid")
    token_bought = order.get("buyToken")
    token_sold = order.get("sellToken")
    
    try:
        token_bought_symbol = get_token_symbol(token_bought)
        time.sleep(0.35)  # Ensuring rate limit compliance
    except Exception as e:
        token_bought_symbol = token_bought  # Fallback to hash if symbol retrieval fails
        print(f"Error retrieving symbol for token bought {token_bought}: {e}")
    
    try:
        token_sold_symbol = get_token_symbol(token_sold)
        time.sleep(0.35)  # Ensuring rate limit compliance
    except Exception as e:
        token_sold_symbol = token_sold  # Fallback to hash if symbol retrieval fails
        print(f"Error retrieving symbol for token sold {token_sold}: {e}")

    token_bought_amount = order.get("buyAmount")
    token_sold_amount = order.get("sellAmount")
    
    try:
        token_bought_price_usd = get_token_price_usd(token_bought)
        time.sleep(0.35)  # Ensuring rate limit compliance
    except Exception as e:
        token_bought_price_usd = None  # Set to None if price retrieval fails
        print(f"Error retrieving price for token bought {token_bought}: {e}")
    
    try:
        token_sold_price_usd = get_token_price_usd(token_sold)
        time.sleep(0.35)  # Ensuring rate limit compliance
    except Exception as e:
        token_sold_price_usd = None  # Set to None if price retrieval fails
        print(f"Error retrieving price for token sold {token_sold}: {e}")
    
    # Placeholder for amount_usd, assuming we need to convert from token amounts
    amount_usd = None  # Since no conversion is provided, setting it to None or any default value
    
    data_list.append({
        "tx_from": tx_from,
        "amount_usd": amount_usd,
        "token_bought_symbol": token_bought_symbol,
        "token_sold_symbol": token_sold_symbol,
        "token_bought_amount": token_bought_amount,
        "token_sold_amount": token_sold_amount,
        "token_bought_price_usd": token_bought_price_usd,
        "token_sold_price_usd": token_sold_price_usd
    })

# Convert the list of dictionaries to a pandas DataFrame
df = pd.DataFrame(data_list)

# Save the DataFrame to a CSV file
csv_filename = "orders.csv"
df.to_csv(csv_filename, index=False)

print(f"Data successfully saved to {csv_filename}")
