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


def get_ytd_price_history(ticker, number_of_years):
    url = tda_url.format(ticker=ticker)
    params = {
        'apikey': os.environ['API_KEY'],
        'periodType': 'year',
        'period': number_of_years,
        'frequencyType': 'daily',
        'frequency': 1
    }
    response = requests.get(url, params=params)
    resp_json = json.loads(response.content)

    for each in resp_json['candles']:
        each['datetime'] = datetime.fromtimestamp(int(each['datetime']) / 1000).strftime("%Y-%m-%d")

    with open(ticker+'.json', 'w') as file:
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

    print(resp_json)

    for each in resp_json['candles']:
        each['datetime'] = datetime.fromtimestamp(int(each['datetime']) / 1000).strftime("%Y-%m-%d")

    return resp_json


def load_json_price_history(ticker):
    if ticker+'json' not in os.listdir():
        get_ytd_price_history(ticker, 5)
    price_dict = json.load(open(ticker+'.json'))
    df = pd.DataFrame(price_dict['candles'])
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


def candlestick(ticker, number_of_months):
    prices_dict = get_daily_price_history(ticker, number_of_months)
    df = pd.DataFrame(prices_dict['candles'])

    width = .4
    width2 = .05

    up = df[df.close >= df.open]
    down = df[df.close < df.open]

    col1 = 'green'
    col2 = 'red'

    fig = plt.figure()

    plt.grid(True)
    plt.bar(up.index, up.close - up.open, width, bottom=up.open, color=col1)
    plt.bar(up.index, up.high - up.close, width2, bottom=up.close, color=col1)
    plt.bar(up.index, up.low - up.open, width2, bottom=up.open, color=col1)

    plt.bar(down.index, down.close - down.open, width, bottom=down.open, color=col2)
    plt.bar(down.index, down.high - down.open, width2, bottom=down.open, color=col2)
    plt.bar(down.index, down.low - down.close, width2, bottom=down.close, color=col2)
    plt.xticks(rotation=45, ha='right')

    ax2 = fig.add_axes([0, len(df.datetime), 0, 0])
    ax2.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax2.grid(True)
    ax2.set_xlabel('date')

    plt.show()


def main():
    candlestick('DSNY', 3)


if __name__ == "__main__":
    main()
