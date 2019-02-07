import pandas as pd
import numpy as np
import pylab
import os.path, time
from urllib.request import urlretrieve
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick_ohlc
from subprocess import Popen
import sys
import final_prediction as fp
import advanced_stats as ad
import webbrowser


################################ Getting the latest Company list file ###################################

def tickerinput():
    data = pd.read_csv("http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchan0ge=nasdaq&render=download", usecols = [*range(0,7)])
    data = data[~data['Symbol'].astype(str).str.contains('\^')]
    data = data[~data['Symbol'].astype(str).str.contains('\.')] # Removes the ticker symbol whi has special characters
    data = data[~data['Symbol'].astype(str).str.contains('\$')]
    #print(data['Symbol'])
    stock_name = input("Enter the symbol of the company: ")     # Input from the user for Ticker symbol
    stock_name = stock_name.upper()
    company_info = data.loc[data['Symbol'] == stock_name ]      # Check the ticker in NASDAQ company list
    if company_info.empty:                                      # if wrong ticker, go back to main menu
        print("\nPlease enter the correct ticker Symbol")
        mainMenu()
    else:
        company_info.index = range(len(company_info))               # Rearranging the index for the below line of code
        print("\nSummary of the company selected ")
        print("\nName of the Company: ",company_info["Name"][0])    # Access elements such as Name, Market cap, etc from the csv for that company
        print("Market Cap         : ",company_info["MarketCap"][0])
        print("Industry           : ",company_info["industry"][0])
        print("Sector             : ",company_info["Sector"][0])
        pulldata(stock_name)                                        # Call pull data function for a articular stock


################################ Function for Pulling data from google finance ###################################

def pulldata(stock_name):
    # Read data from Google
    url = ("https://finance.google.com/finance/historical?output=csv&q={}".format(stock_name))
    urlretrieve(url, "stock.csv".format(stock_name))                # save it in local for accessing
    stock_file = pd.read_csv("stock.csv".format(stock_name), na_values = ['-'])
######## Missing value treatment
    stock_file = stock_file[np.isfinite(stock_file['Close'])]
    stock_file = stock_file[np.isfinite(stock_file['Open'])]
    stock_file = stock_file[np.isfinite(stock_file['Low'])]
    stock_file = stock_file[np.isfinite(stock_file['High'])]
    stock_file.index = range(len(stock_file))               # Resetting the index if any row removed
    stock_file['Date'] = pd.to_datetime(stock_file['Date']) # Conver Date from object to datetime format
    menu1(stock_file, stock_name)                           # call menu 1.

################################ First menu after the stok selection ###################################

def menu1(stock_file,stock_name):
    print("\n" + "="*30 + "Please Select From Below Option" + "="*27)
    print("\n1. Forecast for {} stock \n2. Statistics of stock for particular time range \n3. Statistics of stock for entire year \n4. OHLC candlestick graph of the selected stock\n5. Go back to main menu ".format(stock_name))
    print("="*88)
    choice = input("\nChoose option: ")
    candle_stick_data = stock_file
    try:
        if choice == "1":
            fp.predictdate(stock_file)                                          # Regression
            menu1(stock_file,stock_name)
        elif choice == "2":
            time_range(stock_file,stock_name)                                   # Selecting a particular time range for statistics
        elif choice == "3":
            print("\nPlease choose the options from below list")
            stats_menu(stock_file,stock_name)                                   # Options for statistics
        elif choice == "4":
            candle_stick(stock_name)                                            # Plot Candle Stick
            menu1(stock_file,stock_name)
        elif choice == "5":
            mainMenu()                                                          # main menu
        else:
            print("===========================================================")
            print("Wrong choice, Please select options 1,2,3 as per requirement")
            print("===========================================================")
            menu1(stock_file,stock_name)
    except ValueError:
        print("Wrong choice, Please try again....\n\n")

################################ Menu for Statistics (Raw time series, trend, basic and advanced) ###################################

