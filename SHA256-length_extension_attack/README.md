# SHA256长度扩展攻击

哈希长度扩展攻击(hash lengthextensionattacks)是指针对某些允许包含额外信息的加密散列函数的攻击手段。次攻击适用于MD5和SHA-1等基于Merkle–Damgård构造的算法。

## 攻击原理

 要想对SHA256进行长度扩展攻击，我们首先要知道SHA256算法中消息填充有一定的了解。
 
 在SHA256算法中，输入的消息是512bit倍数，如果不是则需要消息填充。其中512bit消息分为“消息+填充+消息长度”，其中填充是从消息末尾先填一个1，再补0到448比特长度为止；最后64比特用来
 存放消息长度。
 
 知道了消息填充，我们便可进行长度扩展攻击。SHA256属于hash函数，输入512比特倍数消息，输出固定256比特长度的哈希值。一般情况下，要被hash的消息为“key||message”，其中key是相当于密钥
 message是要发送的消息，消息接收方得到message和哈希值用共享密钥进行判断消息是否安全。而作为攻击者的我们，是对key不知道的，所以我们可以通过长度扩展攻击伪造hash值。
 
 首先我们已知的是message和SHA256（key||message）,我们先从message得到消息的长度len。然后根据消息填充规则我们可以知道message后填充内容为padding=10...000||len。然后我们既然已经知道了
 SHA256（key||message）的值我们可以再来一轮SHA256，对我们想要扩展的消息X进行一轮hash运行，最后得到的结果为SHA256（key||message||padding||x）。而我们将此时的SHA256计算出的hash值
 和message||padding||x发送给接收方是可以通过验证，则我们进行伪造的hash值成立，长度扩展攻击达成。
 
 下面图片为上述过程的原理图：
 ![This is an image](https://github.com/ziyizhou0813/Innovation-and-Entrepreneurship-Project/blob/main/SHA256-length_extension_attack/sha256%E9%95%BF%E5%BA%A6%E6%89%A9%E5%B1%95%E6%94%BB%E5%87%BB%E5%8E%9F%E7%90%86%E5%9B%BE.png)
 
 
 ## 运行结果
 
该为长度扩展攻击伪造生成的hash值和message
 十六进制下的message：
 
 ![This is an image](https://github.com/ziyizhou0813/Innovation-and-Entrepreneurship-Project/blob/main/SHA256-length_extension_attack/test.png)
 
 最终结果：
 
 ![This is an image](https://github.com/ziyizhou0813/Innovation-and-Entrepreneurship-Project/blob/main/SHA256-length_extension_attack/%E4%BC%AA%E9%80%A0%E7%BB%93%E6%9E%9C.png)
