import requests
import json

def functie(nume):
    url='https://1.1.1.1/dns-query'
    headers={}
    headers={'accept':'application/dns-json'}
    params={}
    params={'name':nume}

    result=requests.get(url,params=params, headers=headers)
    return result.json()['Answer'][0]['data']

print(functie('fmi.unibuc.ro'))