def stats_menu(user_selected_data,stock_name):
    print("\n" + "="*30 + "Please Select From Below Option" + "="*27)
    print("\n1. Raw time series Plot \n2. Trend line chart \n3. Basic statistics (mean, variance, quartiles, etc.) \n4. Advanced level statistics (MA, WMA, MACD)? \n5. Go back to previous menu ")
    print("="*88)
    choice = input("\nChoose Option: ")
    try:
        if choice == "1":
            #### Raw Time series Plot
            plt.plot(user_selected_data["Date"],user_selected_data["Close"])
            plt.xlabel('Date')
            plt.ylabel('Closing Price of the stock')
            plt.title('Raw Time Series for closing price')
            plt.show()                                                          # Plot Raw time series
            stats_menu(user_selected_data,stock_name)
        elif choice == "2":
            # Trend Line with the scatter plot
            data = user_selected_data[['Date', 'Close']]
            data['Date'] = pd.to_datetime(data['Date'])
            data['Date'] = (data['Date'] - data['Date'].min()) / np.timedelta64(1,'D')
            x = data['Date']
            y = data['Close']
            pylab.plot(x,y,'o')
            z = np.polyfit(x,y,1)
            p = np.poly1d(z)
            pylab.plot(x,p(x),"r--")
            plt.xlabel('Date')
            plt.ylabel('Closing Price of the stock')
            plt.title('Trend Line for Closing Price')
            plt.show()                                                          # Plot Trend line on scatter plot
            stats_menu(user_selected_data,stock_name)
        elif choice == "3":
            basic_statistics(user_selected_data)                                # basic statistics (mean, median, sd, etc.)
            stats_menu(user_selected_data,stock_name)
        elif choice == "4":
            MA_options(user_selected_data,stock_name)                           # advanced statistics (Simple MA, Exponentil MA, MACD)
            stats_menu(user_selected_data,stock_name)
        elif choice == "5":
            menu1(user_selected_data,stock_name)                                # Previous menu
        else:
            print("===========================================================")
            print("Wrong choice, Please select options 1,2,3 as per requirement")
            print("===========================================================")
            stats_menu(user_selected_data,stock_name)
    except ValueError:
        print("Wrong choice, Please try again....\n\n")

################################ Menu for basic Statistics (Mean, Meadian, Quartiles, Coeff of variation) ###################################

def basic_statistics(stock_file):

    print("=" * 30+" SUMMARY STATISTICS "+"=" * 30)
    print("\t\nBasic Summary stats_menu for Closing Price:")
    print("\t\nMean: ",stock_file["Close"].mean())
    print("\t\nMedian: ",stock_file["Close"].median())
    print("\t\nRange: ",(stock_file["Close"].max() - stock_file["Close"].min()))
    print("\t\nFirst Quartile (25th Percentile) :", stock_file["Close"].quantile(0.25))
    print("\t\nThird Quartile (75th Percentile) :",stock_file["Close"].quantile(0.75))
    print("\t\nStandard deviation : ",np.std(stock_file["Close"]))
    print("\t\nCoefficient of Variation: ",np.std(stock_file["Close"])/stock_file["Close"].mean())

################################ Menu for advanced statistics (Simple MA, Exponential MA and MACD) ###################################

def MA_options(stock_file,stock_name):
    print("\n" + "="*30 + "Please Select From Below Option" + "="*27)
    print("\n1.Simple Moving Average \n2.Exponential Weighted Moving Average \n3.Moving Average Convergence Divergence (MACD)\n4.Go back to previous menu")
    print("="*88)
    choice = input("\nChoose option: ")
    try:
        if choice == "1":
            ad.moving_Avg(stock_file)                                           # Simple MA (in other file)
            MA_options(stock_file,stock_name)
        elif choice == '2':
            ad.WMA(stock_file)
            MA_options(stock_file,stock_name)                                   # Exp MA (in other file)
        elif choice == '3':
            ad.MACD(stock_file)
            MA_options(stock_file,stock_name)                                   # MACD (in other file)
        elif choice == "4":
            stats_menu(stock_file,stock_name)
        else:
            print("===========================================================")
            print("Wrong choice, Please select options 1,2,3 as per requirement")
            print("===========================================================")
            MA_options(stock_file,stock_name)
    except ValueError:
        print("Wrong choice, Please try again....\n\n")
        MA_options(stock_file,stock_name)


################################ Slicing the data as per users requirement based on Dates ###################################

