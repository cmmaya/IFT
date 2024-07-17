import requests
import os
import time

# Create the directory if it does not exist
output_dir = 'auction_data'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def download_json_files():
    file_count = 0
    
    while file_count < 100:
        try:
            # Fetch the first JSON
            url_auction = 'https://api.cow.fi/mainnet/api/v1/auction'
            response_auction = requests.get(url_auction)
            if response_auction.status_code == 200:
                auction_data = response_auction.json()
                id_value = auction_data.get('id')

                if id_value:
                    url_solver = f'https://api.cow.fi/mainnet/api/v1/solver_competition/{id_value}'
                    response_solver = requests.get(url_solver)

                    # Check if the second URL returns an error
                    if response_solver.status_code == 200 and 'NotFound' not in response_solver.json().values():
                        auction_filename = os.path.join(output_dir, f'data_id_{id_value}.json')
                        solver_filename = os.path.join(output_dir, f'auction_{id_value}.json')

                        # Save the first JSON file
                        with open(auction_filename, 'w') as file:
                            file.write(response_auction.text)

                        # Save the second JSON file
                        with open(solver_filename, 'w') as file:
                            file.write(response_solver.text)

                        file_count += 2
                        print(f'Downloaded and saved files for ID: {id_value}')
                    else:
                        print(f'Solver competition not found for ID: {id_value}, skipping download.')
                else:
                    print('ID not found in auction JSON.')
            else:
                print(f'Failed to fetch auction data, status code: {response_auction.status_code}')

        except Exception as e:
            print(f'Error occurred: {e}')
        
        # Wait for 10 seconds before next iteration if successful
        if file_count % 2 == 0:
            time.sleep(10)

if __name__ == "__main__":
    download_json_files()
