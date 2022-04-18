import json
import os
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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


def get_ytd_price_history(ticker):
    url = tda_url.format(ticker=ticker)
    params = {
        'apikey': os.environ['API_KEY'],
        'periodType': 'year',
        'period': 5,
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


def load_json_price_history(ticker):
    if ticker+'json' not in os.listdir():
        get_ytd_price_history(ticker)
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


def main():
    load_json_price_history('MSFT')


if __name__ == "__main__":
    main()
