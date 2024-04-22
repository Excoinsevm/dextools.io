import requests
import sqlite3
import time
import dotenv
import os
import config

class InfoDataFetcher:
    def __init__(self, delay=60):
        dotenv.load_dotenv()
        self.API_KEY = os.getenv('API_KEY')
        self.headers = {
            'accept': 'application/json',
            'x-api-key': self.API_KEY,
        }
        self.connection = sqlite3.connect('database.db')
        self.cursor = self.connection.cursor()
        self.delay = delay
        self.liquidity=config.liquidity

    def fetch_distinct_addresses(self):
        query = f"""
            SELECT DISTINCT chain,address 
                    FROM LiquidityPools 
                    WHERE creationTime >= datetime('now', '-1 day')
                AND mainToken_address NOT IN (SELECT mainToken_address from TelegramAleart)
				AND address NOT IN (SELECT LiquidityPoolAddress from LiquidityData WHERE liquidity>={config.liquidity});
        """
        self.cursor.execute(query)
        return [row for row in self.cursor.fetchall()]

    def extract_liquidity_pool_info(self, chain,liquidity_pool_address):
        response = requests.get(
            f'https://public-api.dextools.io/trial/v2/pool/{chain}/{liquidity_pool_address}/price',
            headers=self.headers,
        )
        if response.status_code == 200:
            return response.json()['data']
        else:
            print(f'LiquidityPoolAddress: {liquidity_pool_address}, status code: {response.status_code}')
            return None

    def insert_infodata(self, info_data, liquidity_pool_address):
        if info_data:
            columns = ', '.join([*info_data.keys(), 'LiquidityPoolAddress'])
            values = ', '.join(['COALESCE(?, NULL)' for _ in info_data]+ ['?'])
            insert_statement = f"""
            REPLACE INTO I InfoData ({columns})
            VALUES ({values})
            """
            self.cursor.execute(insert_statement, [*info_data.values(), liquidity_pool_address])
            self.connection.commit()
            print(f'Inserted InfoData: {liquidity_pool_address}')

    def fetch_and_insert_prices(self):
        distinct_addresses = self.fetch_distinct_addresses()
        for chain,liquidity_pool_address in distinct_addresses:
            info_data = self.extract_liquidity_pool_info(chain,liquidity_pool_address)
            self.insert_infodata(info_data, liquidity_pool_address)
            time.sleep(1)

    def run(self):
        while True:
            self.fetch_and_insert_prices()
            print(f"Waiting for {self.delay} seconds before next update...")
            time.sleep(self.delay)

# usage:
if __name__ == "__main__":
    price_fetcher = InfoDataFetcher(delay=10)  # Set delay to x seconds
    price_fetcher.run()
