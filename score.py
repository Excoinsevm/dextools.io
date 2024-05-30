import dotenv
import os
import requests
import sqlite3
import time

class TokeScoreInfoRetriever:
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
            SELECT chainId,baseToken_address
            FROM dexscreener_pairs 
            WHERE pairCreatedAt_dt >= datetime('now', '-1 day')
            AND baseToken_address NOT IN (SELECT baseToken_address from TokenScore);
        """
        self.cursor.execute(query)
        return [row for row in self.cursor.fetchall()]

    def extract_tokenscore_info(self, chain,baseToken_address):
        if 'eth' in chain:
            chain='ether'
        url = f'https://public-api.dextools.io/standard/v2/token/{chain}/{baseToken_address}/score'
        response = requests.get(url, headers=self.headers)
        #print(url,response.text)
        if response.status_code == 200:
            dextScore = response.json()['data']['dextScore']['total']
            self.cursor.execute("""
                REPLACE INTO TokenScore (baseToken_address, dextScore) 
                VALUES (?, ?)
            """, (baseToken_address, dextScore))
            self.connection.commit()
            print(f'baseToken_address: {baseToken_address}, dextScore: {dextScore}')
        else:
            print(f'baseToken_address: {baseToken_address}, status code: {response.status_code}')

    def retrieve_tokenscore_information(self):
        distinct_addresses = self.fetch_distinct_addresses()
        for chain,baseToken_address in distinct_addresses:
            self.extract_tokenscore_info(chain,baseToken_address)
            time.sleep(1)

    def run(self):
        while True:
            self.retrieve_tokenscore_information()
            print(f"Waiting for {self.delay} seconds before next update...")
            time.sleep(self.delay)

# usage:
if __name__ == "__main__":
    tokenscore_retriever = TokeScoreInfoRetriever(delay=10)  # Set delay to x seconds)
    tokenscore_retriever.run()
