#-----------------------------------------------------------------------------------------------------------------------
# imports
#-----------------------------------------------------------------------------------------------------------------------
import json
import pyotp
import csv
from datetime import datetime
import robin_stocks.robinhood as robin # dir(robin)

#-----------------------------------------------------------------------------------------------------------------------
# functions
#-----------------------------------------------------------------------------------------------------------------------
def getJsonLoad(fileName): # get json loads
    with open(fileName) as f:
        data = json.load(f)
    return data

def getMfaCode(authKey): # get current mfa code
    return pyotp.TOTP(authKey).now()

def listDictToCsv(fileName, listDict): # write list of dictionaries to csv file
    keys = listDict[0].keys()
    with open(fileName, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(listDict)

def makeFileNameTimestamp(fileName, fileExtension):  # make a file name with timestamp
    date_time = datetime.now()
    return fileName.lower() + "-" + date_time.strftime("%Y%m%d") + "-" + date_time.strftime("%H%M%S") + fileExtension

#-----------------------------------------------------------------------------------------------------------------------
# robinhood - new session
#-----------------------------------------------------------------------------------------------------------------------
# get credentials
credsPath = "creds/robinhood.json"
creds = getJsonLoad(credsPath)

# login
login = robin.login(creds["username"], creds["password"], mfa_code=getMfaCode(creds["auth_key"]))

#-----------------------------------------------------------------------------------------------------------------------
# cryptocurrency
#-----------------------------------------------------------------------------------------------------------------------
# setting scope ticker
cryptoSymbol = "BTC"

# getting historicals
cryptoHist = robin.get_crypto_historicals(cryptoSymbol, interval='10minute', span='week', bounds='24_7', info=None)

# save historicals to csv file
csvFileName = makeFileNameTimestamp(cryptoSymbol, ".csv")
listDictToCsv(csvFileName, cryptoHist)

#-----------------------------------------------------------------------------------------------------------------------
# equity
#-----------------------------------------------------------------------------------------------------------------------
# setting scope ticker
equitySymbol = "SENS"

# getting historicals
equityHist = robin.get_stock_historicals(equitySymbol, interval='hour', span='3month', bounds='regular', info=None)

# save historicals to csv file
csvFileName = makeFileNameTimestamp(equitySymbol, ".csv")
listDictToCsv(csvFileName, equityHist)

#-----------------------------------------------------------------------------------------------------------------------
# robinhood - end session
#-----------------------------------------------------------------------------------------------------------------------
# logout
robin.logout



