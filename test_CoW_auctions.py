# Here we run for multiple auctions a revision of: number of trx filled

import pandas as pd
import os
from get_orderBook_data import getOrderBookData

csv_filename = os.path.join("dataframes",'dataframe_9051834.csv')
df = pd.read_csv(csv_filename)

list_of_auctions = ["9051834", "9060621", "9060632", "9060646", "9060658"]

def obtain_data(list_of_auctions):
    for auction_id in list_of_auctions:
        getOrderBookData(auction_id)

for auction_id in list_of_auctions:
    csv_filename = os.path.join("dataframes",f"dataframe_{auction_id}.csv")
    df = pd.read_csv(csv_filename)
    num_of_trx_filled = sum(df['fulfill'])
    num_of_trx = len(df)
    print("id", auction_id, "  ","num_of_trx = ", num_of_trx, "  ", "num_of_trx_filled=", num_of_trx_filled)



# obtain_data(list_of_auctions)