def time_range(stock_file,stock_name):
    print("\nPlease enter the time range for the stock: ")
    try:
        start_date = pd.to_datetime(input("\nEnter the start date in YYYY-MM-DD: ")) # take input from the user and
        end_date = pd.to_datetime(input("\nEnter the end date in YYYY-MM-DD: "))     # convert into datetime format
        stock_file['Date'] = pd.to_datetime(stock_file['Date'])
        user_selected_data = stock_file.loc[(stock_file['Date'] > start_date) & (stock_file['Date'] <= end_date)]  #slice the data
        if user_selected_data.empty:                                                  # If date entered is beyond todays date, ask again
            print("\nThe date entered is not valid. Please enter again")
            time_range(stock_file,stock_name)
        stats_menu(user_selected_data,stock_name)
    except ValueError:
        print("\n###########################################################")
        print("You have entered an incorrect Date range. Please enter again!")
        print("#############################################################")
        time_range(stock_file,stock_name)


################################ Plot OHLC(Open, High, Low, Close) candlestick plot ###################################

def candle_stick(stock_name):
    ## Data separate for candle stick graph
    candle_stick_data = pd.read_csv("https://www.google.com/finance/historical?output=csv&q={}".format(stock_name),na_values = ['-'])
    candle_stick_data = candle_stick_data[np.isfinite(candle_stick_data['Close'])] # Dropping missing values
    candle_stick_data = candle_stick_data[np.isfinite(candle_stick_data['Open'])]  # Dropping missing values
    candle_stick_data = candle_stick_data[np.isfinite(candle_stick_data['Low'])]
    candle_stick_data = candle_stick_data[np.isfinite(candle_stick_data['High'])]
    candle_stick_data.index = range(len(candle_stick_data))                        # Reset index if any value is dropped
    # Preparing x,y plot for candlestick
    ax1 = plt.subplot2grid((1,1),(0,0))
    x = 0
    y = len(candle_stick_data)
    ohlc = []                                                  #### Open, High, Low, Close

    candle_stick_data['Date'] = pd.to_datetime(candle_stick_data['Date'])
    candle_stick_data['Date'] = ((candle_stick_data['Date'] - candle_stick_data['Date'].min())/np.timedelta64(1,'D')) # Convert datetime to floaat
    #### MAke a new sequence of data in ohlc which will be input to candlestick_ohlc function as it does not take values in datetime64 format
    while x<y:
        new_seq = candle_stick_data['Date'][x],candle_stick_data['Open'][x],candle_stick_data['High'][x],candle_stick_data['Low'][x],candle_stick_data['Close'][x],candle_stick_data['Volume'][x]
        ohlc.append(new_seq)
        x += 1
    # plot
    candlestick_ohlc(ax1,ohlc) #Plot OHLC (Open, High, Low, Close)
    plt.xlabel('Date')
    plt.ylabel('Open, High, Low and Close values')
    plt.title('Candle Stick plot ')
    plt.show()

########################################### Prints project information from file ##############################

def project_info():
    for text in open("proj_info.txt"):
        print(text, end = "")
    print("\n")

########################################### Program starts from here ###########################################
################################################################################################################

################################## Main Menu as soon as the Project Runs #############################

def mainMenu():
	print("\n1. Enter the stock ticker symbol\n2. Check the list of companies on NASDAQ \n3. Information about the project\n4. Quit")
	print("="*88)
	choice = input("Please select the option: ")
	try:
		if choice == "1":                                         #ticker input
			tickerinput()                                         # Take ticker input (1st function in the file)
		elif choice == "2":                                       # Print company information
			print("\nGive the list of the companies")
			webbrowser.open_new_tab("http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchan0ge=nasdaq&render") # open NASDAQ search
			mainMenu()
		elif choice == "3":                                       # Open user manual
			print("\nInformation about the project\n")
			project_info()
			print("="*88)
			mainMenu()
		elif choice == "4":                                       # Quit
			print("\nQuit the program")
			quit()
		else:
			print("=========================================================")
			print("Wrong choice, Please select 1,2,3,4 as per requirement")
			print("=========================================================")
			mainMenu()
	except ValueError:
		print("Wrong choice, Please select 1,2,3,4 as per requirement\n\n")

print("-" * 88)
print("--------------------------Welcome to the NASDAQ Financial Market------------------------")
print("-"*88)
mainMenu()
