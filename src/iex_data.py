import requests
import pandas as pd
import numpy as np


# single get request to API
def single_query(endpoint, payload):
    response = requests.get(endpoint, params=payload)
    if response.status_code != 200:
        print('request unsuccessful')
    else:
        response_j = response.json()
    return response_j

# function to step through list of symbols 'size' at a time
def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

# function to replace None with 0
def replace_none(x):
    for i, val in enumerate(x):
        if val == None:
            x[i] = 0
    return x


def company_info_get(ticker_list, parameters, cat, endpoint):
    symbol_dict = {}
    for group in chunker(ticker_list, 100):
        group_dict = {}
        payload = {'filter': parameters, 'types': cat, 'symbols':(', ').join(group)}
        response = single_query(endpoint, payload)
        for ticker in group:
            group_dict[ticker] =[response[ticker][cat][param]\
            for param in parameters.split(', ')]
        symbol_dict.update(group_dict)

    return symbol_dict


def earnings_info_get(ticker_list, parameters, cat, endpoint):
    parameters_list = parameters.split(', ')
    symbol_dict = {}
    for group in chunker(ticker_list, 100):
        group_dict = {}
        payload = {'filter': parameters, 'types': cat, 'symbols':(', ').join(group)}
        response = single_query(endpoint, payload)
        for ticker in group:
            try:
                if response[ticker][cat][cat][0][parameters_list[0]] == None:
                    group_dict[ticker] = np.nan
                else:
                    group_dict[ticker] =[sum([response[ticker][cat][cat][0][param]\
                    for param in parameters_list \
                    for i in range(len(response[ticker][cat][cat]))])]
            except:
                group_dict[ticker] = np.nan
        symbol_dict.update(group_dict)

    return symbol_dict


def financials_info_get(ticker_list, cat, period, endpoint):
    symbol_dict = {}
    for group in chunker(ticker_list, 100):
        group_dict = {}
        payload = {'types': cat, 'symbols':(', ').join(group), 'period': period}
        response = single_query(endpoint, payload)
        for ticker in group:
            try:
                if response[ticker]['financials']\
                    ['financials'][0] == None:
                    group_dict[ticker] = np.nan
                else:

                    group_dict[ticker] = sum([np.apply_along_axis(replace_none, 0, \
                    np.array(list(response[ticker]['financials']\
                    ['financials'][i].values())[1:])) for i in range(len(response[ticker]\
                    ['financials']['financials']))])
            except:
                group_dict[ticker] = np.nan
        financials_keys = list(response[ticker]['financials']['financials'][0].keys())
        symbol_dict.update(group_dict)[1:]

    return symbol_dict, financials_keys



if __name__ == '__main__':
    # Query IEX API for list of all supported symbols
    endpoint = 'https://api.iextrading.com/1.0/ref-data/symbols'
    symbols = requests.get(endpoint).json()
    # Filter symbols to create list of common stocks only
    stock_symbols = []
    for sym in symbols:
        if sym['type'] == 'cs':
            stock_symbols.append(sym['symbol'])

    financials_group_list = []
    endpoint_1 = 'https://api.iextrading.com/1.0/stock/market/batch'
    for group in chunker(stock_symbols, 100):
        params = {'types': 'financials', 'symbols': (', ').join(group), 'period': 'annual'}
        fin_group = single_query(endpoint_1, params)
        financials_group_list.append(fin_group)

    financials_data_list = []
    for group in financials_group_list:
        for stock in group:
            financials_data_list.append([group[stock]['financials'].values()])
    # Create list of stocks that are missing financials data and list of lists of financials data for all others
    new_list = []
    missing_list = []
    for i in range(len(financials_data_list)):
        fin_list = list(financials_data_list[i][0])
        if len(fin_list) == 0:
            missing_list.append(i)
        else:
            new_list.append(fin_list[1][0])
    new_values = []
    for dict in new_list:
        new_values.append(dict.values())
    total_index = list(range(len(stock_symbols)))
    # boolean index of stocks that have financials data
    mask = [False if x in missing_list else True for x in total_index]
    stocks_array = np.array(stock_symbols)[mask]
    # Create final dataframe for all financials data
    final_df = pd.DataFrame(index=stocks_array, columns=new_list[0].keys(), data=new_values)

    # Create list with stats and 1y historical prices
    stats_list = []
    price_list = []
    for group in chunker(stocks_array, 100):
        params = {'types': 'stats', 'symbols': (', ').join(group)}
        stats_group = single_query(endpoint_1, params)
        stats_list.append(stats_group)
        params_p = {'types': 'chart', 'symbols': (', ').join(group), 'range': '1y'}
        price_group = single_query(endpoint_1, params_p)
        price_list.append(price_group)
    # Create lists with shares outstanding and average prices over 1y
    shares_list = []
    price_averages = []
    for i, group in enumerate(chunker(stocks_array, 100)):
        for stock in group:
            shares_list.append(stats_list[i][stock]['stats']['sharesOutstanding'])
            annual_prices = []
            for dict in price_list[i][stock]['chart']:
                annual_prices.append(dict['close'])
            if len(annual_prices) == 0:
                price_averages.append(0)
            else:
                price_averages.append(sum(annual_prices)/len(annual_prices))
    shares_array = np.array(shares_list)
    prices_array = np.array(price_averages)
    final_df['marketCap'] = shares_array * prices_array

    final_df['totalLiabilities'].fillna(0,axis=0, inplace=True)
    final_df['totalDebt'] = final_df['totalLiabilities']+final_df['totalDebt']
    final_df.drop('totalLiabilities', inplace=True, axis=1)

    # Get company name, industry, and sector
    company_params = 'companyName, industry, sector'
    company_info = company_info_get(stock_symbols, company_params, 'company', endpoint_1)
    df_cols = company_params.split(', ')
    company_info_df = pd.DataFrame(company_info)
    company_info_df = company_info_df.T
    company_info_df.columns = df_cols

    # Get company earnings
    earnings_params = 'actualEPS'
    earnings_df = earnings_info_get(stocks_array, earnings_params,'earnings', endpoint_1)
    earnings_df = pd.DataFrame(earnings_df).T
    earnings_df.columns = ['earnings']

    # Get financials info
    financials_df, fin_keys = financials_info_get(stocks_array, 'financials', 'quarter', endpoint_1)
    financials_df = pd.DataFrame(financials_df).T
    financials_df.columns = list(fin_keys)[1:]
    #
    # final_df = pd.concat([financials_df, earnings_df, company_info_df], axis=1)
    # final_df.drop(['companyName'], inplace=True, axis=1)
    #
    # I_swear_final_df = pd.get_dummies(final_df, columns=['industry', 'sector'])
    # I_swear_final_df.dropna(inplace=True)
    # I_swear_final_df.to_csv('johnny_tables.csv', index=False)
