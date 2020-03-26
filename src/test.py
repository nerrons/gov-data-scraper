import requests

count = 0
for i in range(0, 10):
    try:
        response = requests.get('http://www.jepx.org/market/excel/spot_2019.csv')
        print(response)
    except:
        count += 1

print(f'final {count}')

