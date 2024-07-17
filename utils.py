from web3 import Web3
import json
import os
import warnings
import requests
import pickle

# Initialize Web3
web3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/eth'))

# ABI for the ERC20 token contract to get the symbol
abi = [
    {"inputs": [], "name": "name", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "symbol", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}
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

# Function to get token price in USD using local JSON file
def get_token_price_usd_from_file(token_hash, uid, eth_price):
    """
    Retrieves the USD price for a given token hash using a local JSON file.

    Parameters:
    token_hash (str): The hash of the token.
    uid (str): The unique identifier for the auction.

    Returns:
    float: The price of the token in USD, or None if not found.
    """
    cache_file =  os.path.join("cache", "token_cache.json")
    pickle_file = os.path.join("cache", "symbols_and_decimals.pkl")
    auction_file = os.path.join("auction_data", f"auction_{uid}.json")

    try:
        with open(pickle_file, 'rb') as file:
            symbols_and_decimals = pickle.load(file)
        with open(auction_file, 'r') as file:
            data = json.load(file)
            prices = data.get("auction", {}).get("prices", {})
            
            if token_hash in prices:
                if token_hash in symbols_and_decimals:
                    decimals = symbols_and_decimals[token_hash]['decimals']
                    price = prices[token_hash]
                    price_usd = int(price) * eth_price * 1e-18 / 10**(18 - decimals)
                    return price_usd
    except Exception as e:
        warnings.warn(f"Warning: Error reading auction file. Error: {str(e)}")

    # Try to get the price from the current JSON file
    try:
        with open(cache_file, 'r') as file:
            data = json.load(file)
            hash_price_pairs = {k: v['price_usd'] for k, v in data.items() if 'price_usd' in v}
            
            if token_hash in hash_price_pairs:
                return hash_price_pairs[token_hash]

    except Exception as e:
        warnings.warn(f"Warning: Error reading cahe file. Error: {str(e)}")
    # If price not found in either, return None
    return None

# Local cache for symbols only
cache_file = 'cache/token_cache.json'
if os.path.exists(cache_file):
    with open(cache_file, 'r') as f:
        token_cache = json.load(f)
else:
    token_cache = {}

def save_cache():
    with open(cache_file, 'w') as f:
        json.dump(token_cache, f)

def get_token_info(address, uid, eth_price):
    # Fetch symbol using Web3 and check cache first
    if address in token_cache:
        token_symbol = token_cache[address]['symbol']
    else:
        token_symbol = get_token_symbol(address)
        token_cache[address] = {'symbol': token_symbol}
        save_cache()

    # Fetch price using local JSON file
    token_price = get_token_price_usd_from_file(address, uid, eth_price)

    return {'symbol': token_symbol, 'price_usd': token_price}

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

# Example usage
# uid = "9142103"
# eth_price = 3462
# token_info = get_token_info("0x2260fac5e5542a773aa44fbcfedf7c193bc2c599", uid, eth_price)
# print(token_info['symbol'])
# print(token_info['price_usd'])
