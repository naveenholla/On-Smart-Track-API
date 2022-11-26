# import os
# import sys

# path = os.getcwd()
# path = os.path.abspath(os.path.join(path, "packages/fyers-apiv2/2.0.5"))
# sys.path.insert(1,os.path.abspath(path))

# import fyers_api
# print(fyers_api.__path__)
#     #this will be 0.24.2 

import re
test_string = "Face Value Split (Sub-Division) - From Rs 10/- Per Share To Rs 2/- Per Share"
test_string ="Annual General Meeting/Dividend - Rs  1.50 Per Share/Special Dividend- Rs 0.75 Per Share"
res = [float(s) for s in re.findall(r'-?\d+\.?\d*', test_string)]
print(res)