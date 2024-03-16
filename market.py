import requests
import sqlite3
import time
import dotenv
import os

class MarketDataFetcher:
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

    def fetch_distinct_addresses(self):
        query = """
            SELECT LiquidityPoolAddress 
            FROM LiquidityData 
            WHERE liquidity IS NOT NULL 
                AND LiquidityPoolAddress IN (
                    SELECT DISTINCT address 
                    FROM LiquidityPools 
                    WHERE creationTime >= datetime('now', '-1 day')
                AND mainToken_address NOT IN (SELECT mainToken_address from TelegramAleart)
                );
        """
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]

    def extract_liquidity_pool_market(self, liquidity_pool_address):
        response = requests.get(
            f'https://public-api.dextools.io/trial/v2/pool/ether/{liquidity_pool_address}/price',
            headers=self.headers,
        )
        if response.status_code == 200:
            return response.json()['data']
        else:
            print(f'LiquidityPoolAddress: {liquidity_pool_address}, status code: {response.status_code}')
            return None

    def insert_marketdata(self, market_data, liquidity_pool_address):
        if market_data:
            columns = ', '.join([*market_data.keys(), 'LiquidityPoolAddress'])
            values = ', '.join(['COALESCE(?, NULL)' for _ in market_data]+ ['?'])
            insert_statement = f"""
            REPLACE INTO MarketData ({columns})
            VALUES ({values})
            """
            self.cursor.execute(insert_statement, [*market_data.values(), liquidity_pool_address])
            self.connection.commit()
            print(f'Inserted marketdata: {liquidity_pool_address}')

    def fetch_and_insert_prices(self):
        distinct_addresses = self.fetch_distinct_addresses()
        for liquidity_pool_address in distinct_addresses:
            market_data = self.extract_liquidity_pool_market(liquidity_pool_address)
            self.insert_marketdata(market_data, liquidity_pool_address)
            time.sleep(1)

    def run(self):
        while True:
            self.fetch_and_insert_prices()
            print(f"Waiting for {self.delay} seconds before next update...")
            time.sleep(self.delay)

# usage:
if __name__ == "__main__":
    price_fetcher = MarketDataFetcher(delay=10)  # Set delay to x seconds
    price_fetcher.run()
