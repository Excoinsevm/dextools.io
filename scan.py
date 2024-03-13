import dotenv
import os
import requests
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

dotenv.load_dotenv()
API_KEY = os.getenv('API_KEY')

headers = {
    'accept': 'application/json',
    'x-api-key': '',
}
headers['x-api-key']=API_KEY

params = {
    'sort': 'creationTime',
    'order': 'desc',
    'from': '2024-03-13T00:00:00.000Z',
    'to': '2024-03-13T23:00:00.000Z',
    'pageSize':50,
}



response = requests.get('https://public-api.dextools.io/trial/v2/pool/ether', params=params, headers=headers)
if response.status_code==200:
    response=response.json()
    data=response['data']['results']

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
cursor.execute("""
    INSERT INTO tokens (
        mainToken_name, mainToken_symbol, mainToken_address,
        exchange_name, exchange_factory, address,
        sideToken_name, sideToken_symbol, sideToken_address,
        creationTime
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    main_token_name, main_token_symbol, main_token_address,
    exchange_name, exchange_factory, address,
    side_token_name, side_token_symbol, side_token_address,
    creation_time
))

conn.commit()