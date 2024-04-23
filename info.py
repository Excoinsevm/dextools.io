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
            SELECT DISTINCT chain,mainToken_address 
                    FROM LiquidityPools 
                    WHERE creationTime >= datetime('now', '-1 day')
                AND mainToken_address NOT IN (SELECT mainToken_address from TelegramAleart)
				AND address IN (SELECT LiquidityPoolAddress from LiquidityData WHERE liquidity>={config.liquidity});
        """
        self.cursor.execute(query)
        data=[row for row in self.cursor.fetchall()]
        return data

    def extract_liquidity_pool_info(self, chain,mainToken_address):
        response = requests.get(
            f'https://public-api.dextools.io/standard/v2/token/{chain}/{mainToken_address}/info',
            headers=self.headers,
        )
        if response.status_code == 200:
            return response.json()['data']
        else:
            print(f'mainToken_address: {mainToken_address}, status code: {response.status_code}')
            return None

    def insert_infodata(self, info_data, mainToken_address):
        if info_data:
            columns = ', '.join([*info_data.keys(), 'mainToken_address'])
            values = ', '.join(['COALESCE(?, NULL)' for _ in info_data]+ ['?'])
            insert_statement = f"""
            REPLACE INTO InfoData ({columns})
            VALUES ({values})
            """
            self.cursor.execute(insert_statement, [*info_data.values(), mainToken_address])
            self.connection.commit()
            print(f'Inserted InfoData: {mainToken_address}')

    def fetch_and_insert_prices(self):
        distinct_addresses = self.fetch_distinct_addresses()
        for chain,mainToken_address in distinct_addresses:
            info_data = self.extract_liquidity_pool_info(chain,mainToken_address)
            print(info_data)
            self.insert_infodata(info_data, mainToken_address)
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
