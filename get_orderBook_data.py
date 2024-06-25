import pandas as pd
from utils import get_token_info
import json

# Read JSON data from a text file
file_path = "JSON_data.txt"

with open(file_path, "r") as file:
    data = json.load(file)

# Extract the orders
orders = data.get("orders", [])
block_id = data.get("id")
# Prepare the list to hold the extracted data
data_list = []

# Loop through each order and extract the required fields
for order in orders:
    tx_from = order.get("uid")
    token_bought = order.get("buyToken")
    token_sold = order.get("sellToken")

    token_bought_info = get_token_info(token_bought)
    token_bought_symbol = token_bought_info['symbol']
    token_bought_price_usd = token_bought_info['price_usd']
    # time.sleep(0.35)  # Ensuring rate limit compliance

    token_sold_info = get_token_info(token_sold)
    token_sold_symbol = token_sold_info['symbol']
    token_sold_price_usd = token_sold_info['price_usd']
    # time.sleep(0.35)  # Ensuring rate limit compliance

    token_bought_amount = int(order.get("buyAmount"))
    token_sold_amount = int(order.get("sellAmount"))

    # Adjust token amounts based on the token symbol
    if token_bought_symbol in ['USDC', 'USDT']:
        token_bought_amount *= 1e-6
    else:
        token_bought_amount *= 1e-18

    if token_sold_symbol in ['USDC', 'USDT']:
        token_sold_amount *= 1e-6
    else:
        token_sold_amount *= 1e-18

    # Calculate amount_usd
    if token_sold_amount is not None and token_sold_price_usd is not None:
        amount_usd = int(token_sold_amount) * token_sold_price_usd
    else:
        amount_usd = None
    
    data_list.append({
        "tx_from": tx_from,
        "amount_usd": amount_usd,
        "token_bought_symbol": token_bought_symbol,
        "token_sold_symbol": token_sold_symbol,
        "token_bought_amount": token_bought_amount,
        "token_sold_amount": token_sold_amount,
        "token_bought_price_usd": token_bought_price_usd,
        "token_sold_price_usd": token_sold_price_usd,
    })

# Convert the list of dictionaries to a pandas DataFrame
df = pd.DataFrame(data_list)

# Save the DataFrame to a CSV file
csv_filename = f"dataframe_{block_id}.csv"
df.to_csv(csv_filename, index=False)

print(f"Data successfully saved to {csv_filename}")
