import json
import os
from datetime import datetime

import pandas as pd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import requests

tda_url = 'https://api.tdameritrade.com/v1/marketdata/{ticker}/pricehistory'

load_dotenv()


def get_price_history(ticker):
    url = tda_url.format(ticker=ticker)
    params = {
        'apikey': os.environ['API_KEY']
    }
    response = requests.get(url, params=params)
    resp_json = json.loads(response.content)
    print(json.dumps(resp_json))


def get_price_history(ticker, period_type, period, frequency_type, frequency):
    url = tda_url.format(ticker=ticker)
    params = {
        'apikey': os.environ['API_KEY'],
        'periodType': period_type,
        'period': period,
        'frequencyType': frequency_type,
        'frequency': frequency
    }
    response = requests.get(url, params=params)
    resp_json = json.loads(response.content)

    for each in resp_json['candles']:
        each['datetime'] = datetime.fromtimestamp(int(each['datetime']) / 1000).strftime("%Y-%m-%d")

    with open(ticker + '.json', 'w') as file:
        file.write(json.dumps(resp_json, indent=4, sort_keys=True))
    file.close()


def get_daily_price_history(ticker, number):
    url = tda_url.format(ticker=ticker)
    params = {
        'apikey': os.environ['API_KEY'],
        'periodType': 'month',
        'period': number,
        'frequencyType': 'daily',
        'frequency': 1
    }
    response = requests.get(url, params=params)
    resp_json = json.loads(response.content)
    for each in resp_json['candles']:
        each['datetime'] = datetime.fromtimestamp(int(each['datetime']) / 1000).strftime("%Y-%m-%d")

    return resp_json


def load_json_price_history(ticker, number_of_years):
    if ticker + 'json' not in os.listdir():
        get_price_history(ticker, number_of_years)
    price_dict = json.load(open(ticker + '.json'))
    df = pd.DataFrame(price_dict['candles'])
    df['Date'] = pd.to_datetime(df['datetime'])
    df.set_index('Date', inplace=True)
    df['ma50'] = df['close'].rolling(50).mean()
    df['ma200'] = df['close'].rolling(200).mean()

    plt.figure(figsize=[16, 8])
    plt.style.use('default')
    fig, ax = plt.subplots()

    plt.plot(df['close'], label='data')
    plt.plot(df['ma50'], label='data')
    plt.plot(df['ma200'], label='data')

    ax.grid(True)
    ax.set_ylabel(r'Price [\$]')
    ax.set_title(ticker, loc='left', y=0.85, x=0.02, fontsize='medium')
    for label in ax.get_xticklabels(which='major'):
        label.set(rotation=30, horizontalalignment='right')
    plt.show()


def get_candlestick(ticker, number_of_months):
    prices_dict = get_daily_price_history(ticker, number_of_months)
    df = pd.DataFrame(prices_dict['candles'])
    df['Date'] = pd.to_datetime(df['datetime'])
    df.set_index('Date', inplace=True)

    width = .5
    width2 = .05

    up = df[df.close >= df.open]
    down = df[df.close < df.open]

    col1 = 'green'
    col2 = 'red'

    plt.figure()
    fig, ax = plt.subplots()
    ax.set_title(ticker)
    fig.subplots_adjust(bottom=0.2)

    plt.grid(True)
    plt.bar(up.index, up.close - up.open, width, bottom=up.open, color=col1)
    plt.bar(up.index, up.high - up.close, width2, bottom=up.close, color=col1)
    plt.bar(up.index, up.low - up.open, width2, bottom=up.open, color=col1)

    plt.bar(down.index, down.close - down.open, width, bottom=down.open, color=col2)
    plt.bar(down.index, down.high - down.open, width2, bottom=down.open, color=col2)
    plt.bar(down.index, down.low - down.close, width2, bottom=down.close, color=col2)
    plt.xticks(rotation=45, ha='right')
    print(df.tail())
    plt.show()


def get_volume(ticker, number_of_months):
    prices_dict = get_daily_price_history(ticker, number_of_months)
    df = pd.DataFrame(prices_dict['candles'])
    df['Date'] = pd.to_datetime(df['datetime'])
    df.set_index('Date', inplace=True)

    plt.figure()
    fig, ax = plt.subplots()
    ax.set_title(ticker)
    fig.subplots_adjust(bottom=0.2)
    plt.plot(df['volume'], label='data')
    ax.set_ylabel(r'Volume')
    for label in ax.get_xticklabels(which='major'):
        label.set(rotation=30, horizontalalignment='right')
    plt.show()


def get_volume_and_averages(ticker, period_type, period, frequency_type, frequency):
    if ticker + 'json' not in os.listdir():
        get_price_history(ticker, period_type, period, frequency_type, frequency)
    price_dict = json.load(open(ticker + '.json'))
    df = pd.DataFrame(price_dict['candles'])
    df['Date'] = pd.to_datetime(df['datetime'])
    df.set_index(df['Date'])

    # Create a new column in dataframe and populate with bar color
    i = 0
    while i < len(df):
        if df.iloc[i]['close'] >= df.iloc[i]['open']:
            df.at[i, 'color'] = "green"
        elif df.iloc[i]['close'] < df.iloc[i]['open']:
            df.at[i, 'color'] = "red"
        else:
            df.at[i, 'color'] = "blue"
        i += 1

    # Set up the chart
    plt.figure(figsize=[16, 8])
    plt.style.use('default')
    figure, axis = plt.subplots(2)
    figure.suptitle(ticker)

    # Draw the price history
    axis[0].plot(df['Date'], df['close'])
    axis[0].axes.get_xaxis().set_visible(False)  # Remove X labels

    # Draw the volume
    axis[1].bar(df['Date'], df['volume'], color=df['color'])

    # Tweak chart to display better
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.2)
    plt.show()


def main():
    get_volume_and_averages('TSLA', 'month', 3, 'daily', 1)


if __name__ == "__main__":
    main()
