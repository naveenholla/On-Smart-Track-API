# import json
# from django.conf import settings

# exchange = "NSE"
# config_dir = settings.CONFIG_DIR

# def log_info(message):
#     print(message)

# def log_debug(message):
#     print(message)

# def get_config(fileName:str):
#   path = f'{str(config_dir)}\\{fileName}.json'
#   log_debug(path)

#   # read all the file content
#   with open(path, 'r') as config:
#     jsonServerData = json.load(config)
#     return jsonServerData

# def test_get_exchange(exchange):
#     # read the url config
#     input_dictionary = get_config('exchanges')
#     log_info(input_dictionary)
#     output_dictionary = [x for x in input_dictionary if x["name"] == str(exchange)]
#     log_info(output_dictionary)
#     return output_dictionary[0]
