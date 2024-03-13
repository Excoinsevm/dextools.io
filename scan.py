import dotenv
import os
import requests
import sqlite3
from datetime import datetime, timedelta

class LiquidityPoolExtractor:
    def __init__(self, api_key, chains, database_path='database.db'):
        self.API_KEY = api_key
        self.headers = {
            'accept': 'application/json',
            'x-api-key': self.API_KEY,
        }
        self.params = {
            'sort': 'creationTime',
            'order': 'desc',
            'pageSize': 50,
        }
        self.chains = chains
        self.database_path = database_path

    def connect_to_database(self):
        return sqlite3.connect(self.database_path)

    def extract_liquidity_pools(self, chain):
        params = self.params.copy()
        params['from'] = datetime.now() - timedelta(hours=24)
        params['to'] = datetime.now()

        response = requests.get(f'https://public-api.dextools.io/trial/v2/pool/{chain}', params=params, headers=self.headers)

        if response.status_code == 200:
            liquidity_pools = response.json()['data']['results']
            self.save_liquidity_pools(chain, liquidity_pools)
        else:
            print(f'chain: {chain}, status code: {response.status_code}')

    def save_liquidity_pools(self, chain, liquidity_pools):
        with self.connect_to_database() as conn:
            cursor = conn.cursor()

            for data in liquidity_pools:
                # Extracting values from the data dictionary
                main_token_name = data['mainToken']['name']
                main_token_symbol = data['mainToken']['symbol']
                main_token_address = data['mainToken']['address']
                exchange_name = data['exchange']['name']
                exchange_factory = data['exchange']['factory']
                address = data['address']
                side_token_name = data['sideToken']['name']
                side_token_symbol = data['sideToken']['symbol']
                side_token_address = data['sideToken']['address']
                creation_time = data['creationTime']

                # Insert data into the table
                cursor.execute(
                    """
                        REPLACE INTO LiquidityPools (
                        chain,mainToken_name, mainToken_symbol, mainToken_address,
                        exchange_name, exchange_factory, address,
                        sideToken_name, sideToken_symbol, sideToken_address,
                        creationTime
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, 
                    (
                        chain, main_token_name, main_token_symbol, main_token_address,
                        exchange_name, exchange_factory, address,
                        side_token_name, side_token_symbol, side_token_address,
                        creation_time
                    )
                )
                conn.commit()

    def run_extraction(self):
        for chain in self.chains:
            self.extract_liquidity_pools(chain)

if __name__ == "__main__":
    dotenv.load_dotenv()
    api_key = os.getenv('API_KEY')
    chains = ['ether']

    extractor = LiquidityPoolExtractor(api_key, chains)
    extractor.run_extraction()
