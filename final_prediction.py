import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from datetime import datetime

################################ Take forecast date from user and error handeling ###################################

def predictdate(stock_file):
    try:
        X_Predict = datetime.strptime(input("Enter the date for close price prediction in YYYY-MM-DD:") ,'%Y-%m-%d')
        X_Predict = (X_Predict.strftime("%Y-%m-%d"))
    except ValueError:
        print("Enter the date in correct format YYYY-MM-DD\n")
        predictdate(stock_file)
    else:
        today = datetime.now()
        today = (today.strftime("%Y-%m-%d"))
        if X_Predict != 0:
            predict(X_Predict,stock_file)
        else:
            print("Please enter correct date\n")
            predictdate(stock_file)

################################ Checking the training period (should be less than 100) ###################################

def checktrain_size():
    while True:
        try:
            train_size = int(input ("Enter the training period (1-99):"))       # Take input from the user
        except ValueError:
            print ("\nEnter correct training period between 1-99")             # error handeling
        else:
            if 1 <= train_size < 100:
                return train_size
            else:
                print("\nEnter correct training period between 1-99")

def predict(X_Predict,stock_file):
    stock_file = stock_file.sort_values(by=['Date'], ascending=[True])          # sort with Date
    stock_file.set_index('Date', inplace=True)                                  # Reset index (to include saturday and sundays in the data)
    stock_file = stock_file.resample('D').ffill().reset_index()                 # Treating missing values (sat, sun) by placing fridays value
    train_size = checktrain_size()
    ts = train_size/100
    X_Predict = pd.to_datetime(X_Predict)                                       # Date to be Predicted
    X_pred_date = (X_Predict - max(stock_file['Date']))
    X_pred_date = (X_pred_date / np.timedelta64(1, 'D')).astype(int)
    stock_file['Date'] = (stock_file['Date'] - stock_file['Date'].min()) / np.timedelta64(1,'D')    # convert to float
    X = stock_file[['Date']]
    y = stock_file['Close']
    X_train, X_test, y_train, y_test = train_test_split(X,y,train_size=ts,random_state = 1)  # splitting data into training and testing
    linreg = LinearRegression()                                                              # Regression model
    linreg.fit(X_train, y_train)                                                             # Fitting the model
    y_pred = linreg.predict(X_test)
    print("Mean squared error: %.2f" % mean_squared_error(y_test,y_pred))
    print("R Square Value    : %.2f" % r2_score(y_test,y_pred))
    plt.scatter(X,y)
    plt.plot(X_test,y_pred,'r')
    plt.xlabel('Date')
    plt.ylabel('Closing Price')
    plt.title('Linear Regression Model')
    final_date = int(max(stock_file['Date']))
    X_pred = (final_date + X_pred_date)
    x_pred = linreg.predict(X_pred)                                                         # Predict future values
    print ("The Stock Prediction Value for", X_Predict," is:", x_pred)
    plt.show()                                                                               # Plotting regression model
