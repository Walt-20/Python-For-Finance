import bs4 as bs
import datetime as dt
import os
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import yfinance as yf
import pickle
import requests
import matplotlib.pyplot as plt

def save_sp500_tickers():
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, "lxml")
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker)
    with open('sp500tickers.pickle','wb') as f:
        pickle.dump(tickers, f)
    print(tickers)
    return tickers

def get_data_yfinance(reload_sp500=False):
    yf.pdr_override()
    if reload_sp500:
        tickers = save_sp500_tickers()
    else:
        with open('sp500tickers.pickle','rb') as f:
            tickers = pickle.load(f)
    if not os.path.exists('stock_dfs_yfinance'):
        os.makedirs('stock_dfs_yfinance')
    for ticker in tickers:
        ticker = ticker.strip()
        print(ticker)
        if not os.path.exists('stock_dfs_yfinance/{}.csv'.format(ticker)):
            df = web.DataReader(ticker, "2000-01-01", "2023-12-31")
            df.to_csv('stock_dfs_yfinance/{}.csv'.format(ticker))
        else:
            print('Already have {}'.format(ticker))

# get_data_yfinance()

def compile_data():
    with open('sp500tickers.pickle','rb') as f:
        tickers = pickle.load(f)
    main_df = pd.DataFrame()
    for count, ticker in enumerate(tickers):
        ticker = ticker.strip()
        df = pd.read_csv('stock_dfs_yfinance/{}.csv'.format(ticker))
        df.set_index('Date', inplace=True)
        df.rename(columns={'Adj Close': ticker}, inplace=True)
        df.drop(['Open', 'High', 'Low', 'Close', 'Volume'], axis=1, inplace=True)
        if main_df.empty:
            main_df = df
        else:
            main_df = main_df.join(df, how='outer')
        if count % 10 == 0:
            print(count)
    print(main_df.head())
    main_df.to_csv('sp500_joined_closes_yfinance.csv')

def visualize_data():
    df = pd.read_csv('sp500_joined_closes_yfinance.csv')
    # df['AAPL'].plot()
    # plt.show()
    df = df.drop('Date', axis=1)
    df_corr = df.corr()

    data = df_corr.values
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    heatmap = ax.pcolor(data, cmap=plt.cm.RdYlGn)
    fig.colorbar(heatmap)
    ax.set_xticks(np.arange(data.shape[0]) + 0.5, minor=False)
    ax.set_yticks(np.arange(data.shape[1]) + 0.5, minor=False)
    ax.invert_yaxis()
    ax.xaxis.tick_top()

    column_labels = df_corr.columns
    row_labels = df_corr.index

    ax.set_xticklabels(column_labels)
    ax.set_yticklabels(row_labels)
    plt.xticks(rotation=90)
    heatmap.set_clim(-1,1)

    plt.tight_layout()
    plt.show()

visualize_data()