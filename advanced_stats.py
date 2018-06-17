import pandas as pd
import numpy as np
import os.path, time
from urllib.request import urlretrieve
import datetime as dt
import matplotlib.pyplot as plt

################################ Moving Averages ###################################

def moving_Avg(stock_file):
    try:
        number = int(input("Please enter Moving Average days: "))
        if number <= 200:
            stock_file["numberd"] = np.round(stock_file["Close"].rolling(window = number, center = False).mean(), 2)
            plt.plot(stock_file["numberd"])
            plt.plot(stock_file["Close"])
            plt.xlabel('Date')
            plt.ylabel('Close Price')
            plt.title('Moving Average')
            plt.show()
        else:
            print("\n You have entered a number greater than 200 for moving average calculation, please try following options\n")
            moving_Avg(stock_file)
    except ValueError:
        print("\n You have entered wrong value for calculation, please try following options\n")
        moving_Avg(stock_file)


################################ Exponential weighted moving average ###################################

def WMA(stock_file):
    try:
        number = int(input("Please enter Weighted Moving Average days: "))
        if number <= 200:
            exp_200=stock_file["Close"].ewm(span=number,adjust=False).mean()
            plt.plot(exp_200)
            plt.plot(stock_file["Close"])
            plt.xlabel('Date')
            plt.ylabel('Close Price')
            plt.title('Weighted Moving Average')
            plt.show()
        else:
            print("\n You have entered a number greater than 200 for moving average calculation, please try again....\n")
            WMA(stock_file)
    except ValueError:
        print("\n You have entered wrong value for calculation, please try following options\n")
        WMA(stock_file)

################################ Moving average convergence/divergence ###################################


def MACD(stock_file): # Calcualtes MACD for 10,30 and 60 days. Also based on user input not more than 200 days

    emaslow =stock_file["Close"].ewm(span=26,adjust=False).mean()
    emafast =stock_file["Close"].ewm(span=12,adjust=False).mean()
    MACD = emafast - emaslow
    exp_9=MACD.ewm(span=9,adjust=False).mean()
    plt.plot(MACD, 'r', label='MACD')     #MACD
    plt.plot(exp_9, 'b', label='Signal')  #Signal Line
    plt.legend(loc='upper right')
    plt.xlabel('Date')
    plt.title('MACD')
    plt.show()
