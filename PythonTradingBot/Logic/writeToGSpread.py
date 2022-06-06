import gspread
import time
from gspread_formatting import *
##Connects to google service account, accessing google spreadsheet
sa = gspread.service_account(filename = "./../Documentation/tradingbot-350817-6fc7fddd3359.json") ######************ THIS IS DIFFERNET HERE VS AWS SERVER. In LOCAL COMPUTER FUNCTION CALL SHOULD BE EMPTYservice_account(filename = "tradingbot-350817-6fc7fddd3359.json")
sh = sa.open("Tradeing_Bot_Data")
worksheet = sh.worksheet("Sheet1")

##Finds the next avaliable row in the sheets
def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list)+1)

#insert passed data into first empty row in sheets
def logDataToSheets(isBuy, orderPrice, orderTime):
	print("Logging Data to Sheets: {}, {}, {} " .format(isBuy, orderPrice, orderTime) )
	next_row = next_available_row(worksheet)

	orderProfit = "-"
	orderType = "Sell"
	if isBuy:
		orderType = "Buy"
	else:
		orderProfit = getProfit(next_row, orderPrice)

	worksheet.update_acell("A{}".format(next_row), orderType)
	worksheet.update_acell("B{}".format(next_row), orderPrice)
	worksheet.update_acell("C{}".format(next_row), orderProfit)
	worksheet.update_acell("D{}".format(next_row), orderTime)
	format(next_row, isBuy)
	print("Data Logged")


##Calculates the percent change of given trade
def getProfit(nextRow, orderPrice):
	row = int(nextRow)
	price = int(orderPrice)
	prevRow = (row - 1)
	prevCell = "B" + str(prevRow) 
	preVal = worksheet.acell(prevCell).value

	''.join(filter(str.isdigit, preVal))
	#print(preVal)
	prevValStr = preVal.replace("$", "").replace(",", "")
	prevPrice = float(prevValStr)
	percentChange = ((price - prevPrice)/prevPrice) * 100
	return str(percentChange) + "%"



def format(row, buy):
	regFormat = cellFormat(
	backgroundColor=color(.21, .23, .27),
    textFormat=textFormat(foregroundColor=color(1, 1, 1),fontFamily='Avenir',bold=False, fontSize=14),
    horizontalAlignment='CENTER',
    verticalAlignment='MIDDLE'
    )

	sellFormat = cellFormat(
	backgroundColor=color(.92, 0.26, 0.21),
    textFormat=textFormat(foregroundColor=color(1, 1, 1),fontFamily='Avenir',bold=False, fontSize=14),
    horizontalAlignment='CENTER',
    verticalAlignment='MIDDLE'
    )

	buyFormat = cellFormat(
	backgroundColor=color(.20, .66, .33),
    textFormat=textFormat(foregroundColor=color(1, 1, 1),fontFamily='Avenir',bold=False, fontSize=14),
    horizontalAlignment='CENTER',
    verticalAlignment='MIDDLE'
    )

	rowA = 'A' + str(row) 
	rowBC = "B" + str(row) + ":D" + str(row)
	# print(rowA)
	# print(rowBC)

	if buy:
		format_cell_range(worksheet, rowA, buyFormat)
	else:
		format_cell_range(worksheet, rowA, sellFormat)

	format_cell_range(worksheet, rowBC, regFormat)


##Returns true if current action is buy
## Returns false if current action is sell
def getNextOrderType():
	isBuy = True
	nextRow = next_available_row(worksheet)
	currRow = int(nextRow) - 1
	currCell = "A" + str(currRow) 
	currAction = worksheet.acell(currCell).value
	if currAction[0] == 'S':
		return True		
	else:
		return False


#time.sleep(20)
#getNextOrderType()
# time.sleep(60)
#logDataToSheets(False, "1781", "04/06/2022 10:38:00")
# time.sleep(120)
# logDataToSheets(False, "3000", "ya mums a hoe")

