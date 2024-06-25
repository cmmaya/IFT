from web3 import Web3
import json
import requests
import os
import warnings
import time
# Initialize Web3
web3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/eth'))

# ABI for the ERC20 token contract to get the symbol
abi = [
    {"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"}
]

# Function to get token symbol using Web3
def get_token_symbol(address):
    try:
        checksum_address = web3.to_checksum_address(address)  # Convert to checksum address
        contract = web3.eth.contract(address=checksum_address, abi=abi)
        token_symbol = contract.functions.symbol().call()
        return token_symbol.upper()  # Convert to uppercase for consistency
    except Exception as e:
        warnings.warn(f"Warning: Could not retrieve symbol for token {address}. Error: {str(e)}")
        return None

# Function to get token price in USD using Binance API
def get_token_price_usd(token_hash, retries=1, delay=0):
    """
    Retrieves the current USD price for a given token hash using the CoinGecko API.

    Parameters:
    token_hash (str): The hash of the token.
    retries (int): Number of retries for the API request in case of failure.
    delay (float): Delay in seconds between each retry.

    Returns:
    float: The current price of the token in USD, or None if retrieval fails.
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
                price_usd = data[token_hash].get("usd")
                if price_usd is not None:
                    return price_usd
                else:
                    raise ValueError(f"Error: USD price not found for token {token_hash}")
            else:
                raise ValueError(f"Error retrieving price for token {token_hash}: {data.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for token price {token_hash}: {e}")
            time.sleep(delay)  # Delay before retrying
    
    print(f"Failed to retrieve token price for {token_hash} after {retries} attempts")
    return None

# Local cache
cache_file = 'token_cache.json'
if os.path.exists(cache_file):
    with open(cache_file, 'r') as f:
        token_cache = json.load(f)
else:
    token_cache = {}

def save_cache():
    with open(cache_file, 'w') as f:
        json.dump(token_cache, f)

def get_token_info(address):
    # Check cache first
    if address in token_cache:
        if token_cache[address]['price_usd'] is None:
            token_cache[address]['price_usd'] = get_token_price_usd(address)
    
        if token_cache[address]['symbol'] is None:
            token_cache[address]['symbol'] = get_token_symbol(address)

        save_cache()
        return token_cache[address]

    # Fetch symbol using Web3
    token_symbol = get_token_symbol(address)

    # Fetch price using Binance API
    token_price = get_token_price_usd(address)

    # Cache the result
    token_cache[address] = {'symbol': token_symbol, 'price_usd': token_price}
    save_cache()

    return token_cache[address]

def get_eth_price_usd():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "ethereum",
        "vs_currencies": "usd"
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'ethereum' in data and 'usd' in data['ethereum']:
            return data['ethereum']['usd']
        else:
            raise ValueError("Error: Ethereum price not found in the API response")
    
    except Exception as e:
        print(f"Error fetching Ethereum price: {e}")
        return None

token_info = get_token_info("0xae7ab96520de3a18e5e111b5eaab095312d7fe84")
print(token_info['symbol'])
print(token_info['price_usd'])
