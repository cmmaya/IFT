import pandas as pd
from dune_client.client import DuneClient

# Initialize the DuneClient with your API key
dune = DuneClient("UbiIvkzQZlVWnKnl0RyGbBiv7nKFnPSK")

# Get the latest result of the specified query
query_result = dune.get_latest_result(3849243)

# Assuming `query_result` is an instance of ResultsResponse
# You need to use appropriate methods to access the data
rows = query_result.result.rows

# Define the columns based on the metadata
columns = [
    'time', 'tx_hash', 'sell_token', 'buy_token', 'units_sold',
    'units_bought', 'buy_price', 'sell_price', 'buy_value_usd',
    'sell_value_usd', 'fee', 'limit_sell_amount', 'limit_buy_amount',
    'partial_fill', 'fill_proportion', 'surplus_usd'
]

# Convert the rows to a pandas DataFrame
df = pd.DataFrame(rows, columns=columns)

# Save the DataFrame to a CSV file
df.to_csv('query_result.csv', index=False)

print("Query result saved to query_result.csv")
