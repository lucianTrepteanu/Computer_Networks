import requests
import json

url='http://rt1:8001/post'
headers={'Content-Type':'application/json'}
data={'value':100}

print(requests.post(url,data=json.dumps(data),headers=headers).content)