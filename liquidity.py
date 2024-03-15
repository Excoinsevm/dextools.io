# Retrieve liquidity information of a specific pool.
import dotenv
import os
import requests
import sqlite3
import time

dotenv.load_dotenv()
API_KEY = os.getenv('API_KEY')

headers = {
    'accept': 'application/json',
    'x-api-key': '',
}

headers['x-api-key']=API_KEY

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

# SQLite query to select distinct addresses from the LiquidityPools table
query = "SELECT DISTINCT address FROM LiquidityPools WHERE creationTime >= datetime('now', '-1 day');"

# Execute the query
cursor.execute(query)

# Fetch all the distinct addresses as a list
distinct_addresses = [row[0] for row in cursor.fetchall()]

def extract_liquidity_info(LiquidityPoolAddress):
    response = requests.get(
        f'https://public-api.dextools.io/trial/v2/pool/ether/{LiquidityPoolAddress}/liquidity',
        headers=headers,
    )
    if response.status_code == 200:
            liquidity = response.json()['data']['liquidity']
            cursor.execute(
                    """
                        REPLACE INTO LiquidityData (
                        LiquidityPoolAddress,liquidity
                        ) VALUES (?, ?)
                    """, 
                    (
                        LiquidityPoolAddress,liquidity
                    )
                )
            connection.commit()
            print(f'LiquidityPoolAddress: {LiquidityPoolAddress}, liquidity: {liquidity}')
    else:
        print(f'LiquidityPoolAddress: {LiquidityPoolAddress}, status code: {response.status_code}')

for LiquidityPoolAddress in distinct_addresses:
    extract_liquidity_info(LiquidityPoolAddress)
    time.sleep(1)