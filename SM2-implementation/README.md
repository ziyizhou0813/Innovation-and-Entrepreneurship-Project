# SM2算法实现

## 算法原理

设需要发送的信息为比特串M，klen为M的比特长度。

为了对明文M进行加密，我们需要实现以下步骤：

1.用随机数发生器产生随机数$k\in [1,n-1]$;

2.计算椭圆曲线点$C_1= [k]G=(x_1,y_1)$，将$C_ 1$的的数据类型转换为比特串；

3.计算椭圆曲线点$S=[h]P_B$,若S是无穷远点，则报错并退出；

4.计算椭圆曲线点$[k]P_B=(x_2,y_2)$,将坐标$x_2$、$y_2$的数据类型转换为比特串；

5.计算$t=KDF(x_2 \parallel y_2,klen)$,若t为全0比特串，则返回第一步；

6.计算$C_2=M \oplus t$;

7.计算$C_3=Hash(x_2 \parallel M \parallel y_2)$;

8.输出密文$C=C_1 \parallel C_3 \parallel C_2$。

其中密钥派生函数需要调用密码杂凑算法。

设密码杂凑算法为$H_v()$,其输出是长度恰为v比特的杂凑值。

密钥派生函数$KDF(Z,klen)$:

输入：比特串Z，整数klen[表示要获得的密钥数据的比特长度，要求该值小于$(2^{32}-1)v$]。

输出：长度为klen的密钥数据比特串K。

a) 初始化一个32比特构成的计数器$ct=0x00000001$;

b) 对i从1到$\lceil klen/v \rceil$执行:

   1) 计算$Ha_i=H_v(Z \parallel ct)$;
   
   2) $ct++$;

c)若klen/v是整数，令 

$$Ha!_{\lceil klen/v \rceil}= Ha_{\lceil klen/v \rceil}$$

否则令

$$Ha!_{\lceil klen/v \rceil}$$

为 $Ha_{\lceil klen/v \rceil}$最左边的$(klen-(v\times \lfloor klen/v \rfloor)$比特；

令$K=Ha_1 \parallel Ha_2 \parallel \cdots \parallel Ha_{\lceil klen/v \rceil -1} \parallel Ha!_{\lceil klen/v \rceil}$。
## 代码实现

在SM2.py文件中有对代码步骤的注释，请在文件中查看

## 运行结果

 ![This is an image](https://github.com/ziyizhou0813/Innovation-and-Entrepreneurship-Project/blob/main/SM2-implementation/SM2test.png)
