import struct
from flask import Flask
from flask import request

app=Flask(__name__)

@app.route('/')
def hello():
    '''
    Scrieti aici numele voastre
    '''
    return "CRC API LUCIAN TREPTEANU"

def calculeaza_crc(polinom,date):
    poli=bin(polinom)
    poli=poli[2:]

    n=len(poli)
    msg=''.join(format(ord(i),'b') for i in str(date,'utf-8'))
    m=len(msg)

    curr=[]
    p=[]
    for i in range(m):
        curr.append(int(msg[i]))
    for i in range(n-1):
        curr.append(0)
        p.append(int(poli[i]))
    p.append(int(poli[n-1]))

    for i in range(m):
        if curr[i] == 1:
            for j in range(n):
                curr[i+j]=curr[i+j]^p[j]

    crc=''.join(str(elem)for elem in curr[m:])
    crc=msg+crc
    crc=bytes(crc,encoding='utf-8')

    return crc


@app.route('/crc',methods=['POST','GET'])
def post_method():
    params=struct.unpack('!L{}s'.format(len(request.data)-4),request.data)
    crc=calculeaza_crc(params[0],params[1])

    return crc

if __name__=='__main__':
    app.run(host='0.0.0.0',port=8001)