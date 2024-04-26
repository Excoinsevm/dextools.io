import logging
import re
import sqlite3
import json

from mitmproxy import http

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

def websocket_message(flow: http.HTTPFlow):
    assert flow.websocket is not None  # make type checker happy
    # get the latest message
    message = flow.websocket.messages[-1]

    # was the message sent from the client or server?
    if message.from_client:
        #logging.info(f"Client sent a message: {message.content!r}")
        None
    else:
        #logging.info(f"Server sent a message: {message.content!r}")
        data=json.loads(message.text)
        pairs=data['pairs']
        for pair in pairs:
            baseToken=pair['baseToken']
            chainId=pair['chainId']
            dexId=pair['dexId']
            liquidity=pair['liquidity']
            marketCap=pair['marketCap']
            pairAddress=pair['pairAddress']
            pairCreatedAt=pair['pairCreatedAt']
            priceUsd=pair['priceUsd']
            quoteToken=pair['quoteToken']
            txns=pair['txns']
            volume=pair['volume']
            cursor.execute("""
                REPLACE INTO DexScreener_L1 (baseToken,chainId,dexId,liquidity,marketCap,pairAddress,pairCreatedAt,priceUsd,quoteToken,txns,volume)
                VALUES (?, ?,?, ?,?, ?,?, ?,?, ?,?)
            """, (json.dumps(baseToken),chainId,dexId,json.dumps(liquidity),marketCap,pairAddress,pairCreatedAt,priceUsd,json.dumps(quoteToken),json.dumps(txns),json.dumps(volume)) )
            connection.commit()
            print(pairAddress)