# import pyupbit

# with open("secret_key.txt", "r",encoding='utf-8') as f:
#     access = f.readline().strip()
#     secret = f.readline().strip()

# upbit = pyupbit.Upbit(access, secret)

# cash  = upbit.get_balance()
# print("보유현금", cash)


import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode

import requests

with open("secret_key.txt", "r",encoding='utf-8') as f:
    access = f.readline().strip()
    secret = f.readline().strip()

access_key = access
secret_key = secret
server_url = "https://api.upbit.com"

payload = {
    'access_key': access_key,
    'nonce': str(uuid.uuid4()),
}

jwt_token = jwt.encode(payload, secret_key)
authorize_token = 'Bearer {}'.format(jwt_token)
headers = {"Authorization": authorize_token}

res = requests.get(server_url + "/v1/accounts", headers=headers)

print(res.json())