import requests


def send_msg(msg):
    headers = {'Content-Type': 'application/json'}
    d = {"msgtype": "text",
         "text": {
             "content": msg
         }}
    resp = requests.post(
        "https://oapi.dingtalk.com/robot/send?access_token=8f003b0d3519a6686c4ab455b6df52b5794fc1a311be71cdeae9628dceb22a2c",
        json=d, headers=headers)
    return resp.text
