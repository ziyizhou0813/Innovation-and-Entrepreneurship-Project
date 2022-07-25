# SM4 and optimizations

# 优化思路 

## SM4 多线程优化

### 基于T函数的优化

在国密SM4算法中，分为明文处理和产生密钥两大部分，而在这两部分中都有一个T函数，其主要负责置换和移位。置换部分由s盒担任，因为有32比特的置换，每个s盒只能负责8比特，所以一共需要4个s盒。而对于该T函数的置换算法，s盒与s盒之间是相互独立进行的，所以我们可以对于s盒的置换创建4个线程，每个线程负责一个s盒的置换，这样同时运行可以优化其性能。

## 运用多线程同时加密多组明文

国密SM4属于密码中的分组密码，其一次只能操作128比特的明文加密，对于大于128比特的明文，需要将其分成n个128比特的组，对于每组分别加密，最后将加密好的密文拼接起来。对于每组的加密，其相互之间其实是相互独立的，我们可以基于创建多个进程，每个进程负责一组明文的加密工作，以此来提升程序性能。

## 循环展开

在sm4中不涉及到串行循环的变量，即没有依赖的变量，我们进行循环展开，提升算法性能。

## 查表法

SM4加/解密轮函数中的T变换由非线性变换τ和线性变换L构成。将非线性变换τ的输入记为$X=(x0, x1, x2, x3)∈({Z_2}^8)^4$，输出记为$Y=(y0, y1, y2, y3)∈({Z_2}^8)^4$。可将非线性变换τ的操作定义如下。

$$y_i = Sbox(x_i) , 0 \leq i < 4   (1)$$

将线性变换L的输入记为$P=(p0, p1, …, pn-1)∈({Z_2}^8)^4$，输出记为$Q=(q0, q1, …, qn-1)∈({Z_2}^8)^4$。其中，$m$大小需为SM4使用S盒规模的倍数，$m$与$n$的关系满足$n=32/m$。由于L中仅包含循环移位和异或操作。因此，可将线性变换L的操作定义为式(2)，非线性变换T操作可由式(1)与式(2)合并表示为式(3)：

$$Q = L(B) = L(p_0 << (n-1)m) \oplus L(p_1 <<(n-2)m) \oplus \cdots \oplus L(p_{n-1})(2)$$

$$Q = T(X) =L(Sbox(x_0) << (n-1)m) \oplus L(Sbox(x_1) << (n-2)m) \oplus \cdots \oplus L(Sbox(x_{n-1}))(3)$$

这里可将非线性变换T的操作制成4个8-bit输入32-bit输出的表：

$$T3[d_0] = L(Sbox(d_0) << 24)$$

$$T2[d_1] = L(Sbox(d_1) << 16)$$

$$T1[d_2] = L(Sbox(d_2) << 8)$$

$$T0[d_3] = L(Sbox(d_3));d_i \in [0,255], 0 \leq i < 4$$

## 代码实现

### 多线程
```
u32 Transt(u32 rki) {
	u32 rki_aftert = 0;		//输出t置换之后的rki
	for (int i = 0; i < 4; i++) {
		temp[i] = 0;
	}
  //四个s盒置换线程
	thread t1(transtAtoB, rki, 24, 0);
	thread t2(transtAtoB, rki, 16, 1);
	thread t3(transtAtoB, rki, 8, 2);
	thread t4(transtAtoB, rki, 0, 3);
	t1.join();
	t2.join();
	t3.join();
	t4.join();
	rki_aftert = temp[0] | temp[1] | temp[2] | temp[3];
	return rki_aftert;
}
```
这里将T函数中s盒的置换放在四个线程里进行，可以加速并行，使得性能提升。
``` 
  thread t1(decsk1,MK); 
	thread t2(decsk2,mk); 
	t1.join();
	t2.join();
```
这里decks可以看成sm4加密，其中只是对明文进行分组处理了一下。本次实验是将明文分成两组，使用多线程进行加密，而在代码中我们可以根据自己电脑cpu核数增加线程，可能会带来性能的提升。
### 循环展开
```
for (i = 4; i < 32; )//循环展开
	{
		rk1[i] = rk1[i - 4] ^ TransT_1(rk1[i - 3] ^ rk1[i - 2] ^ rk1[i - 1] ^ CK[i]); i++;
		rk1[i] = rk1[i - 4] ^ TransT_1(rk1[i - 3] ^ rk1[i - 2] ^ rk1[i - 1] ^ CK[i]); i++;
		rk1[i] = rk1[i - 4] ^ TransT_1(rk1[i - 3] ^ rk1[i - 2] ^ rk1[i - 1] ^ CK[i]); i++;
		rk1[i] = rk1[i - 4] ^ TransT_1(rk1[i - 3] ^ rk1[i - 2] ^ rk1[i - 1] ^ CK[i]); i++;
		rk1[i] = rk1[i - 4] ^ TransT_1(rk1[i - 3] ^ rk1[i - 2] ^ rk1[i - 1] ^ CK[i]); i++;
		rk1[i] = rk1[i - 4] ^ TransT_1(rk1[i - 3] ^ rk1[i - 2] ^ rk1[i - 1] ^ CK[i]); i++;
		rk1[i] = rk1[i - 4] ^ TransT_1(rk1[i - 3] ^ rk1[i - 2] ^ rk1[i - 1] ^ CK[i]); i++;
		rk1[i] = rk1[i - 4] ^ TransT_1(rk1[i - 3] ^ rk1[i - 2] ^ rk1[i - 1] ^ CK[i]); i++;
	}
```
将代码中能展开的循环尽量展开，提升程序性能。
### 查表法
在思路中已经介绍了如何通过查表提升性能，代码中将四个s盒进行列表为BOX1,BOX2,BOX3,BOX4.
```
 b = Sbox[a[0]] * 0x1000000 + Sbox[a[1]] * 0x10000 + Sbox[a[2]] * 0x100 + Sbox[a[3]];
 ```
 该代码为通过查表得到T变换后的结果。
 
 ## 运行结果
 
 ### 多线程
 
 优化前后：
 
  ![This is an image](https://github.com/ziyizhou0813/Innovation-and-Entrepreneurship-Project/blob/main/SM4-optimization/%E5%A4%9A%E7%BA%BF%E7%A8%8B%E7%BB%93%E6%9E%9C.png)
  
  可以看到下面优化后比上面优化前时间上有所减少。
  
  ### 循环展开
  
  展开前：
  
  ![This is an image](https://github.com/ziyizhou0813/Innovation-and-Entrepreneurship-Project/blob/main/SM4-optimization/%E5%BE%AA%E7%8E%AF%E5%B1%95%E5%BC%80%E5%89%8D.png)
    
  展开后：
  
  ![This is an image](https://github.com/ziyizhou0813/Innovation-and-Entrepreneurship-Project/blob/main/SM4-optimization/%E5%BE%AA%E7%8E%AF%E5%B1%95%E5%BC%80%E5%90%8E.png)
  
  ### 查表法
  优化前：
  
  ![This is an image](https://github.com/ziyizhou0813/Innovation-and-Entrepreneurship-Project/blob/main/SM4-optimization/%E6%9F%A5%E8%A1%A8%E5%89%8D.png)
    
  查表法：
  
  ![This is an image](https://github.com/ziyizhou0813/Innovation-and-Entrepreneurship-Project/blob/main/SM4-optimization/%E6%9F%A5%E8%A1%A8%E6%B3%95%E5%90%8E.png)
  
