import random
import math
from gmssl import sm3, func
from gmpy2 import invert

#基本参数
#这里为椭圆曲线参数和随机数k
n=0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93
p=0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
a=0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC
b=0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93
gx=0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7
gy=0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0
db=0x58892B807074F53FBF67288A1DFAA1AC313455FE60355AFD
k=random.randint(1,n-1)

#encode是将字符串转换为编码后的二进制字符串
#s为要转换的字符串（明文）
def encode(s):
    return ''.join(["{:0>8}".format(bin(ord(c)).replace('0b', ''))for c in s])


#最大公因数
def gcd_x_y(x, y):
    if y == 0:
        return x
    else:
        return gcd_x_y(y, x % y)

#椭圆曲线中两点相加函数
#(x1,y1),(x2,y2)为相加的两点，a为椭圆曲线方程a的值，p为模数
def add_gf(x1,y1,x2,y2, a, p):
    flag = 1  
    if x1 == x2 and y1 == y2:
        member = 3 * (x1 ** 2) + a  
        denominator = 2 * y1    
    else:
        member = y2 - y1
        denominator = x2 - x1 
        if member* denominator < 0:
            flag = 0
            member = abs(member)
            denominator = abs(denominator)
    
    # 将分子和分母化为最简
    gcd_value = gcd_x_y(member, denominator)
    member = int(member / gcd_value)
    denominator = int(denominator / gcd_value)
    # 求分母的逆元    
    inverse_value = invert(denominator, p)
    k = (member * inverse_value)
    if flag == 0:
        k = -k
    k = k % p
    # 计算x3,y3
    x3 = (k ** 2 - x1 - x2) % p
    y3 = (k * (x1 - x3) - y1) % p
    return x3,y3

#椭圆曲线方程乘法运算
#n为乘数，(x,y)为被乘点，最后输出(x3,y3)
def mul(n,x,y):
    tempx = x
    tempy = y
    n=bin(n)[2:]
    for i in range(1,len(n)):
        tempx,tempy = add_gf(tempx,tempy,tempx,tempy,a,p)
        if n[i]=='1':
            tempx,tempy = add_gf(tempx,tempy,x,y,a,p)
    return tempx,tempy

#SM2算法中计算C1，其中k为随机数，范围在[1,n-1)
def getC1(n,k):
    xc1,yc1  = mul(k,gx,gy)
    xc1=hex(xc1)[2:]
    yc1=hex(yc1)[2:]
    C1="04"+xc1+yc1
    return C1

#计算(x2,y2),其中(x2,y2)为SM2中求C2和C3的中间变量
def get_x2y2(db):
    PBx,PBy = mul(db,gx,gy)
    x2,y2 = mul(k,PBx,PBy)
    return x2,y2

#SM2算法中计算C2，其中M为明文，klen为明文比特长度，db为私钥
#hash算法采用gmssl库中SM3(这里注意要把比特串转为字节)
def getC2(M,klen,db):
    x2,y2=get_x2y2(db)
    v=256
    t1=""
    ha=[]
    t1=t1+hex(x2)[2:]+hex(y2)[2:]
    ll=math.ceil(klen/v)
    ct=1
    #KDF密钥派生函数
    for i in range(1,ll+1):
        hexct='{:0>8x}'.format(ct)
        m=t1+hexct
        length=(len(m)+1)//2
        intm=int(m,16)
        msg=intm.to_bytes(length,"big")
        hai=sm3.sm3_hash(func.bytes_to_list(msg))
        ha.append(hai)
    r=klen-v*(ll-1)
    ha[-1]=ha[-1][:r]
    C2="".join(ha)
    C2=int(C2,16)^int(M,16)
    C2=hex(C2)[2:]
    return C2

#SM2算法中计算C3，M为明文。db为私钥
#hash函数采用SM3算法
def getC3(M,db):
    x2,y2=get_x2y2(db)
    t=''
    t=t+hex(x2)[2:]+M+hex(y2)[2:]
    length=(len(t)+1)//2
    intm=int(t,16)
    msg=intm.to_bytes(length,"big")
    C3=sm3.sm3_hash(func.bytes_to_list(msg))
    return C3

#SM2算法，计算得到C1,C2,C3;将其拼接得到最后的密文C
def SM2(db,M,klen):
    C1=getC1(n,k)
    C2=getC2(M,klen,db)
    C3=getC3(M,db)
    C=C1+C2+C3
    return C


if __name__ == "__main__":
    M="abc"
    msg=encode(M)
    klen=len(msg)
    c=SM2(db,msg,klen)
    print(c)