from web3 import Web3
import json
import os
import warnings
import requests

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
    auction_file = f"auction_{uid}.json"
    
    if not os.path.exists(auction_file):
        warnings.warn(f"Warning: Auction file {auction_file} not found.")
        return None

    try:
        with open(auction_file, 'r') as file:
            data = json.load(file)
            prices = data.get("auction", {}).get("prices", {})

            if token_hash in prices:
                # if get_token_symbol(token_hash) in ['USDC', 'USDT']:
                #     token_sold_amount *= 1e-6
                # else:
                #     token_sold_amount *= 1e-18               
                usd_price = int(prices[token_hash]) * eth_price
                return usd_price
            else:
                warnings.warn(f"Warning: Token price for {token_hash} not found in auction file.")
                return None
    except Exception as e:
        warnings.warn(f"Warning: Error reading auction file {auction_file}. Error: {str(e)}")
        return None

# Local cache for symbols only
cache_file = 'token_cache.json'
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
# uid = "9051834"
# token_info = get_token_info("0xae7ab96520de3a18e5e111b5eaab095312d7fe84", uid)
# print(token_info['symbol'])
# print(token_info['price_usd'])
