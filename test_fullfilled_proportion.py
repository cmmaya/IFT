from optimize_swap import optimizeSwap
import pandas as pd
import os
import time
import re

# Function to process chunks and collect results
def process_chunk(chunk_num, df, dataset_id):
    start_time_chunk = time.time()  # Start time for the chunk processing
    df_chunk = df.iloc[0:50].copy()
    
    try:
        # Calculate prices
        df_chunk['price_token_sold'] = df_chunk['amount_usd'] / df_chunk['token_sold_amount']
        df_chunk['price_token_bought'] = df_chunk['amount_usd'] / df_chunk['token_bought_amount']

        # Optimize and calculate fullfilled proportion
        sol = optimizeSwap(df_chunk)
        fullfilled_percentage = sol.fulfilled_percentage * 0.01
        volume_paired = sum(fullfilled_percentage.values * df_chunk['amount_usd'].values)
        fullfilled_proportion = volume_paired / sum(df['amount_usd'].values)
        total_volume = sum(df['amount_usd'].values)
        Volume_fee_estimate = volume_paired * 0.0001

        CoW_total_volume = sum(df['fulfill'].values * df['amount_usd'].values)
        CoW_proportion_volume = CoW_total_volume / sum(df['amount_usd'].values)
        CoW_transaction_paired = sum(df['fulfill'])
        CoW_fee_estimate =  sum(df['fee'])


        # Return chunk results
        return {
            'auction_id': dataset_id,
            'deals_paired': sum(sol.fulfilled_percentage.values) / 100,
            'fullfilled_proportion': fullfilled_proportion,
            'total_volume': total_volume,
            'volume_paired': volume_paired,
            'execution_time_seconds': time.time() - start_time_chunk,
            'CoW_total_volume': CoW_total_volume,
            'CoW_volume_proportion': CoW_proportion_volume,
            'CoW transaction paired': CoW_transaction_paired,
            'CoW_fee_estimate': CoW_fee_estimate,
            'Volume_fee_estimate': Volume_fee_estimate
        }
    except Exception as e:
        print(f"Error occurred in chunk {chunk_num}: {str(e)}")
        return None

# Start time for the entire script
start_time_script = time.time()



def Iterate_over_chunks(df, chunk_size):
    results = []
    # Iterate over chunks
    num_chunks = len(df) // chunk_size
    for chunk_num in range(num_chunks):
        start_idx = chunk_num * chunk_size
        end_idx = (chunk_num + 1) * chunk_size
        df_chunk = df.iloc[start_idx:end_idx].copy()
        
        # Process chunk and handle errors
        chunk_result = process_chunk(chunk_num + 1, df_chunk, 0)
        if chunk_result is not None:
            results.append(chunk_result)
        else:
            print(f"Skipping chunk {chunk_num + 1} due to error.")
        print(f"executed chunk, operation time: {time.time() - start_time_script}")
    return results

def iterate_over_datasets(list_of_datasets):
    results = []
    i = 1

    # Iterate over dataSets
    for dataset in list_of_datasets:
        i += 1
        csv_filename = os.path.join("dataframes", f"dataframe_{dataset}.csv")
        df = pd.read_csv(csv_filename)
        df = df.dropna(how='any')
        df = df[df['amount_usd'] <= 1e6]  # Drop rows with dubious data
        df = df[(df['token_sold_amount'] <= 1e6) | (df['token_sold_amount'] >= 1e-3) ]  # Drop rows with dubious data
        df = df[(df['token_bought_amount'] <= 1e6) |( df['token_bought_amount'] >= 1e-3) ]  # Drop rows with dubious data
        # Process chunk and handle errors
        chunk_result = process_chunk(1, df, dataset)
        if chunk_result is not None:
            results.append(chunk_result)
        else:
            print(f"Skipping dataSet {i} due to error.")
        print(f"executed dataSet, operation time: {time.time() - start_time_script}")
    return results

## ---------------------------------
# Import the dataframe
# csv_filename = os.path.join("dataframes", 'dataframe_9051834.csv')
# df = pd.read_csv(csv_filename)
# df = df[df['amount_usd'] != 0]  # Drop rows with no price data
# df = df[df['amount_usd'] <= 10e6]  # Drop rows with dubious data

# # Define chunk size
# chunk_size = 50

# # Convert results list to DataFrame
# results_chunk_iteration = pd.DataFrame(Iterate_over_chunks(df, chunk_size))

# results_filename = os.path.join("results", "chunk_iteration_results.csv")
# results_chunk_iteration.to_csv(results_filename, index=False)

##--------------------------------
dataframes_folder = "dataframes"
list_of_datasets = [int(re.search(r"dataframe_(\d+)\.csv", f).group(1)) for f in os.listdir(dataframes_folder) if re.search(r"dataframe_(\d+)\.csv", f)]
results_dataset_iteration = pd.DataFrame(iterate_over_datasets(list_of_datasets))
results_filename = os.path.join("results", "datasets_iteration_results.csv")
results_dataset_iteration.to_csv(results_filename, index=False)


# End time for the entire script
end_time_script = time.time()
elapsed_time_script = end_time_script - start_time_script

# Print the total elapsed time for the entire script
print(f"Total time taken to execute the script: {elapsed_time_script:.2f} seconds")
