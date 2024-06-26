import pandas as pd
from utils import get_token_info, get_eth_price_usd
import json

# Read JSON data from a text file
file_path = "JSON_data.txt"

with open(file_path, "r") as file:
    data = json.load(file)

# Read the additional JSON data for the auction_9051834
auction_file_path = "auction_9051834.json"

with open(auction_file_path, "r") as auction_file:
    auction_data = json.load(auction_file)

# Extract the orders and the fulfilled order ids
orders = data.get("orders", [])
block_id = data.get("id")
fulfilled_order_ids = {order.get("id") for solution in auction_data.get("solutions", []) for order in solution.get("orders", [])}

# Get the actual eth price
eth_price = get_eth_price_usd()

# Prepare the list to hold the extracted data
data_list = []

# Loop through each order and extract the required fields
for order in orders:
    uid = order.get("uid")
    token_bought = order.get("buyToken")
    token_sold = order.get("sellToken")

    token_bought_info = get_token_info(token_bought, block_id, eth_price)
    token_bought_symbol = token_bought_info['symbol']
    token_bought_price_usd = token_bought_info['price_usd']
    # time.sleep(0.35)  # Ensuring rate limit compliance

    token_sold_info = get_token_info(token_sold, block_id, eth_price)
    token_sold_symbol = token_sold_info['symbol']
    token_sold_price_usd = token_sold_info['price_usd']
    # time.sleep(0.35)  # Ensuring rate limit compliance

    token_bought_amount = int(order.get("buyAmount"))
    token_sold_amount = int(order.get("sellAmount"))

    # Adjust token amounts based on the token symbol
    if token_bought_symbol and any(substring in token_bought_symbol for substring in ['USDC', 'USDT']):
        token_bought_amount *= 1e-6
        token_bought_price_usd *= 1e-30
    else:
        token_bought_amount *= 1e-18
        token_bought_price_usd *= 1e-18

    if token_sold_symbol and any(substring in token_sold_symbol for substring in ['USDC', 'USDT']):
        token_sold_amount *= 1e-6
        token_sold_price_usd *= 1e-30
    else:
        token_sold_amount *= 1e-18
        token_sold_price_usd *= 1e-18

    # Calculate amount_usd
    if token_sold_amount is not None and token_sold_price_usd is not None:
        amount_usd = token_sold_amount * token_sold_price_usd
    else:
        amount_usd = None

    # Determine if the order is fulfilled
    fulfill = 1 if uid in fulfilled_order_ids else 0

    data_list.append({
        "uid": uid,
        "amount_usd": amount_usd,
        "token_bought_symbol": token_bought_symbol,
        "token_sold_symbol": token_sold_symbol,
        "token_bought_amount": token_bought_amount,
        "token_sold_amount": token_sold_amount,
        "token_bought_price_usd": token_bought_price_usd,
        "token_sold_price_usd": token_sold_price_usd,
        "fulfill": fulfill
    })

# Convert the list of dictionaries to a pandas DataFrame
df = pd.DataFrame(data_list)

# Save the DataFrame to a CSV file
csv_filename = f"dataframe_{block_id}.csv"
df.to_csv(csv_filename, index=False)

print(f"Data successfully saved to {csv_filename}")
