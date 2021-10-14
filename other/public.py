import requests
import json


def request_method(third_order_id):
    request_url = 'https://api.mautunai.finboat.net/admin/orders/order/detail'
    data_search = {}
    data_search['_id'] = third_order_id
    request_body = json.dumps(data_search)
    headers = {
        'Content-Type': 'application/json',
        'Referer': 'https://mautunai.finboat.net/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
        'Cookie': 'access_token_cookie=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MzQxNzMxMjAsIm5iZiI6MTYzNDE3MzEyMCwianRpIjoiMTM2NTM3YjYtOTE3Yy00NThlLWI2ODctZjg5NWZhMWZmNTI0IiwiZXhwIjoxNjM0MjA5MTIwLCJpZGVudGl0eSI6eyJ1aWQiOiI2MDQ1ODIyMDJiMzllMTRlZWY5NjE0MTQiLCJuYW1lIjoibWF1dHVuYWkiLCJwZmxhZyI6MCwicm9sZSI6Ilx1N2JhMVx1NzQwNlx1NTQ1OCJ9LCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MiLCJjc3JmIjoiM2JlZDQ5NTUtNDU4OC00ZDdjLTkxM2EtODg4Y2JkNDM1MGNlIn0.YhWTNrhVYgDjRr6SZ1Dj3tSQ7yrEKE8dhodiBEXo9eM; csrf_access_token=3bed4955-4588-4d7c-913a-888cbd4350ce'
    }
    response = requests.post(url=request_url, headers=headers, data=request_body)
    if response.status_code == 200:
        response_data = response.json()
        return response_data
    else:
        print('%s request error, %s' % (third_order_id, response.status_code))
    return None
