# Innovation and Entrepreneurship Project

注明：对于"sm3优化"，"sm3生日攻击"，"sm4优化"，"sm4-SIMD指令集优化"这四个项目为之前做好的project，它们所在不同的仓库（可以看到我主页），在这里将其合并到这个总的项目仓库，并非短时间push。

本md文件只介绍了"sm3优化"项目的报告，其他项目报告具体在仓库中对应的md文件中查看。
# 基于SIMD优化SM3算法

## SIMD优化思路

SM3算法是一种分组密码算法。其分组长度为128bit，以字（32位）为单位进行加密运算。通过观察整个SM3算法，主要分为消息填充、消息扩展和压缩函数三个部分。

### 消息填充

SM3对消息的处理是分组进行的，每组长度64字节，如果消息的长度不是64字节的整数倍，即最后一个分组的长度不是64字节，就需要对最后一个分组进行填充。
对于消息填充，我们只需要对其进行简单的优化尝试，例如对于循环展开和基于流水线的优化。
在本次project中在消息填充最多尝试的是循环展开，分成不同的步长，发现对于时间上没有明显的优化，猜测可能由于数据大小不够大体现出不来，又或者是电脑的寄存器和cpu核数并没有完全匹配，使得性能提升不大。

### 消息扩展

消息扩展部分是本次SM3算法优化中主要研究的方向。我们发现在消息扩展中将512bit消息分为16个32bit的字进行加密计算。
这里我们将字保存在unsigned int类型W数组中，公式如下：

$$P_1(X) = X \oplus (X \lll 15)  \oplus (X \lll 23)$$

$$W_j=P_1(W_{j-16} \oplus W_{j-9} \oplus (W_{j-16} \lll 15)) \oplus (W_{j-13} \lll 7) \oplus W_{j-6}$$

$$W_j'  = W_j \oplus W_{j+4}$$

通过这16个字可生成下16个字，最终扩展生成132个字。所以我们可以将生成16个字看为1轮，使用SIMD中__m128i存储方式，可以将4个字存储在一个寄存器中，一次同时进行4个字的生成计算，可以大大优化性能。大体流程可以从下图中看出

![This is an image](https://github.com/ziyizhou0813/Innovation-and-Entrepreneurship-Project/blob/main/SM3-optimization/%E6%B6%88%E6%81%AF%E6%89%A9%E5%B1%95%E4%BC%98%E5%8C%96%E8%BF%87%E7%A8%8B.jpg)

上图右边就是把消息放进寄存器，然后做消息扩展，和上图左边一次计算出一个字$W_j$相比，右边一次可以计算出3个字$W_{j}$,$W_{j+1}$,$W_{j+2}$ 。之所以不是一次计算出4个字 ，是因为$W_{j+3}$的计算需要用到 $W_{j}$，但$W_{j}$又是扩展出来的，此时$W_{j}$还未算出。在具体的实现中，我是先等$W_{j}$,$W_{j+1}$,$W_{j+2}$计算完成，再用上图左边的方法计算$W_{j+3}$。

### 压缩函数

对于压缩函数这个部分，并没有采取有效的优化。因为压缩函数属于一种线性的计算，本轮的处理好的数据会作用到下一轮之中，若要采用并行的优化方法是不能直接实现的，所以在这并没有深度研究下去。

## 代码说明

```
__m128i left(__m128i a, int k)
{
	k = k % 32;
	__m128i tmp1, tmp2, tmp3, tmp4;
	__m128i ze = _mm_set_epi32(0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF);
	tmp2 = _mm_slli_epi32(a, k); //左移
	tmp2 = _mm_and_si128(ze, tmp2);  //并操作
	tmp3 = _mm_srli_epi32(_mm_and_si128(ze, a), 32-k);  
	tmp4 = _mm_or_si128(tmp2, tmp3); //将左移的位数放到末尾
	return tmp4;
}
```
该代码是通过SIMD指令实现循环左移操作。
```
for (j = 4; j < 17; j++)//基于SIMD对消息扩展进行优化
	{
		int i = j * 4 + 3;
    //如上图所示，将16字中4个字放在一个寄存器中
		tmp10 = _mm_setr_epi32(W[j * 4 - 16], W[j * 4 - 15], W[j * 4 - 14], W[j * 4 - 13]); 
		tmp4 = _mm_setr_epi32(W[j * 4 - 13], W[j * 4 - 12], W[j * 4 - 11], W[j * 4 - 10]);
		tmp5 = _mm_setr_epi32(W[j * 4 - 9], W[j * 4 - 8], W[j * 4 - 7], W[j * 4 - 6]);
		tmp6 = _mm_setr_epi32(W[j * 4 - 3], W[j * 4 - 2], W[j * 4 - 1], 0);
		tmp7 = _mm_setr_epi32(W[j * 4 - 6], W[j * 4 - 5], W[j * 4 - 4], W[j * 4 - 3]);
    //一次进行4次并行的消息扩展操作
		tmp1 = _mm_xor_si128(tmp10, tmp5); 
		tmp2 = left(tmp6, 15);
		tmp1 = _mm_xor_si128(tmp1, tmp2);
		tmp3 = _mm_xor_si128(tmp1, _mm_xor_si128(left(tmp1, 15), left(tmp1, 23)));
		tmp8 = _mm_xor_si128(left(tmp4, 7), tmp7);
		temp[j] = _mm_xor_si128(tmp3, tmp8);
		_mm_maskstore_epi32(&W[j * 4], ze, temp[j]);
		W[i] = P_1(W[i - 16] ^ W[i - 9] ^ (rotate_left(W[i - 3], 15))) ^ (rotate_left(W[i - 13], 7)) ^ W[i - 6];
	}
```
该代码为优化后的消息扩展，其具体优化过程在优化思路有提到，总的来说是将其四组放在寄存器进行并行位运算，最后输出结果。
## 结果对比
运行结果：

![This is an image](https://github.com/ziyizhou0813/Innovation-and-Entrepreneurship-Project/blob/main/SM3-optimization/%E7%BB%93%E6%9E%9C.png)

最后我们将优化前和优化后的性能测试进行对比，如下图所示：

优化前：

![This is an image](https://github.com/ziyizhou0813/Innovation-and-Entrepreneurship-Project/blob/main/SM3-optimization/%E4%BC%98%E5%8C%96%E5%89%8D.png)

优化后：

![This is an image](https://github.com/ziyizhou0813/Innovation-and-Entrepreneurship-Project/blob/main/SM3-optimization/%E4%BC%98%E5%8C%96%E5%90%8E.png)

我们发现在基于SIMD优化后的消息扩展的SM3算法快了0.1秒左右。

因为这是加密一组的结果，若对于更大的数据，这0.1的优化则会带来更好性能提升。

## 项目路径

该sm3优化项目路径在SM3-optimization文件夹内。

