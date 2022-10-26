# import pandas as pd

# url = "https://archives.nseindia.com/content/fo/fii_stats_20-Oct-2022.xls"
# df = pd.read_excel(url, header=2)
# df = df.head(4)
# df.rename(
#     columns={
#         "Unnamed: 0": "instrument",
#         "No. of contracts": "no_of_contracts_bought",
#         "Amt in Crores": "value_of_contracts_bought",        
#         "No. of contracts.1": "no_of_contracts_sold",
#         "Amt in Crores.1": "value_of_contracts_sold",       
#         "No. of contracts.2": "open_interest",
#         "Amt in Crores.2": "value_of_open_interest",
#     },
#     inplace=True,
# )  # rename
# print(df)
# # df.columns=df.columns.map('-'.join).str.strip('-')

# # columns = []
# # for column in df.columns:
# #     c = column.rsplit("-", 1)[0].replace("Unnamed: 0_level_0-","").replace(" Rs Crores-"," ").replace("-","")
# #     columns.append(c)
# # df.columns=columns

# # for index, record in df.iterrows():
# #      if record["Date"] == "25-Oct-2022":
# #          print(record)


# # import requests
# # from bs4 import BeautifulSoup


# # vgm_url = 'https://in.investing.com/indices/major-indices'
# # html_text = requests.get(vgm_url).text
# # soup = BeautifulSoup(html_text, 'html.parser')
# # print(soup)