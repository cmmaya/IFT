from optimize_swap import optimizeSwap
import pandas as pd

# Import the dataframe
df = pd.read_csv('dataframe_9051834.csv')
df = df[df['amount_usd'] != 0] # Drop columns with no price data
df_first_50 = df.head(50) # First 50 rows

df_first_50['price_token_sold']=df_first_50['amount_usd']/df_first_50['token_sold_amount']
df_first_50['price_token_bought']=df_first_50['amount_usd']/df_first_50['token_bought_amount']

# Get the fullfill percentage of each transaction
sol = optimizeSwap(df_first_50)
fullfilled_percentage = sol.fulfilled_percentage * 0.01
fullfilled_proportion = sum(fullfilled_percentage.values * df_first_50['amount_usd'].values) / sum(df_first_50['amount_usd'].values)
# Get the proportion
print("IFT fullfilled proportion = ", fullfilled_percentage)
print("IFT fullfilled proportion = ", fullfilled_proportion)

