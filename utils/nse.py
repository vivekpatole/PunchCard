import json
from datetime import datetime

import requests

# Urls for fetching Data
url_oc = "https://www.nseindia.com/option-chain"
url_indices = "https://www.nseindia.com/api/allIndices"

target_columns = ["CE OI", "CE OI Change", "CE Volume", "CE LTP",
                  "Strike",
                  "PE LTP", "PE Volume", "PE OI Change", "PE OI"]

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/80.0.3987.149 Safari/537.36',
    'accept-language': 'en,gu;q=0.9,hi;q=0.8',
    'accept-encoding': 'gzip, deflate, br'
}

sess = requests.Session()
cookies = dict()


# Local methods
def set_cookie():
    request = sess.get(url_oc, headers=headers, timeout=5)
    cookies = dict(request.cookies)


def get_data(url):
    set_cookie()
    response = sess.get(url, headers=headers, timeout=5, cookies=cookies)
    if response.status_code == 200:
        return response.text
    return ""


def get_expiry(symbol):
    url = f'https://www.nseindia.com/api/option-chain-indices?symbol={symbol}'
    response_text = get_data(url)
    data = json.loads(response_text)
    current_expiry = data["records"]["expiryDates"][0]
    current = datetime.strptime(current_expiry, '%d-%b-%Y').date()
    today = datetime.today().date()
    if current < today:
        current_expiry = data["records"]["expiryDates"][1]
    current_expiry = current_expiry.replace('-', '').upper()
    # print(data['records']['timestamp'])
    return current_expiry

# print(get_expiry(symbol='NIFTY'))
# print(get_expiry(symbol='BANKNIFTY'))
