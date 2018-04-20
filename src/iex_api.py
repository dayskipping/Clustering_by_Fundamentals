import requests
import pandas as pd
import numpy as np

'''
https://api.iextrading.com/1.0/stock/market/batch?symbols=aapl,fb,tsla&types=company&filter=sector
'''

X = pd.read_pickle('data/stocks_ratios.pkl')
ticker_list = X.index
endpoint = 'https://api.iextrading.com/1.0/stock/market/batch'

# def _make_payload(ticker_list, X):
#     symbols = ','.join(ticker_list)
#     payload = {'filter':'sector', 'types': 'company', 'symbols':symbols}
#     return payload
#
# def _single_query(endpoint, payload):
#     response = requests.get(endpoint, params=payload)
#     if response.status_code == 200:
#         print('request successful')
#         return response.json()
#     else:
#         print ('WARNING status code {}'.format(response.status_code))
#
# def sector_extractor(ticker_list, response_dict):
#     sector_list = []
#     for ticker in ticker_list:
#         sector_list.append(response_dict[ticker]['company']['sector'])
#     return sector_list

def _single_query(endpoint, payload):
    response = requests.get(endpoint, params=payload)
    if response.status_code == 200:
        print('request successful')
        return response.json()
    else:
        print('Not available')
        return None

def sector_get(ticker_list, endpoint):
    symbol_dict = dict()
    for ticker in ticker_list:
        try:
            payload = {'filter':'sector', 'types': 'company', 'symbols':ticker}
            response = _single_query(endpoint, payload)
            if not response:
                symbol_dict[ticker] = None
            else:
                response = dict(response)
                symbol_dict[ticker] = response[ticker]['company']['sector']
        except:
            symbol_dict[ticker] = None
    return symbol_dict


sectors = sector_get(ticker_list, endpoint)
newvar = X.index.map(lambda x: sector_list[x] if x in sector_list.keys() else None)
X['Sector'] = pd.Series(newvar, index=X.index)

X['Market Cap'] = pd.cut(X['Market Capitalisation'], [0, 2000000, 10000000, 200000000,1000000000], labels=['Small', 'Mid', 'Large', 'Mega'])
