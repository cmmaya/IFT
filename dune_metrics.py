import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate

# Load the CSV file
csv_filename = os.path.join("dataframes", 'duneData.csv')
df = pd.read_csv(csv_filename)

# Create the results directory if it doesn't exist
if not os.path.exists("results"):
    os.makedirs("results")

# Top 10 most used "buy_token" and "sell_token"
top_buy_tokens = df['buy_token'].value_counts().head(10)
top_sell_tokens = df['sell_token'].value_counts().head(10)

# Mean percentage of fees: "fee" / "units_sold"
df['fee_percentage'] = (df['fee'] / df['units_sold']) * 100
mean_fee_percentage = df['fee_percentage'].mean()

# Top 10 sell_tokens with more percentage fees
top_sell_tokens_fee_percentage = df.groupby('sell_token')['fee_percentage'].mean().sort_values(ascending=False).head(10)

# Top 10 most volume transactions based on sell_value_usd
top_volume_transactions = df[['sell_token', 'buy_token', 'sell_value_usd']].sort_values(by='sell_value_usd', ascending=False).head(10)

# Top 10 most volume transactions excluding USDT, USDC, DAI
excluded_tokens = ['USDT', 'USDC', 'DAI']
filtered_df = df[~df['sell_token'].isin(excluded_tokens)]
top_volume_transactions_excluding_stablecoins = filtered_df[['sell_token', 'buy_token', 'sell_value_usd']].sort_values(by='sell_value_usd', ascending=False).head(10)

# Top 10 highest fees
top_fees = df[['sell_token', 'fee']].sort_values(by='fee', ascending=False).head(10)

# Median transaction volume
median_volume_usd = df[['buy_value_usd', 'sell_value_usd']].median()

# Standard deviation of transaction volumes
std_volume_usd = df[['buy_value_usd', 'sell_value_usd']].std()

# Count of unique transactions
transactions = len(df['tx_hash'])
unique_transactions = df['tx_hash'].nunique()

# Plot Top 10 most used buy_token
plt.figure(figsize=(10, 6))
sns.barplot(x=top_buy_tokens.values, y=top_buy_tokens.index, palette="viridis")
plt.title('Top 10 Most Used Buy Tokens')
plt.xlabel('Count')
plt.ylabel('Buy Token')
plt.savefig(os.path.join("results", "top_10_buy_tokens.png"))
plt.close()

# Plot Top 10 most used sell_token
plt.figure(figsize=(10, 6))
sns.barplot(x=top_sell_tokens.values, y=top_sell_tokens.index, palette="viridis")
plt.title('Top 10 Most Used Sell Tokens')
plt.xlabel('Count')
plt.ylabel('Sell Token')
plt.savefig(os.path.join("results", "top_10_sell_tokens.png"))
plt.close()

# Plot Top 10 sell_tokens with highest percentage fees
plt.figure(figsize=(10, 6))
sns.barplot(x=top_sell_tokens_fee_percentage.values, y=top_sell_tokens_fee_percentage.index, palette="viridis")
plt.title('Top 10 Sell Tokens with Highest Percentage Fees')
plt.xlabel('Fee Percentage')
plt.ylabel('Sell Token')
plt.savefig(os.path.join("results", "top_10_sell_tokens_fee_percentage.png"))
plt.close()

# Plot Top 10 most volume transactions excluding stablecoins
plt.figure(figsize=(10, 6))
sns.barplot(x=top_volume_transactions_excluding_stablecoins['sell_value_usd'], y=top_volume_transactions_excluding_stablecoins['sell_token'], palette="viridis")
plt.title('Top 10 Most Volume Transactions Excluding USDT, USDC, DAI')
plt.xlabel('Sell Value USD')
plt.ylabel('Sell Token')
plt.savefig(os.path.join("results", "top_10_volume_transactions_excluding_stablecoins.png"))
plt.close()

# Write statistics to a markdown file
output_file = os.path.join("results", 'transaction_statistics.md')
with open(output_file, 'w') as f:
    f.write("# CoW Protocol Metrics\n\n")
    f.write(f"**Count of transactions**: {transactions}\n")
    f.write(f"**Count of unique transactions**: {unique_transactions}\n\n")

    f.write("## Token Metrics\n\n")
    f.write("### Top 10 Most Used Buy Tokens\n")
    f.write(tabulate(top_buy_tokens.reset_index().values, headers=["Token", "Count"], tablefmt="pipe"))
    f.write("\n![Top 10 Most Used Buy Tokens](top_10_buy_tokens.png)\n\n")
    f.write("### Top 10 Most Used Sell Tokens\n")
    f.write(tabulate(top_sell_tokens.reset_index().values, headers=["Token", "Count"], tablefmt="pipe"))
    f.write("\n![Top 10 Most Used Sell Tokens](top_10_sell_tokens.png)\n\n")

    f.write("## Fees Metrics\n\n")
    f.write(f"### Mean Percentage of Fees\n")
    f.write(f"{mean_fee_percentage:.2f}%\n\n")
    f.write("### Top 10 Sell Tokens with Highest Percentage Fees\n")
    f.write(tabulate(top_sell_tokens_fee_percentage.reset_index().values, headers=["Token", "Fee Percentage"], tablefmt="pipe"))
    f.write("\n![Top 10 Sell Tokens with Highest Percentage Fees](top_10_sell_tokens_fee_percentage.png)\n\n")

    f.write("## Volume Metrics\n\n")
    f.write("### Top 10 Most Volume Transactions (Sell -> Buy)\n")
    f.write(tabulate(top_volume_transactions.values, headers=["Sell Token", "Buy Token", "Sell Value USD"], tablefmt="pipe"))
    f.write("\n\n### Top 10 Most Volume Transactions Excluding USDT, USDC, DAI (Sell -> Buy)\n")
    f.write(tabulate(top_volume_transactions_excluding_stablecoins.values, headers=["Sell Token", "Buy Token", "Sell Value USD"], tablefmt="pipe"))
    f.write("\n![Top 10 Most Volume Transactions Excluding USDT, USDC, DAI](top_10_volume_transactions_excluding_stablecoins.png)\n\n")
    
    f.write("### Top 10 Highest Fees\n")
    f.write(tabulate(top_fees.values, headers=["Sell Token", "Fee"], tablefmt="pipe"))
    
    f.write("\n\n### Median Volume USD per Transaction\n")
    f.write(tabulate(median_volume_usd.reset_index().values, headers=["Metric", "Value"], tablefmt="pipe"))
    
    f.write("\n\n### Standard Deviation of Volume USD per Transaction\n")
    f.write(tabulate(std_volume_usd.reset_index().values, headers=["Metric", "Value"], tablefmt="pipe"))

print(f"Statistics and graphs have been written to the 'results' directory")
