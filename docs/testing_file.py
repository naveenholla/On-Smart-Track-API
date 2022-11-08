# # # from asyncio.log import logger
# # # from contextlib import closing
# # # from urllib.request import urlopen
# # # import json
# # # import yaml
# # # import pandas as pd
# # # import io
# # # import csv

# # # class MarketDataManager():

# # #     def pull_indices_market_cap(record): 
# # #         temp_folder = r"C:\Sachin\Projects\On-Smart-Track\logs\temp"
# # #         url = record["url"]
# # #         sector_name = str(record["name"]).replace(" ", "_")
# # #         is_sectoral = bool(record["is_sector"])
                    
# # #         print(f"Started with {sector_name}, {url}.")
# # #         with urlopen(url) as webpage:
# # #             content = webpage.read().decode().replace("'","||||").replace("modelDataAvailable(","[").replace(");","]").replace("label:","\"label\":").replace("label:","\"label\":").replace("file:","\"file\":")

# # #             url_temp = f'{temp_folder}/{sector_name}_temp.json'

# # #             with open(url_temp, 'w') as file_intermediate: 
# # #                 # Writing the replaced data in our
# # #                 # text file
# # #                 file_intermediate.write(json.dumps(content, ensure_ascii=True, indent=4).replace('\\"', '"')[1:-1])

# # #             with open(url_temp, 'r') as file_intermediate2: 
# # #                 # Writing the replaced data in our
# # #                 # text file
# # #                 data = yaml.safe_load(file_intermediate2)

# # #             with open(url_temp, 'w') as file_final: 
# # #                 # Writing the replaced data in our
# # #                 # text file
# # #                 file_final.write(str(data).replace("'", '"').replace("||||","'"))

# # #             with open(url_temp, 'r') as file_final2: 
# # #                 # Writing the replaced data in our
# # #                 # text file
# # #                 data_updated = json.load(file_final2)

# # #                 if not is_sectoral:
# # #                     df = pd.json_normalize(data_updated[0]["groups"], 'groups', ['label', 'weight', 'id'], record_prefix='_')
# # #                     df['label'] = df['label'].str.rsplit(' ', n=1).str.get(0)
# # #                     df['_label'] = df['_label'].str.rsplit(' ', n=1).str.get(0)
# # #                     df.rename(columns = {'_label':'name', "_weight": "equity_weightage", 'label':'sector_name', "weight": "sector_weightage"}, inplace = True) # rename the column name

# # #                 else:
# # #                     df = pd.DataFrame(data_updated[0]["groups"])
# # #                     df['label'] = df['label'].str.rsplit(' ', n=1).str.get(0)
# # #                     df.rename(columns = {'label':'name', "weight": "equity_weightage"}, inplace = True) # rename the column name
# # #                 return df

# # # record = {
# # #             "name": "Nifty 50",
# # #             "url": "https://blob.niftyindices.com/jsonfiles/SectorialIndex/SectorialIndexDataNIFTY%20FMCG.js",
# # #             "ordinal": 1,
# # #             "is_sector": True
# # #         }
# # # data = MarketDataManager.pull_indices_market_cap(record)
# # # distinct_sector_pd = pd.DataFrame(data,columns=['sector_name']).drop_duplicates()
# # # distinct_sector_pd.dropna()
# # # distinct_sector_pd.rename(columns = {'sector_name':'name'}, inplace = True) # rename the column name
# # # print(distinct_sector_pd)
# # # distinct_sector = distinct_sector_pd.to_dict('records') # convert to dictionary
# # # print(distinct_sector)

# # # ############################################
# # # # BULK COPY
# # # ############################################
# # # # https://github.com/sreeo/django-bulk-saving-demo/tree/e647ee665617f862a508b228716d8753994ac9de
# # # # import io
# # # # import pandas
# # # # import csv
# # # # import uuid
# # # # from contextlib import closing
# # # # from django.db import connection

# # # # from rest_framework import viewsets, status
# # # # from rest_framework.decorators import action
# # # # from rest_framework.response import Response

# # # # from icecream.models import IceCream
# # # # from icecream.api.serializers import IceCreamSerializer


# # # # class IceCreamViewset(viewsets.ModelViewSet):
# # # #     permission_classes = []
# # # #     queryset = IceCream.objects.all()
# # # #     serializer_class = IceCreamSerializer

# # # #     @action(methods=["POST"], detail=False)
# # # #     def bulk_create(self, request, *args, **kwargs):

# # # #         uploaded_file = request.FILES["file"]
# # # #         file_stream = io.StringIO(uploaded_file.read().decode('utf-8'))
# # # #         csv_data = pandas.read_csv(file_stream, delimiter=',').to_dict('records')

# # # #         serializer = self.get_serializer(data=csv_data, many=True)
# # # #         serializer.is_valid(raise_exception=True)
# # # #         icecreams = serializer.save()
# # # #         return Response(data=IceCreamSerializer(icecreams, many=True).data, status=status.HTTP_200_OK)

# # # #     @action(methods=["POST"], detail=False)
# # # #     def bulk_upload(self, request, *args, **kwargs):
# # # #         uploaded_file = request.FILES["file"]
# # # #         file_stream = io.StringIO(uploaded_file.read().decode('utf-8'))
# # # #         csv_data = pandas.read_csv(file_stream, delimiter=',').to_dict('records')

# # # #         stream = io.StringIO()
# # # #         writer = csv.writer(stream, delimiter='\t')

# # # #         for row in csv_data:
# # # #             writer.writerow([str(uuid.uuid4()), row["name"]])
# # # #         stream.seek(0)

