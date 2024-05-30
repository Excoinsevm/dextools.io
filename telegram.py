import os
import sqlite3
from datetime import datetime
import requests
from urllib.parse import quote_plus
import config
import time
import dotenv
from gsheet import GoogleSheetDownloader

# gsheet details
gsheet_credentials_path = 'gsheet.json'
sheetname = config.sheetname
worksheetname = config.worksheetname

# Open the file in read mode
# with open("filter.txt", "r") as my_file:
#     data = my_file.read()
# # Split the text when newline ('\\n') is encountered
# input_filter=  data.split("\n")

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
        send_text = f'https://api.telegram.org/bot{self.TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={self.TELEGRAM_CHATID}&text={encoded_message}'
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
        print('Doing first run....')
        self.fetch_and_notify(first_run=1)
        while True:
            self.fetch_and_notify()
            print(f"Waiting for {self.delay_seconds} seconds before next notification...")
            time.sleep(self.delay_seconds)

    # def fetch_and_notify(self):
    #     query = f"""
    #         SELECT *
    #         FROM view1
    #         WHERE liquidity >= {config.liquidity}
    #         AND volume1h >= {config.volume1h}
    #         AND fdv >= {config.marketcap}
    #         AND mainToken_address NOT IN (SELECT mainToken_address from TelegramAleart)
    #     """
    #     self.cursor.execute(query)
    #     results = self.cursor.fetchall()
    #     column_names = [description[0] for description in self.cursor.description]
    #     for row in results:
    #         data = {column_names[i]: row[i] for i in range(len(column_names))}
    #         chain = data['chain']
    #         mainToken_symbol = data['mainToken_symbol']
    #         mainToken_address = data['mainToken_address']
    #         exchange_name = data['exchange_name']
    #         sideToken_symbol = data['sideToken_symbol']
    #         liquidity = round(data['liquidity'], 2)
    #         try:
    #             volume6h = round(data['volume6h'], 2)
    #         except:
    #             volume6h = round(data['volume1h'], 2)
    #         try:
    #             volume24h = round(data['volume24h'], 2)
    #         except:
    #             volume24h=volume6h
    #         transactions = round(data['transactions'], 2)
    #         marketcap = round(data['fdv'], 2)
    #         messageList = [
    #             f'chain : {chain}',
    #             f'mainToken_symbol : {mainToken_symbol}',
    #             f'mainToken_address : {mainToken_address}',
    #             f'exchange_name : {exchange_name}',
    #             f'sideToken_symbol : {sideToken_symbol}',
    #             f'liquidity : {"{:,}".format(liquidity)}',
    #             f'volume24h : {"{:,}".format(volume24h)}',
    #             f'volume6h : {"{:,}".format(volume6h)}',
    #             #f'transactions : {"{:,}".format(transactions)}',
    #             f'marketcap : {"{:,}".format(marketcap)}'
    #         ]
    #         self.telegram_bot_sendtext('\n'.join(str(s) for s in messageList))
    #         self.save_notification_address(mainToken_address)

    def fetch_and_notify(self,first_run=None):
        query = f"""
            SELECT *
            FROM dexscreener_pairs
            left JOIN TokenScore on 
	        dexscreener_pairs.baseToken_address=TokenScore.baseToken_address
            WHERE liquidity_usd >= {config.liquidity}
            AND volume_h24 >= {config.volume_h24}
            AND marketCap >= {config.marketcap}
            AND dexscreener_pairs.baseToken_address NOT IN (SELECT mainToken_address from TelegramAleart)
            AND dextScore>={config.dextScore}
        """
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        column_names = [description[0] for description in self.cursor.description]
        if results:
            input_filter = downloader.download_sheet(sheetname, worksheetname)
        for row in results:
            data = {column_names[i]: row[i] for i in range(len(column_names))}
            chain = data['chainId']
            mainToken_symbol = data['baseToken_symbol'].strip()
            mainToken_address = data['baseToken_address'].strip()
            maintoken_link=f'https://dexscreener.com/{chain}/{mainToken_address}'
            twitter_link=f'https://twitter.com/search?q=%24{mainToken_symbol}'
            if 'eth' in chain:
                tokensniffer_link=f'https://tokensniffer.com/token/eth/{mainToken_address}'
            else:
                tokensniffer_link=f'https://tokensniffer.com/token/{chain}/{mainToken_address}'
            dextScore=data['dextScore']
            exchange_name = data['dexId']
            sideToken_symbol = data['quoteToken_symbol']
            liquidity = round(data['liquidity_usd'], 2)
            volume24h=round(data['volume_h24'], 2)
            marketcap = round(data['marketCap'], 2)
            messageList = [
                f'chain : {chain}',
                f'mainToken_symbol : {mainToken_symbol}',
                f'mainToken_address : {mainToken_address}',
                f'maintoken_link : {maintoken_link}',
                f'tokensniffer_link : {tokensniffer_link}',
                f'dextScore : {dextScore}',
                f'twitter_link : {twitter_link}',
                f'exchange_name : {exchange_name}',
                f'sideToken_symbol : {sideToken_symbol}',
                f'liquidity : {"{:,}".format(liquidity)}',
                f'volume24h : {"{:,}".format(volume24h)}',
                f'marketcap : {"{:,}".format(marketcap)}'
            ]
            if first_run:
                pass
            else:
                if not any(mainToken_symbol.upper() in x for x in input_filter):
                    print(mainToken_symbol) 
                    self.telegram_bot_sendtext('\n'.join(str(s) for s in messageList))
            self.save_notification_address(mainToken_address)

if __name__ == "__main__":
    delay_seconds = 10  # Set delay to x seconds
    downloader = GoogleSheetDownloader(gsheet_credentials_path)
    notifier = TelegramNotifier(delay_seconds=delay_seconds)
    notifier.fetch_and_notify_loop()
