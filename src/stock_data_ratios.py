import pandas as pd
import numpy as np
from extractor import *
import pdb
import pickle

data = SimFinDataset('data/simfin-data (1).csv', csvDelimiter='semicolon')

num_comp = data.numCompanies
num_ind = data.numIndicators
# get tickers
ticker_list = []
for i in range(num_comp):
    ticker_list.append(data.companies[i].ticker)
# get indicator names
ind_names = []
for i in range(num_ind):
    ind_names.append(data.companies[0].data[i].name)
# get dates for index
date_index = data.timePeriodsDates

#create list of dataframes of each company
df_list = []
for i in range(num_comp):
    comp_df = pd.DataFrame(index=date_index, columns=ind_names)
    for j in range(num_ind):
        comp_df[ind_names[j]]=(data.companies[i].data[j].values)
#forward fill nan values for shares columns
    for k in range(1,4):
        comp_df[ind_names[k]].fillna(method='ffill',inplace=True)
# remove entries where null for financials
    comp_df = comp_df[comp_df[ind_names[36]].notnull()]
# backfill nans for non-shares columns
    comp_df.fillna(method='backfill',axis=0, inplace=True)
# append comp dfs to list
    df_list.append(comp_df)

# collect entry dates for later use
entry_dates = []
# build df of annual financials for each company
main_df = pd.DataFrame(index=ticker_list, columns=ind_names)
for idx, comp in enumerate(df_list):
    if comp.shape[0] <= 3:
        continue
    entry_dates.append(comp.iloc[-1,:].name)
    entry = comp.iloc[-1,:].values.reshape(1,59)
    main_df.iloc[idx,:] = entry
#
main_df_nonans = main_df.dropna(axis=0, how='any')
#
main_df_nonans.to_pickle('data/stocks_ratios.pkl')