# # # #         with closing(connection.cursor()) as cursor:
# # # #             cursor.copy_from(
# # # #                 file=stream,
# # # #                 table=IceCream.objects.model._meta.db_table,
# # # #                 sep='\t',
# # # #                 columns=('id', 'name'),
# # # #             )
# # # #         return Response(data=csv_data, status=status.HTTP_200_OK)

# # # # from icecream.models import IceCream
# # # # from rest_framework import serializers


# # # # class ListIceCreamSerializer(serializers.ListSerializer):
# # # #     def create(self, validated_data):
# # # #         result = [self.child.create(attrs) for attrs in validated_data]
# # # #         IceCream.objects.bulk_create(result, ignore_conflicts=True)

# # # #         return result


# # # # class IceCreamSerializer(serializers.ModelSerializer):
# # # #     def create(self, validated_data):
# # # #         return IceCream(**validated_data)

# # # #     class Meta:
# # # #         model = IceCream
# # # #         fields = "__all__"
# # # #         list_serializer_class = ListIceCreamSerializer

# # # # from uuid import uuid4
# # # # from django.db import models

# # # # class IceCream(models.Model):
# # # #     id = models.UUIDField(default=uuid4, primary_key=True)
# # # #     name = models.CharField(max_length=512)
# # # #     created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
# # # #     modified_date = models.DateTimeField(auto_now=True, null=True, blank=True)

# # # # def log_info(message):
# # # #     logger.info(message)

# # # # def Error_While_Data_Pull(message):
# # # #     logger.error(message)

# # # # def reading_csv_pandas_web(url:str, header=0, skiprows=None, delimiter:str=','):
# # # #     """This task is used to pull the data from the website"""
    
# # # #     log_info(f"Started with {url}.")
# # # #     try:
# # # #         # fetch page source using pandas
# # # #         data = pd.read_csv(url,sep=delimiter, skiprows=skiprows, skipfooter=0, header=header, engine='python')
# # # #         log_info(f"{len(data)} records found from {url}.")            
# # # #         print(data)
# # # #     except Exception as e:
# # # #         message = f"Request exception from {url} - `{format(e)}`."
# # # #         raise Error_While_Data_Pull(message=message)

# # # # reading_csv_pandas_web("https://www1.nseindia.com/content/equities/EQUITY_L.csv")

# import datetime
# import pandas as pd

# default_date_format = r"%Y-%m-%d"
# default_time_format = r"%H:%M:%S"
# default_date_time_format = r"%Y-%m-%d %H:%M:%S.%f %z"

# def convert_datetime_to_string(datetimeObj:datetime, dateFormat:str=None) -> str:
#     f = dateFormat
#     return datetimeObj.strftime(f)

# def log_debug(message):
#     print(message)

# class Error_While_Data_Pull(Exception):
#     pass

# def reading_csv_pandas_web(url:str, header=0, skiprows=None, delimiter:str=','):
#     """This task is used to pull the data from the website"""

#     log_debug(f"Started with {url}.")
#     try:
#         # fetch page source using pandas
#         data = pd.read_csv(url,sep=delimiter, skiprows=skiprows, skipfooter=0, header=header, engine='python')
#         log_debug(f"{len(data)} records found from {url}.")            
#         return data
#     except Exception as e:
#         message = f"Request exception from {url} - `{format(e)}`."
#         raise Error_While_Data_Pull(message=message)

# def format_url(url_record, date):
#     url = convert_datetime_to_string(date, f"{url_record['url']}")
#     if "args" in url_record:
#         index = 0
#         for arg in url_record["args"]:
#             if 'format' in arg:
#                 value = convert_datetime_to_string(date, arg['format'])
#                 if "is_upper" in arg and bool(arg["is_upper"]):
#                     value = value.upper()
#                 url = url.replace("{"+ str(index)+"}", value)
#                 index += 1
#     return url

# def pull_equity_eod_data(urls, date):
#     url_record = urls["equity_bhavcopy"] # get the all listed equity url
#     url = format_url(url_record, date)
            
#     log_debug(f"Started with {url}.")

#     # fetch page source using requests.get() 
#     data = reading_csv_pandas_web(url=url) # pull csv containing all the listed equities from web
#     data.columns = data.columns.str.strip()  # remove extra spaces from the column names
#     data.rename(
#         columns = {            
#             'Index Name':'name',
#             'Open Index Value':'open_price', 
#             'High Index Value':'high_price', 
#             'Low Index Value':'low_price', 
#             'Closing Index Value':'close_price', 
#             'Points Change':'point_changed', 
#             'Change(%)':'percentage_changed',  
#             'Volume':'traded_quantity',
#             'Turnover (Rs. Cr.)':'turn_overs_in_cr', 
#             'P/E': "index_pe", 
#             'P/B': "index_pb", 
#             'Div Yield': "index_div_yield",
#             'Index Date': 'date'
#         }, inplace = True) # rename the column name  
#     data = data[[
#             'name',
#             'open_price', 
#             'high_price', 
#             'low_price', 
#             'close_price', 
#             'point_changed', 
#             'percentage_changed',
#             'traded_quantity', 
#             'turn_overs_in_cr',
#             "index_pe", 
#             "index_pb", 
#             "index_div_yield",
#             'date']] # select only specific columns
#     log_debug(f"{data.count}")

#     return data

# record = {
#     "equity_bhavcopy":{
#         "url": "https://archives.nseindia.com/content/indices/ind_close_all_%d%m%Y.csv"
#     }
# }

# pull_equity_eod_data(record, datetime.datetime(year=2022,month=9,day=29))

import datetime

import pytz

utcTimeZone = pytz.timezone("UTC")
testing_date_time_value = datetime.datetime(2022, 6, 20, 6, 52, 0, 0, tzinfo=utcTimeZone)
print(testing_date_time_value)