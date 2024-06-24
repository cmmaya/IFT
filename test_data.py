from time_dependance_CoW import getWeightProportion, getDataFrameFirstMinutes
from optimize_swap import optimizeSwap
import pandas as pd

# Import the dataframe
df = pd.read_csv('query_result.csv')
df = df.dropna()
df2 = pd.read_csv('rainbowSwap.csv')

# Store the fullfill percentage of CoW
df_minutes = getDataFrameFirstMinutes(15)
CoW_fill_percentage = getWeightProportion(df_minutes)

df.rename(columns={'time': 'block_time'}, inplace=True)
df.rename(columns={'buy_token': 'token_bought_symbol'}, inplace=True)
df.rename(columns={'sell_token': 'token_sold_symbol'}, inplace=True)
df.rename(columns={'units_bought': 'token_bought_amount'}, inplace=True)
df.rename(columns={'units_sold': 'token_sold_amount'}, inplace=True)
df.rename(columns={'tx_hash': 'tx_from'}, inplace=True)
df.rename(columns={'sell_value_usd': 'amount_usd'}, inplace=True)

df['price_token_sold']=df['amount_usd']/df['token_sold_amount']
df['price_token_bought']=df['amount_usd']/df['token_bought_amount']

sol = optimizeSwap(df, 60)
print(sol.fulfilled_percentage)

