from socket import socket
import ssl
import websocket, json, pprint, talib, numpy 
import config
from binance.client import Client 
from binance.enums import *


## Indicator and trade information information
RSI_PERIOD = 14					# number of closes to make rsi calculation over
RSI_OVERBOUGHT = 70				
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ETHUSDT' 		# Ethereum
TRADE_QUANTITY = 0.0025 		# ~$2
SOCKET = 'wss://stream.binance.com:9443/ws/ethusdt@kline_1m' 

##Global vars
closes = []
readyToBuy = True
client = Client(config.API_KEY, config.API_SECRET, tld='us')


## Order logic
## Executes the orders from binance
def order(side, quantity, symbol, order_type):
	try:
		print("Sending order")
		order = client.create_order(
		symbol = symbol,
		side = side,
		type = ORDER_TYPE_MARKET,
		quantity = quantity
		)
	except Exception as e:
		return False

	return True


## Inital open and closing end function
def on_open(ws):
	print('opened connection')
def on_close(ws):
	print('closed connection')


# Message recieved from websocket
# Full candle stick data, and logic to decide if there should be a buy/sell action
def on_message(ws, message):
	global closes, in_position
	print('received message')

	json_message = json.loads(message)											##The full Json message
	#pprint.pprint(json_message)

	candle = json_message['k']													# Parses the json data to just get the candle stick data
	is_candle_closed = candle['x']												# Checks if this is the last data point in this candle aka the actual close of the candle (used for our rsi)
	closePrice = candle['c']													# The price at close
	# print(candle)
	print(is_candle_closed)

	#If the candle is closed, append its result to list of closing candles
	if is_candle_closed:
		print("candle closed at {}" .format(closePrice))
		closes.append(float(closePrice))
		print(closes)

		## Make sure there has been at RSI period number of closes recorded
		if len(closes) > RSI_PERIOD:
			##	Numpy trading functions to get technical indicator data such as RSI
			np_closes = numpy.array(closes)
			rsi = talib.RSI(np_closes, RSI_PERIOD)

			last_rsi = rsi[-1]													# Negitive index, starts from the end and gets last rsi value added
			print("last RIS = " + last_rsi)

			##### SELL condition #####
			## lastRSI mujst be greater than our over bought flag
			## ReadyToBuy must be false, indicating that our last order was a buy and the next one should be a sell
			if last_rsi > RSI_OVERBOUGHT and readyToBuy == False:
				#Binance sell order logic
				print("Sell!")
				order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)

				if order_succeeded:
					readyToBuy = True
				else:
					print("Order failed")
				

			##### Buy condition #####
			## lastRSI mujst be less than our OverSold flag
			## ReadyToBuy must be True, indicating that our last order was a sell and the next one should be a buy
			if last_rsi < RSI_OVERSOLD and readyToBuy == True:
				#Binance buy order logic here
				print("Buy!")
				order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
				if order_succeeded:
					readyToBuy = False
				else:
					print("Order failed")

ws = websocket.WebSocketApp('wss://stream.binance.com:9443/ws/ethusdt@kline_1h', on_open = on_open, on_close = on_close, on_message = on_message)
ws.run_forever()
