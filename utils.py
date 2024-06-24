import requests
import time

def get_token_symbol(token_hash, retries=3, delay=5):
    """
    Retrieves the token symbol for a given token hash using the CoinGecko API.

    Parameters:
    token_hash (str): The hash of the token.
    retries (int): Number of retries for the API request in case of failure.
    delay (float): Delay in seconds between each retry.

    Returns:
    str: The symbol of the token.
    """
    url = f"https://api.coingecko.com/api/v3/coins/ethereum/contract/{token_hash}"
    
    for attempt in range(retries):
        try:
            response = requests.get(url)
            data = response.json()
            
            if "symbol" in data:
                token_symbol = data["symbol"].upper()  # Convert symbol to uppercase for consistency
                return token_symbol
            else:
                raise ValueError(f"Error retrieving token symbol for {token_hash}: {data.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for token symbol {token_hash}: {e}")
            time.sleep(delay)  # Delay before retrying
    raise ValueError(f"Failed to retrieve token symbol for {token_hash} after {retries} attempts")

def get_token_price_usd(token_hash, retries=3, delay=5):
    """
    Retrieves the current USD price for a given token hash using the CoinGecko API.

    Parameters:
    token_hash (str): The hash of the token.
    retries (int): Number of retries for the API request in case of failure.
    delay (float): Delay in seconds between each retry.

    Returns:
    float: The current price of the token in USD.
    """
    url = f"https://api.coingecko.com/api/v3/simple/token_price/ethereum"
    
    params = {
        "contract_addresses": token_hash,
        "vs_currencies": "usd"
    }
    
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if token_hash in data:
                price_usd = data[token_hash]["usd"]
                return price_usd
            else:
                raise ValueError(f"Error retrieving price for token {token_hash}: {data.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for token price {token_hash}: {e}")
            time.sleep(delay)  # Delay before retrying
    raise ValueError(f"Failed to retrieve token price for {token_hash} after {retries} attempts")