#常量初始化
_H0 = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
       0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
_HashConstant = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
                 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
                 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
                 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
                 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
                 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
                 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
                 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
                 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
                 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
                 0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
                 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
                 0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
                 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
                 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
                 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]

#右移
def shiftRight(a, x):
    return ((a >> x)|(a << (32 - x))) & (2 ** 32 - 1)

#消息填充
def msgProcess(m):
    str_l = chr(len(m)<<3)
    m += '\x80'
    m += '\x00' * ((55 - len(m)) % 64)
    str_l = '\x00' * (9 - len(str_l)) + str_l
    m += str_l
    return m

#sha256
def SHA256(message,H0):
    H = H0.copy() 
    #消息填充
    message = msgProcess(message)
    #压缩函数
    #将消息M分解成n个512-bit大小的块
    for i in range(0, len(message), 64):
        msg = message[i:i+64]
        W = []
        #构造64个字
        for j in range(0,64,4):
            cut = msg[j:j+4]
            W.append(ord(cut[0])*(256**3)+ord(cut[1])*(256**2)+ord(cut[2])*256+ord(cut[3]))
        W = W + ([0]*48)
        for j in range(16,64):
            s0 = shiftRight(W[j-15],7) ^ shiftRight(W[j-15],18) ^ (W[j-15]>>3)
            s1 = shiftRight(W[j-2],17) ^ shiftRight(W[j-2],19) ^ (W[j-2]>>10)
            W[j] = (W[j-16] + s0 + W[j-7] + s1) & (2**32-1)
        a,b,c,d,e,f,g,h = H

        #64次加密循环
        for i in range(64):
            s0 = (shiftRight(a, 2) ^ shiftRight(a, 13) ^ shiftRight(a, 22)) & ((2**32)-1)
            maj = ((a & b) ^ (a & c) ^ (b & c)) & ((2**32)-1)
            t2 = (s0 + maj) & ((2**32)-1)
            s1 = (shiftRight(e,6) ^ shiftRight(e,11) ^ shiftRight(e,25)) & ((2**32)-1)
            ch = ((e & f) ^ (~e & g)) & ((2**32)-1)
            t1 = (h + s1 + ch + _HashConstant[i] + W[i]) & ((2**32)-1)
            a,b,c,d,e,f,g,h = (t1+t2) & ((2**32)-1), a,b,c,(d+t1) & ((2**32)-1),e,f,g
        temp = [a,b,c,d,e,f,g,h]
        #将循环结果存放在H中
        for i in range(8):
            H[i] += temp[i]
            H[i] = H[i] & ((2**32)-1)

    #转字符串
    en = [str(hex(it))[2:] for it in H]
    for i in range(8):
        it = en[i]
        if len(it)<8:
            en[i] = '0'*(8-len(it))+it

    return ''.join(en)

#长度扩展攻击
#这里hash为hash（key||msg）的hash值，m为已知消息msg，key未知，其中ll为消息长度，append为消息扩展内容
#我们最终要生成h'=hash(key||meg||100...||length||append)，为伪造的hash值
def length_extension_attack(hash,m,ll,append):
    #首先构造m，将已知的长度通过sha256的填充方式填充为512bit
    str_l = chr(ll<<3)
    m += chr(0x80)
    m += chr(0x00) * ((55 - ll) % 64)
    str_l = chr(0x00) * (9 - len(str_l)) + str_l
    m += str_l
    m += append
    #将hash值分为8组存放在h0中作为下一轮sha256的输入
    h0 = []
    for j in range(0,64,8):
            cut = hash[j:j+8]
            hex_int = int(cut, 16)
            h0.append(hex_int)
    #扩展后的消息（m+padding+append），这里'/x00'字符无法显示
    print('扩展后的msg',m)
    #已知hash和append我们可以构造出新的hash值和对应的消息
    print('扩展后的hash: ', SHA256(append,h0))




if __name__ == '__main__':
    msg = '1234'#已知消息
    key = 'salt'#未知值
    m = key + msg
    append = 'message'#扩展消息
    length = len(m)#消息总长度
    print('消息:   ', m)
    hash = SHA256(m,_H0)#消息加密后的hash值
    print('hash值: ', hash)
    length_extension_attack(hash,msg,length,append)#长度扩展攻击
