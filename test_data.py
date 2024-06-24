from time_dependence_CoW import getWeightProportion, getDataFrameFirstMinutes
from optimize_swap import optimizeSwap
import pandas as pd

# Import the dataframe
df = pd.read_csv('query_result.csv')
df = df.dropna()
df2 = pd.read_csv('rainbowSwap.csv')
MINUTES = 60

# Store the fullfill percentage of CoW
df_minutes = getDataFrameFirstMinutes(MINUTES)
CoW_fill_percentage = getWeightProportion(df_minutes)

# Rename columns to run optiize_swap script
df.rename(columns={'time': 'block_time'}, inplace=True)
df.rename(columns={'buy_token': 'token_bought_symbol'}, inplace=True)
df.rename(columns={'sell_token': 'token_sold_symbol'}, inplace=True)
df.rename(columns={'units_bought': 'token_bought_amount'}, inplace=True)
df.rename(columns={'units_sold': 'token_sold_amount'}, inplace=True)
df.rename(columns={'tx_hash': 'tx_from'}, inplace=True)
df.rename(columns={'sell_value_usd': 'amount_usd'}, inplace=True)

df['price_token_sold']=df['amount_usd']/df['token_sold_amount']
df['price_token_bought']=df['amount_usd']/df['token_bought_amount']

# Get the fullfill percentage of each transaction
sol = optimizeSwap(df, MINUTES)
fullfilled_percentage = sol.fulfilled_percentage * 0.01
last_minutes_df = df[df['block_time'] > df['block_time'].max() - pd.Timedelta(minutes=MINUTES)]

# Get the proportion
proportion_fulfilled = sum(last_minutes_df['amount_usd'].values * fullfilled_percentage) / sum(last_minutes_df['amount_usd'].values)
print("IFT fullfilled proportion = ", proportion_fulfilled)
print("CoW fullfilled proportion = ", CoW_fill_percentage)

