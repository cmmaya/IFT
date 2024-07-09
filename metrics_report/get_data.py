import pandas as pd
from dune_client.client import DuneClient
import os

# Initialize the DuneClient with your API key
dune = DuneClient("KbCF1Q7mvNOvlOsb7WFMgaCGX7HkVGAH")

# Get the latest result of the specified query
query_result = dune.get_latest_result(3096156)

# Assuming `query_result` is an instance of ResultsResponse
# You need to use appropriate methods to access the data
rows = query_result.result.rows

# Define the columns based on the metadata
columns = [

'aggregate_by',

'volume'
]

# Convert the rows to a pandas DataFrame
df = pd.DataFrame(rows, columns=columns)

# Save the DataFrame to a CSV file

csv_filename = os.path.join("metrics_report", "volume.csv")
df.to_csv(csv_filename, index=False)

print("Query result saved to query_result.csv")
