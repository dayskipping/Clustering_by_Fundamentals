# Clustering_by_Fundamentals
Clustering analysis of stocks using fundamental ratios

## Goal

My goal for this project is to investigate whether or not any patterns exist in the financial statement data of various companies which can lead to meaning insights in how they may be grouped together.  I will attempt to answer this question through performing a cluster analysis utilizing various dimension reduction and machine learning techniques.

## The Data

The dataset used in this analysis comes from [Simfin](https://simfin.com) which provides open source access to the fundamental data of 1564 companies with their respective financial statements data dating back to 2009. I was able to extract the data from a bulk downloaded .csv file of their entire dataset with the help of an extractor that can be found on this [Github](https://github.com/SimFin/bd-extractor) page. In addition, I queried the [IEX API](https://iextrading.com/developer/docs/) in order to acquire sector labels for each company in an effort to provide additional comparisons to traditional company classifications.

### Features

Originally the data was comprised of 61 features which included the original financial statement data and ratios thereof. The final feature set was chosen after considering only ratios and, of those ratios, only measures that did not factor in the price of the stock. The reason for this selection criteria was to avoid simply identifying the signal of company size and stock price.   


| **Net Profit Margin** | **Return on Equity** | **Return on Assets** |
| :-----------: | :------------: | :-----------: |
| Income(Loss)/ Revenue | Income(Loss) / Total Equity |Income(Loss) / Total Assets |

| **Current Ratio** | **Liabilities to Equity** | **Debt to Assets** |
| :-------: | :--------:| :-------: |
| Current Assets / Current Liabilities | Liabilities / Equity | Debt / Assets |

## Distribution

The company list included a small group of outliers with extreme valuation readings. In order to better identify the clusters of companies which were more representative of the population majority, I decided to remove those names who fell more than three standard deviations away from the mean of each feature. In total, 18 companies were removed through this process. In the end, the final group included in the analysis was comprised of 986 companies.

![scatter matrix]('plots/scatter_matrix.png')

### Company Profiles

| **Sectors** |                    
| :--------: |
| Basic Materials |47|
|Communication Services |15|
|Consumer Cyclical |160|
|Consumer Defensive |60|
|Energy |50|
|Financial Services |34|
|Healthcare |137|
|Industrials |148|
|Real Estate |55|
|Technology |197|
|Utilities |32|

| **Market Caps** |
| :-------: |
| Small |362|
| Mid |289|
|Large |336|
|Mega |17|
