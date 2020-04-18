# import requests

# count = 0
# for i in range(0, 10):
#     try:
#         response = requests.get('http://www.jepx.org/market/excel/spot_2019.csv')
#         print(response)
#     except:
#         count += 1

# print(f'final {count}')

from tabula import read_pdf
df1 = read_pdf('https://posoco.in/download/28-03-20_nldc_psp-2/?wpdmdl=27995')
print(df1)