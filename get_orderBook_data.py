import pandas as pd
from utils import get_token_info, get_eth_price_usd
import json
import os
import re
import pickle
import warnings

def getOrderBookData(block_id):

    # Read JSON data from a text file
    file_path = os.path.join("auction_data", f"data_id_{block_id}.json")

    with open(file_path, "r") as file:
        data = json.load(file)

    # Read the additional JSON data for the auction_9051834
    auction_file_path = os.path.join("auction_data", f"auction_{block_id}.json")

    with open(auction_file_path, "r") as auction_file:
        auction_data = json.load(auction_file)

    #Extract decimals from pkl file
    pickle_file = os.path.join("cache", "symbols_and_decimals.pkl")
    with open(pickle_file, 'rb') as file:
        symbols_and_decimals = pickle.load(file)
    
    # Extract the orders and the fulfilled order ids
    orders = data.get("orders", [])

    fulfilled_order_ids = {order.get("id") for solution in auction_data.get("solutions", []) for order in solution.get("orders", [])}

    # Get the actual eth price
    eth_price = get_eth_price_usd()

    # Prepare the list to hold the extracted data
    data_list = []

    # Loop through each order and extract the required fields
    for order in orders:
        uid = order.get("uid")
        kind = order.get("kind")
        trx_class = order.get("class")
        
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

        token_bought_info = symbols_and_decimals.get(token_bought)
        if token_bought_info:
                token_bought_amount *= 10**(-token_bought_info['decimals'])
        else:
            token_bought_amount = None

        token_sold_info = symbols_and_decimals.get(token_sold)
        if token_sold_info:
                token_sold_amount *= 10**(-token_sold_info['decimals'])
        else:
            token_sold_amount = None


        # Calculate amount_usd
        if token_sold_amount is not None and token_sold_price_usd is not None:
            amount_usd = token_sold_amount * token_sold_price_usd
        else:
            amount_usd = None

        # Determine if the order is fulfilled

        fulfill = 1 if uid in fulfilled_order_ids else 0

        fee = 0 
        try:
            if fulfill == 1:
                fee = int(order.get('protocolFees')[0]["priceImprovement"]["quote"]["fee"]) * token_sold_price_usd * 10**(-token_sold_info['decimals'])
        except Exception as e:
            warnings.warn("fee not found in file")
        
        data_list.append({
            "uid": uid,
            "amount_usd": amount_usd,
            "kind": kind,
            "class": trx_class,
            "token_bought_symbol": token_bought_symbol,
            "token_sold_symbol": token_sold_symbol,
            "token_bought_amount": token_bought_amount,
            "token_sold_amount": token_sold_amount,
            "token_bought_price_usd": token_bought_price_usd,
            "token_sold_price_usd": token_sold_price_usd,
            "fulfill": fulfill,
            "fee": fee
        })

    # Convert the list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(data_list)

    # Save the DataFrame to a CSV file
    csv_filename = os.path.join("dataframes", f"dataframe_{block_id}.csv")
    df.to_csv(csv_filename, index=False)

    print(f"Data successfully saved to {csv_filename}")

dataframes_folder = "auction_data"
list_of_datasets = [int(re.search(r"data_id_(\d+)\.json", f).group(1)) for f in os.listdir(dataframes_folder) if re.search(r"data_id_(\d+)\.json", f)]

for dataset in list_of_datasets:
    getOrderBookData(dataset)

# getOrderBookData('9142110')
