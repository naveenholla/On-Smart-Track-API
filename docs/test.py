# # # # # import pandas as pd

# # # # # url = "https://www.hdfcpension.com/nav/"
# # # # # df = pd.read_html(url)

# # # # # print(df)


# # # # from selenium import webdriver
# # # # import pandas as pd
# # # # import requests

# # # # # driver = webdriver.Chrome()
# # # # # driver.implicitly_wait(30)

# # # # # url = "https://www.hdfcpension.com/nav/"
# # # # # url = "https://in.investing.com/indices/major-indices"

# # # # # driver.get(url)
# # # # # df=pd.read_html(driver.findElement(By.cssSelector("table[class='common-table']")))[0]
# # # # # print(df)


# # import pandas as pd
# # import pandas_ta as ta

# # df = pd.DataFrame() # Empty DataFrame

# # # Load data
# # #df = pd.read_csv("path/to/symbol.csv", sep=",")
# # # OR if you have yfinance installed
# # df = df.ta.ticker("^NSEBANK", period="2d", interval="5m")

# # # Take a peek
# # df.tail()
# # print(df.columns)

# # # VWAP requires the DataFrame index to be a DatetimeIndex.
# # # Replace "datetime" with the appropriate column from your DataFrame
# # #df.set_index(pd.DatetimeIndex(df["Date"]), inplace=True)

# # # Calculate Returns and append to the df DataFrame
# # df.ta.log_return(cumulative=True, append=True)
# # df.ta.percent_return(cumulative=True, append=True)

# # # New Columns with results
# # print(df.columns)

# # # Take a peek
# # print(df.tail())








# # # # url = "https://www.hdfcpension.com/nav/"

# # # # header = {
# # # #   "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
# # # #   "X-Requested-With": "XMLHttpRequest"
# # # # }

# # # # r = requests.get(url, headers=header)

# # # # dfs = pd.read_html(r.text)[0].dropna()
# # # # print(dfs)





# # # # # import requests
# # # # # from bs4 import BeautifulSoup


# # # # # vgm_url = "https://www.hdfcpension.com/nav/"
# # # # # html_text = requests.get(vgm_url).text
# # # # # soup = BeautifulSoup(html_text, 'html.parser')
# # # # # print(soup)

# # # # # df.columns=df.columns.map('-'.join).str.strip('-')

# # # # # columns = []
# # # # # for column in df.columns:
# # # # #     c = column.rsplit("-", 1)[0].replace("Unnamed: 0_level_0-","").replace(" Rs Crores-"," ").replace("-","")
# # # # #     columns.append(c)
# # # # # df.columns=columns

# # # # # for index, record in df.iterrows():
# # # # #      if record["Date"] == "25-Oct-2022":
# # # # #          print(record)


# # # # # import requests
# # # # # from bs4 import BeautifulSoup


# # # # # vgm_url = 'https://in.investing.com/indices/major-indices'
# # # # # html_text = requests.get(vgm_url).text
# # # # # soup = BeautifulSoup(html_text, 'html.parser')
# # # # # print(soup)
# n = 1
# m = 2


# print(operations('*'))
# print(operations('^'))
