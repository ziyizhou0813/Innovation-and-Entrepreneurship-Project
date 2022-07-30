from encodings import utf_8
from quopri import decodestring
from gmssl import sm3, func
import random
import time

def SM3(m):
    long=(len(hex(m)[2:])+1)//2
    intm=int(m)
    msg=intm.to_bytes(long,"big")
    result = sm3.sm3_hash(func.bytes_to_list(msg))
    return result

def Rhoattack():
    n = 1000000
    x = random.randint(1,n)
    H1 = SM3(x)
    H2 = SM3(int(H1,16))
    while(1):
        H1=SM3(int(H1,16))
        H2=SM3(int(SM3(int(H2,16)),16))
        if (H1[:6] == H2[:6]):
            return 1

if __name__ == "__main__":
    time_start=time.time()
    if(Rhoattack()):
        print("success")
    time_end=time.time()
    print('time：',time_end-time_start,'s')