from socket import socket
import ssl
import websocket, json, pprint, talib, numpy 
import config 
from binance.client import Client 
from binance.enums import *
import writeToGSpread
from datetime import datetime


## Indicator and trade information information
RSI_PERIOD = 14					# number of closes to make rsi calculation over
RSI_OVERBOUGHT = 70				
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ETHUSD' 		# Ethereum
TRADE_QUANTITY = 0.009 		# ~$2
SOCKET = 'wss://stream.binance.com:9443/ws/ethusdt@kline_5m' 

##Global vars
closes = []
readyToBuy = writeToGSpread.getNextOrderType()
client = Client(config.API_KEY, config.API_SECRET, tld='us')


## Order logic
## Executes the orders from binance
def order(side, quantity, symbol, close_price, isBuy, order_type=ORDER_TYPE_MARKET):
	try:
		print("Sending order")
		order = client.create_order(
		symbol = symbol,
		side = side,
		type = ORDER_TYPE_MARKET,
		quantity = quantity
		)
	except Exception as e:
		print("Transaction Failed")
		print(e)
		return False

	print("Transaction Succeedeed")
	logToSheets(isBuy, close_price)
	return True

## Writes the transaction to google spreadsheets
def logToSheets(isBuy, close_price):
	now = datetime.now()
	dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
	writeToGSpread.logDataToSheets(isBuy, str(close_price), dt_string)


def getCurrentTime():
	now = datetime.now()
	dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
	return dt_string


## Inital open and closing end function
def on_open(ws):
	print('opened connection with: readyToBuy = {}' .format(readyToBuy))

def on_close(ws):
	print('closed connection')


# Message recieved from websocket
# Full candle stick data, and logic to decide if there should be a buy/sell action
def on_message(ws, message):
	global closes, readyToBuy
	json_message = json.loads(message)											##The full Json message
	#pprint.pprint(json_message)
	candle = json_message['k']													# Parses the json data to just get the candle stick data
	is_candle_closed = candle['x']												# Checks if this is the last data point in this candle aka the actual close of the candle (used for our rsi)
	closePrice = candle['c']													# The price at close
	#print(candle)
	##print(is_candle_closed)
	

	#If the candle is closed, append its result to list of closing candles
	if is_candle_closed:																#print("candle closed at {}" .format(closePrice))
		closes.append(float(closePrice))
																				#print(closes)
		## Make sure there has been at RSI period number of closes recorded
		if len(closes) > RSI_PERIOD:
			##	Numpy trading functions to get technical indicator data such as RSI
			np_closes = numpy.array(closes)
			rsi = talib.RSI(np_closes, RSI_PERIOD)
			last_rsi = rsi[-1]													# Negitive index, starts from the end and gets last rsi value added
			print(last_rsi)

			##### SELL condition #####
			## lastRSI mujst be greater than our over bought flag
			## ReadyToBuy must be false, indicating that our last order was a buy and the next one should be a sell
			if last_rsi > RSI_OVERBOUGHT: 
				if readyToBuy == False:
					#Binance sell order logic
					print("Sell condition met:")
					print(last_rsi)
					print(closePrice)
					isBuy = False
					order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL, closePrice, isBuy)
					if order_succeeded:
						print("Order Success")
						readyToBuy = True
					else:
						print("Order failed")
						time = getCurrentTime()
						print(time)
				
			##### Buy condition #####
			## lastRSI mujst be less than our OverSold flag
			## ReadyToBuy must be True, indicating that our last order was a sell and the next one should be a buy
			if last_rsi < RSI_OVERSOLD: 
				if readyToBuy:
					#Binance buy order logic here
					print("Buy condition met: ")
					print(last_rsi)
					print(closePrice)
					isBuy = True
					order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL, closePrice, isBuy)
					if order_succeeded:
						print("Order Success")
						readyToBuy = False
					else:
						print("Order failed")
						time = getCurrentTime()
						print(time)


# info = client.get_symbol_info('ETHUSDT')
ws = websocket.WebSocketApp(SOCKET, on_open = on_open, on_close = on_close, on_message = on_message)
ws.run_forever()
