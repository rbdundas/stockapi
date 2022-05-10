import json
import os
from pathlib import Path
from datetime import datetime
import psycopg2
from dotenv import load_dotenv
import requests

import StockHistory

tda_url = 'https://api.tdameritrade.com/v1/marketdata/{ticker}/pricehistory'

load_dotenv()


class Ticker(object):
    indicators = []

    def __init__(self, symbol):
        self.symbol = symbol

    def __str__(self):
        return f"Symbol: {self.symbol}, Indicators: {self.indicators}"

    def __repr__(self):
        return f"Symbol: {self.symbol}, Indicators: {self.indicators}"


class Indicator:
    name = ''
    buy = False
    sell = False

    def __init__(self):
        self.data = []

    def __str__(self):
        return f"Name: {self.name}, Buy: {self.buy}, Sell: {self.sell}"

    def __repr__(self):
        return f"Name: {self.name}, Buy: {self.buy}, Sell: {self.sell}"


def get_database_connection():
    conn = psycopg2.connect(
        dbname=os.environ['dbname'],
        user=os.environ['dbusername'],
        password=os.environ['dbpassword']
    )
    return conn


def get_relative_strength_index_indicator(symbol):
    indicator = Indicator()
    indicator.name = 'RSI'
    df = StockHistory.get_price_history(symbol)
    df = StockHistory.get_relative_strength_index(df)
    latest_close = df.iloc[-1]['rsi']

    for i in range(len(df)):
        if df.iloc[i]['rsi'] >= 70:
            df.at[i, 'rsi_overbought'] = df.iloc[i]['rsi']
            df.at[i, 'rsi_oversold'] = 0
        elif df.iloc[i]['rsi'] <= 30:
            df.at[i, 'rsi_oversold'] = df.iloc[i]['rsi']
            df.at[i, 'rsi_overbought'] = 0
        else:
            df.at[i, 'rsi_oversold'] = 0
            df.at[i, 'rsi_overbought'] = 0

        if df.iloc[i]['rsi_overbought'] == 0 and df.iloc[i-1]['rsi_overbought'] > 0:
            df.at[i, 'rsi_sell_indicator'] = True
            df.at[i, 'rsi_buy_indicator'] = False
        elif df.iloc[i]['rsi_oversold'] == 0 and df.iloc[i-1]['rsi_oversold'] > 0:
            df.at[i, 'rsi_buy_indicator'] = True
            df.at[i, 'rsi_sell_indicator'] = False
        else:
            df.at[i, 'rsi_buy_indicator'] = False
            df.at[i, 'rsi_sell_indicator'] = False

    if df.iloc[-1]['rsi_sell_indicator']:
        indicator.sell = True
        indicator.buy = False
    elif df.iloc[-1]['rsi_buy_indicator']:
        indicator.buy = True
        indicator.sell = False

    return indicator


def get_stochastic_oscillator_indicator(symbol):
    indicator = Indicator()
    indicator.name = 'SO'
    df = StockHistory.get_price_history(symbol)
    df = StockHistory.get_stochastic_oscillator(df)

    for i in range(len(df)):
        if df.iloc[i]['fast_k'] >= 70 and df.iloc[i]['fast_d'] >= 70:
            df.at[i, 'so_overbought'] = True
            df.at[i, 'so_oversold'] = False
        elif df.iloc[i]['fast_k'] <= 30 and df.iloc[i]['fast_d'] <= 30:
            df.at[i, 'so_overbought'] = False
            df.at[i, 'so_oversold'] = True
        else:
            df.at[i, 'so_oversold'] = False
            df.at[i, 'so_overbought'] = False

        if df.iloc[i]['so_overbought'] == 0 and df.iloc[i-1]['so_overbought'] > 0:
            df.at[i, 'so_sell_indicator'] = True
            df.at[i, 'so_buy_indicator'] = False
        elif df.iloc[i]['so_oversold'] == 0 and df.iloc[i-1]['so_oversold'] > 0:
            df.at[i, 'so_buy_indicator'] = True
            df.at[i, 'so_sell_indicator'] = False
        else:
            df.at[i, 'so_buy_indicator'] = False
            df.at[i, 'so_sell_indicator'] = False

    if df.iloc[-1]['so_sell_indicator']:
        indicator.sell = True
        indicator.buy = False
    elif df.iloc[-1]['so_buy_indicator']:
        indicator.buy = True
        indicator.sell = False
    # print(df)
    return indicator


def get_moving_averages_indicator(symbol):
    df = StockHistory.get_moving_averages(symbol)
    for i in range(len(df)):
        if df.iloc[i]['ma50'] >= df.iloc[i]['ma200']:
            df.at[i, 'buy_zone'] = True
            df.at[i, 'sell_zone'] = False
        elif df.iloc[i]['ma200'] >= df.iloc[i]['ma50']:
            df.at[i, 'sell_zone'] = True
            df.at[i, 'buy_zone'] = False
        else:
            df.at[i, 'sell_zone'] = False
            df.at[i, 'buy_zone'] = False


    print(df)


def get_indicators(symbols):
    tickers = []

    for symbol in symbols:
        tickers.append(Ticker(symbol))

    for ticker in tickers:
        rsi = get_relative_strength_index_indicator(ticker.symbol)
        so = get_stochastic_oscillator_indicator(ticker.symbol)

        indicators = [rsi, so]
        ticker.indicators = indicators

        print(f"Symbol: {ticker.symbol}")
        for indicator in ticker.indicators:
              print(f"Indicator: {indicator.name}, "
                    f"Buy: {bool(indicator.buy)}, "
                    f"Sell: {bool(indicator.sell)}")


def main():
    get_moving_averages_indicator(['PYPL', 'SHOP'])


if __name__ == "__main__":
    main()
