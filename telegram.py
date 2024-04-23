import os
import sqlite3
from datetime import datetime
import requests
from urllib.parse import quote_plus
import config
import time
import dotenv

class TelegramNotifier:
    def __init__(self, delay_seconds=10):
        dotenv.load_dotenv()
        self.TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
        self.TELEGRAM_CHATID = os.getenv('TELEGRAM_CHATID')
        self.connection = sqlite3.connect('database.db')
        self.cursor = self.connection.cursor()
        self.delay_seconds = delay_seconds

    def telegram_bot_sendtext(self, bot_message):
        encoded_message = quote_plus(bot_message)
        send_text = f'https://api.telegram.org/bot{self.TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={self.TELEGRAM_CHATID}&parse_mode=Markdown&text={encoded_message}'
        response = requests.get(send_text)
        return response.json()

    def save_notification_address(self, mainToken_address):
        self.cursor.execute(
            """
            INSERT OR IGNORE INTO TelegramAleart (mainToken_address)
            VALUES (?)
            """, 
            (mainToken_address,)
        )
        self.connection.commit()
        print(f'Saved : {mainToken_address}, at {datetime.now()}')

    def fetch_and_notify_loop(self):
        while True:
            self.fetch_and_notify()
            print(f"Waiting for {self.delay_seconds} seconds before next notification...")
            time.sleep(self.delay_seconds)

    def fetch_and_notify(self):
        query = f"""
            SELECT *
            FROM view1
            WHERE liquidity >= {config.liquidity}
            AND volume1h >= {config.volume1h}
            AND fdv >= {config.marketcap}
            AND mainToken_address NOT IN (SELECT mainToken_address from TelegramAleart)
        """
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        column_names = [description[0] for description in self.cursor.description]
        for row in results:
            data = {column_names[i]: row[i] for i in range(len(column_names))}
            chain = data['chain']
            mainToken_symbol = data['mainToken_symbol']
            mainToken_address = data['mainToken_address']
            exchange_name = data['exchange_name']
            sideToken_symbol = data['sideToken_symbol']
            liquidity = round(data['liquidity'], 2)
            try:
                volume6h = round(data['volume6h'], 2)
            except:
                volume6h = round(data['volume1h'], 2)
            try:
                volume24h = round(data['volume24h'], 2)
            except:
                volume24h=volume6h
            transactions = round(data['transactions'], 2)
            marketcap = round(data['fdv'], 2)
            messageList = [
                f'chain : {chain}',
                f'mainToken_symbol : {mainToken_symbol}',
                f'mainToken_address : {mainToken_address}',
                f'exchange_name : {exchange_name}',
                f'sideToken_symbol : {sideToken_symbol}',
                f'liquidity : {"{:,}".format(liquidity)}',
                f'volume24h : {"{:,}".format(volume24h)}',
                f'volume6h : {"{:,}".format(volume6h)}',
                #f'transactions : {"{:,}".format(transactions)}',
                f'marketcap : {"{:,}".format(marketcap)}'
            ]
            self.telegram_bot_sendtext('\n'.join(str(s) for s in messageList))
            self.save_notification_address(mainToken_address)

if __name__ == "__main__":
    delay_seconds = 10  # Set delay to x seconds
    notifier = TelegramNotifier(delay_seconds=delay_seconds)
    notifier.fetch_and_notify_loop()
