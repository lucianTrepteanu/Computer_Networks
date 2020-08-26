import requests
import json
import struct

if __name__=='__main__':
    header={'Content-Type':'application/octet-stream'}
    polinom=235
    mesaj=b'Mesaj 1234'
    sz=len(mesaj)
    data=struct.pack('!L{}s'.format(sz),polinom,mesaj)
    data=bytes(data)

    url='http://0.0.0.0:8001/'
    res=requests.post(url,headers=header, data=data)
    print('CRC : ',res.content)