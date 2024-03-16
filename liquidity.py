import dotenv
import os
import requests
import sqlite3
import time

class LiquidityInfoRetriever:
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
            SELECT DISTINCT address 
            FROM LiquidityPools 
            WHERE creationTime >= datetime('now', '-1 day')
            AND mainToken_address NOT IN (SELECT mainToken_address from TelegramAleart);
        """
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]

    def extract_liquidity_info(self, liquidity_pool_address):
        url = f'https://public-api.dextools.io/trial/v2/pool/ether/{liquidity_pool_address}/liquidity'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            liquidity = response.json()['data']['liquidity']
            self.cursor.execute("""
                REPLACE INTO LiquidityData (LiquidityPoolAddress, liquidity) 
                VALUES (?, ?)
            """, (liquidity_pool_address, liquidity))
            self.connection.commit()
            print(f'LiquidityPoolAddress: {liquidity_pool_address}, liquidity: {liquidity}')
        else:
            print(f'LiquidityPoolAddress: {liquidity_pool_address}, status code: {response.status_code}')

    def retrieve_liquidity_information(self):
        distinct_addresses = self.fetch_distinct_addresses()
        for liquidity_pool_address in distinct_addresses:
            self.extract_liquidity_info(liquidity_pool_address)
            time.sleep(1)

    def run(self):
        while True:
            self.retrieve_liquidity_information()
            print(f"Waiting for {self.delay} seconds before next update...")
            time.sleep(self.delay)

# usage:
if __name__ == "__main__":
    liquidity_retriever = LiquidityInfoRetriever(delay=10)  # Set delay to x seconds)
    liquidity_retriever.run()
