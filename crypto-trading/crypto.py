#-----------------------------------------------------------------------------------------------------------------------
# imports
#-----------------------------------------------------------------------------------------------------------------------
import time
import dateparser
import pytz
import json
import talib
from datetime import datetime
from binance.client import Client
import pandas as pd
import numpy
from numpy import loadtxt
from keras.models import Sequential
from keras.layers import Dense

#-----------------------------------------------------------------------------------------------------------------------
# functions
#-----------------------------------------------------------------------------------------------------------------------
def date_to_milliseconds(date_str): # date to milliseconds
    """Convert UTC date to milliseconds
    If using offset strings add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"
    See dateparse docs for formats http://dateparser.readthedocs.io/en/latest/
    :param date_str: date in readable format, i.e. "January 01, 2018", "11 hours ago UTC", "now UTC"
    :type date_str: str
    """
    # get epoch value in UTC
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    # parse our date string
    d = dateparser.parse(date_str)
    # if the date is not timezone aware apply UTC timezone
    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=pytz.utc)

    # return the difference in time
    return int((d - epoch).total_seconds() * 1000.0)


def interval_to_milliseconds(interval): # interval to milliseconds
    """Convert a Binance interval string to milliseconds
    :param interval: Binance interval string 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w
    :type interval: str
    :return:
         None if unit not one of m, h, d or w
         None if string not in correct format
         int value of interval in milliseconds
    """
    ms = None
    seconds_per_unit = {
        "m": 60,
        "h": 60 * 60,
        "d": 24 * 60 * 60,
        "w": 7 * 24 * 60 * 60
    }

    unit = interval[-1]
    if unit in seconds_per_unit:
        try:
            ms = int(interval[:-1]) * seconds_per_unit[unit] * 1000
        except ValueError:
            pass
    return ms


def get_historical_klines(symbol, interval, start_str, end_str=None):
    """Get Historical Klines from Binance
    See dateparse docs for valid start and end string formats http://dateparser.readthedocs.io/en/latest/
    If using offset strings for dates add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"
    :param symbol: Name of symbol pair e.g BNBBTC
    :type symbol: str
    :param interval: Biannce Kline interval
    :type interval: str
    :param start_str: Start date string in UTC format
    :type start_str: str
    :param end_str: optional - end date string in UTC format
    :type end_str: str
    :return: list of OHLCV values
    """
    # create the Binance client, no need for api key
    client = Client("", "")

    # init our list
    output_data = []

    # setup the max limit
    limit = 500

    # convert interval to useful value in seconds
    timeframe = interval_to_milliseconds(interval)

    # convert our date strings to milliseconds
    start_ts = date_to_milliseconds(start_str)

    # if an end time was passed convert it
    end_ts = None
    if end_str:
        end_ts = date_to_milliseconds(end_str)

    idx = 0
    # it can be difficult to know when a symbol was listed on Binance so allow start time to be before list date
    symbol_existed = False
    while True:
        # fetch the klines from start_ts up to max 500 entries or the end_ts if set
        temp_data = client.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
            startTime=start_ts,
            endTime=end_ts
        )

        # handle the case where our start date is before the symbol pair listed on Binance
        if not symbol_existed and len(temp_data):
            symbol_existed = True

        if symbol_existed:
            # append this loops data to our output data
            output_data += temp_data

            # update our start timestamp using the last value in the array and add the interval timeframe
            start_ts = temp_data[len(temp_data) - 1][0] + timeframe
        else:
            # it wasn't listed yet, increment our start date
            start_ts += timeframe

        idx += 1
        # check if we received less than the required limit and exit the loop
        if len(temp_data) < limit:
            # exit the while loop
            break

        # sleep after every 3rd call to be kind to the API
        if idx % 3 == 0:
            time.sleep(1)

    return output_data

#-----------------------------------------------------------------------------------------------------------------------
# dataset
#-----------------------------------------------------------------------------------------------------------------------
# data characteristics
symbol = "ETHUSDT"
start = "1 Nov, 2020"
end = "1 Nov, 2021"
interval = Client.KLINE_INTERVAL_12HOUR  # https://github.com/sammchardy/python-binance/blob/master/binance/client.py

# collect data
klines = get_historical_klines(symbol, interval, start, end)

#-----------------------------------------------------------------------------------------------------------------------
# cleaning
#-----------------------------------------------------------------------------------------------------------------------
"""
    1499040000000,      // Open time
    "0.01634790",       // Open
    "0.80000000",       // High
    "0.01575800",       // Low
    "0.01577100",       // Close
    "148976.11427815",  // Volume
    1499644799999,      // Close time
    "2434.19055334",    // Quote asset volume
    308,                // Number of trades
    "1756.87402397",    // Taker buy base asset volume
    "28.46694368",      // Taker buy quote asset volume
    "17928899.62484339" // Ignore
"""

# klines list to dataframe
df = pd.DataFrame(klines)
print(df.head())

# variable types
df.dtypes # https://www.skytowner.com/explore/converting_column_type_to_float_in_pandas_dataframe

# >>> df[1] = df[1].astype("float")
# >>> df[2] = df[2].astype("float")
# >>> df[3] = df[3].astype("float")
# >>> df[4] = df[4].astype("float")
# >>> df[5] = df[5].astype("float")
# >>> df[7] = df[7].astype("float")
# >>> df[9] = df[9].astype("float")
# >>> df[10] = df[10].astype("float")
# >>> df[11] = df[11].astype("float")

# Add Classification Column
df[12] = 0
df[12] = df[12].astype("int")

# dataframe list to numpy matrix
dataset = df.values
print(dataset.shape) # shape of numpy arr

#-----------------------------------------------------------------------------------------------------------------------
# add classification obervation
#-----------------------------------------------------------------------------------------------------------------------
for i in range(1, dataset.shape[0]):
    if dataset[i, 4] <= dataset[i - 1, 4] : # t is less than or equal to t-1
        dataset[i, 12] = 0
    elif dataset[i, 4] > dataset[i - 1, 4]: # t is greater than
        dataset[i, 12] = 1

print(dataset[:, 12])

#-----------------------------------------------------------------------------------------------------------------------
# model
#-----------------------------------------------------------------------------------------------------------------------
# input variables (X)
iMinDim = 0
iMaxDim = 12
X = dataset[:,0:12] # select the first 8 columns from index 0 to index 7 via the slice 0:8

# output variables (y)
y = dataset[:,12]

# define the keras model
model = Sequential()
model.add(Dense(12, input_dim=12, activation='relu')) # input_dim=12 : number of obervations in x
model.add(Dense(8, activation='relu'))
model.add(Dense(1, activation='sigmoid'))
model

# Compile Keras Model
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# fit the keras model on the dataset
model.fit(X, y, epochs=150, batch_size=10, verbose=0)

# evaluate the keras model
_, accuracy = model.evaluate(X, y, verbose=0)
print('Accuracy: %.2f' % (accuracy*100))

# make class predictions with the model - round predictions
predictions = (model.predict(X) > 0.5).astype(int)
predictions

# summarize the first 5 cases
for i in range(2):
	print('%s => %d (expected %d)' % (X[i].tolist(), predictions[i], y[i]))
