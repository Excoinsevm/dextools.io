#Fetch price information of a specific liquidity pool.
import requests
import sqlite3
import time
import dotenv
import os

dotenv.load_dotenv()
API_KEY = os.getenv('API_KEY')

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

# SQLite query to select distinct addresses from the LiquidityPools table
query = "SELECT LiquidityPoolAddress FROM LiquidityData WHERE liquidity IS NOT NULL and LiquidityPoolAddress in (SELECT DISTINCT address FROM LiquidityPools WHERE creationTime >= datetime('now', '-1 day'));"

# Execute the query
cursor.execute(query)

# Fetch all the distinct addresses as a list
distinct_addresses = [row[0] for row in cursor.fetchall()]

headers = {
    'accept': 'application/json',
    'x-api-key': '',
}

headers['x-api-key']=API_KEY

def extract_liquidity_pool_market(LiquidityPoolAddress):
    response = requests.get(
        f'https://public-api.dextools.io/trial/v2/pool/ether/{LiquidityPoolAddress}/price',
        headers=headers,
    )
    if response.status_code == 200:
            marketData = response.json()['data']
            #print(f'LiquidityPoolAddress: {LiquidityPoolAddress}, marketData: {marketData}')
    else:
        print(f'LiquidityPoolAddress: {LiquidityPoolAddress}, status code: {response.status_code}')
    return marketData

# SQLite table name
table_name = 'MarketData'
def insert_marketdata(marketData,LiquidityPoolAddress):
    # Get the column names and values
    columns = ', '.join([*marketData.keys(), 'LiquidityPoolAddress'])
    values = ', '.join(['COALESCE(?, NULL)' for _ in marketData]+ ['?'])
    # Create the INSERT statement with COALESCE to handle missing keys
    insert_statement = f"""
    REPLACE INTO {table_name} ({columns})
    VALUES ({values})
    """
    # Execute the INSERT statement
    cursor.execute(insert_statement, [*marketData.values(), LiquidityPoolAddress])
    # Commit the transaction
    connection.commit()
    print(f'Inserted LiquidityPoolAddress: {LiquidityPoolAddress}')

for LiquidityPoolAddress in distinct_addresses:
    marketData=extract_liquidity_pool_market(LiquidityPoolAddress)
    insert_marketdata(marketData,LiquidityPoolAddress)
    time.sleep(1)