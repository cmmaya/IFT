from optimize_swap import optimizeSwap
import pandas as pd
import os
import time

# Function to process chunks and collect results
def process_chunk(chunk_num, df_chunk):
    start_time_chunk = time.time()  # Start time for the chunk processing
    
    try:
        # Calculate prices
        df_chunk['price_token_sold'] = df_chunk['amount_usd'] / df_chunk['token_sold_amount']
        df_chunk['price_token_bought'] = df_chunk['amount_usd'] / df_chunk['token_bought_amount']

        # Optimize and calculate fullfilled proportion
        sol = optimizeSwap(df_chunk)
        fullfilled_percentage = sol.fulfilled_percentage * 0.01
        fullfilled_proportion = sum(fullfilled_percentage.values * df_chunk['amount_usd'].values) / sum(df_chunk['amount_usd'].values)

        # Return chunk results
        return {
            'chunk': chunk_num,
            'fullfilled_proportion': fullfilled_proportion,
            'execution_time_seconds': time.time() - start_time_chunk
        }
    except Exception as e:
        print(f"Error occurred in chunk {chunk_num}: {str(e)}")
        return None

# Start time for the entire script
start_time_script = time.time()

# Import the dataframe
csv_filename = os.path.join("dataframes", 'dataframe_9051834.csv')
df = pd.read_csv(csv_filename)
df = df[df['amount_usd'] != 0]  # Drop rows with no price data

# Define chunk size
chunk_size = 50

# Initialize empty list to collect results
results = []

# Iterate over chunks
num_chunks = len(df) // chunk_size
for chunk_num in range(5):
    start_idx = chunk_num * chunk_size
    end_idx = (chunk_num + 1) * chunk_size
    df_chunk = df.iloc[start_idx:end_idx].copy()
    
    # Process chunk and handle errors
    chunk_result = process_chunk(chunk_num + 1, df_chunk)
    if chunk_result is not None:
        results.append(chunk_result)
    else:
        print(f"Skipping chunk {chunk_num + 1} due to error.")
    print(f"executed chunk, operation time: {time.time() - start_time_script}")

# Convert results list to DataFrame
results_df = pd.DataFrame(results)

# Save results to CSV
results_folder = "results"
if not os.path.exists(results_folder):
    os.makedirs(results_folder)

results_filename = os.path.join(results_folder, "optimization_results.csv")
results_df.to_csv(results_filename, index=False)

# End time for the entire script
end_time_script = time.time()
elapsed_time_script = end_time_script - start_time_script

# Print the total elapsed time for the entire script
print(f"Total time taken to execute the script: {elapsed_time_script:.2f} seconds")
