from socket import socket
import websocket, json, pprint


TRADE_SYMBOL = 'ETHUSD' 		# Ethereum
SOCKET = 'wss://stream.binance.com:9443/ws/ethusdt@kline_5m' 

def on_open(ws):
    print(ws)
    print("Connection opened")

def on_close(ws):
    print("Connection closed")

def on_message(ws, message):
    print("called")
    json_message = json.loads(message)
    pprint.pprint(json_message)

ws = websocket.WebSocketApp(SOCKET, on_open = on_open, on_close = on_close, on_message = on_message)
ws.run_forever()

