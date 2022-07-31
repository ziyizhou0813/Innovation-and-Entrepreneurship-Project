# the Rho method of reduce SM3

## 原理

随机选择一个数m，对其使用SM3加密得到H1，再将H1使用SM3加密得到H2.接下来循环以下操作：
$$H_1=SM3(H_1)$$
$$H_2=SM3(H_2)$$

经过不断的循环，最终H1,H2会出现在一个环里，最后判断H1是否等于H2，若等于则找到一个碰撞。

以下原理图：

![This is an image](https://github.com/ziyizhou0813/Innovation-and-Entrepreneurship-Project/blob/main/SM3-Rhoattack/%E5%8E%9F%E7%90%86%E5%9B%BE.png)

## 运行结果

这里我们从8bit开始测试，最后测试到20bit都能在有限时间找到碰撞，当为24bit时在3分钟内未能跑出。


![This is an image](https://github.com/ziyizhou0813/Innovation-and-Entrepreneurship-Project/blob/main/SM3-Rhoattack/20bit%E8%BF%90%E8%A1%8C%E7%BB%93%E6%9E%9C.png)

