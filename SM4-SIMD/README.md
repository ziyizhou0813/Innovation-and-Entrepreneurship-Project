# 基于SIMD指令集优化SM4算法

SIMD技术可实现同一操作并行处理多组数据。本次我们使用SIMD技术的AVX2指令并行实现SM4的过程方法。AVX2指令使用128-bit xmm寄存器可实现4组消息的并行加/解密，
使用256-bit ymm寄存器可实现8组消息的并行加/解密。


## 优化思路

### 消息的转载

本次优化是实现多组明文进行并行加密和对于SM4中F函数的并行计算。

首先我们要将加密的消息存储到ymm寄存器中，这里将n组128-bit SM4明文消息记为$P_i(0 \leq i< n,n=4,8)$。需将Pi装载到4个SIMD寄存器R0、R1、R2、R3中。装载规则如下

$$R_k[i] \leftarrow P_i[k], 0 \leq i< n,0 \leq k< 4$$

其中，Rk[i]表示Rk寄存器中第i个32-bit字位置，Pi[k]表示明文消息Pi中第k个32-bit字的内容。即Rk寄存器依次存储着所有n组明文消息的第k个32-bit字内容。

在本次project中，我们使用4个256bit的寄存器，用来装载 X[i] (i=1,2,3,4)。因为一个字大小为32bit，所以一个寄存器可以存储8个字消息，这样我们可以并行处理8组128比特的分组消息。

具体代码如下：

```
R[0] = _mm256_loadu_si256((const __m256i*)m + 0);
R[1] = _mm256_loadu_si256((const __m256i*)m + 1);
R[2] = _mm256_loadu_si256((const __m256i*)m + 2);
R[3] = _mm256_loadu_si256((const __m256i*)m + 3);
X[0] = _mm256_unpacklo_epi64(_mm256_unpacklo_epi32(R[0], R[1]), _mm256_unpacklo_epi32(R[2], R[3]));
X[1] = _mm256_unpackhi_epi64(_mm256_unpacklo_epi32(R[0], R[1]), _mm256_unpacklo_epi32(R[2], R[3]));
X[2] = _mm256_unpacklo_epi64(_mm256_unpackhi_epi32(R[0], R[1]), _mm256_unpackhi_epi32(R[2], R[3]));
X[3] = _mm256_unpackhi_epi64(_mm256_unpackhi_epi32(R[0], R[1]), _mm256_unpackhi_epi32(R[2], R[3]));
```
这里是将消息先按顺序装载在4个寄存器中(R[i]),然后再通过_mm256_unpacklo_epi64，_mm256_unpackhi_epi64（64bit分组装载）和_mm256_unpacklo_epi32， _mm256_unpackhi_epi32
（32bit分组装载）[lo为低位，hi为高位]四个函数，将8组128bit消息中第i个字顺序放在对应的寄存器X[i]中。

由于SIMD采用小端存储，我们还需将大端变为小端：
```
__m256i vindex = _mm256_setr_epi8(3, 2, 1, 0, 7, 6, 5, 4, 11, 10, 9, 8, 15, 14, 13, 12, 3, 2, 1, 0, 7, 6, 5, 4, 11, 10, 9, 8, 15, 14, 13, 12);
X[0] = _mm256_shuffle_epi8(X[0], vindex);
X[1] = _mm256_shuffle_epi8(X[1], vindex);
X[2] = _mm256_shuffle_epi8(X[2], vindex);
X[3] = _mm256_shuffle_epi8(X[3], vindex);
```
### F轮函数优化

之前我们在SM4优化中已经验证了查表法的迅速（详细在SM4-optimization项目文件夹中tablecheck文件中），在这次我们依旧采用查表法（8bit->32bit）来优化T函数。
具体代码如下：
```
 for (int i = 0; i < 32; i++) {
        __m256i k =_mm256_set1_epi32((mode == 0) ? RK[i] : RK[31 - i]);//加密or解密
        R[0] = _mm256_xor_si256(_mm256_xor_si256(X[1], X[2]),_mm256_xor_si256(X[3], k));
        R[1] = _mm256_xor_si256(X[0], _mm256_i32gather_epi32((const int*)BOX0,_mm256_and_si256(R[0], Mask), 4));#查表异或
        R[0] = _mm256_srli_epi32(R[0], 8);#左移
        R[1] = _mm256_xor_si256(R[1], _mm256_i32gather_epi32((const int*)BOX1, _mm256_and_si256(R[0], Mask), 4));
        R[0] = _mm256_srli_epi32(R[0], 8);
        R[1] = _mm256_xor_si256(R[1], _mm256_i32gather_epi32((const int*)BOX2, _mm256_and_si256(R[0], Mask), 4));
        R[0] = _mm256_srli_epi32(R[0], 8);
        R[1] = _mm256_xor_si256(R[1], _mm256_i32gather_epi32((const int*)BOX3, _mm256_and_si256(R[0], Mask), 4));
        X[0] = X[1];
        X[1] = X[2];
        X[2] = X[3];
        X[3] = R[1];
    }
```
SM4查表法优化已经在前一个文档说明过，这里不多加赘述。首先我们先算出$X[1]\oplus X[2]\oplus X[3]\oplus RK$作为其T函数的输入。然后将SM4的S盒表记为ST，
转换后的4个表记为S0、S1，S2、S3。S0-S3的生成规则如下：
$$S0[i] = ST[i]$$

$$S1[i] = ST[i] <<8$$

$$S2[i] = ST[i] <<16$$

$$S3[i] = ST[i] <<24;0 \leq i< 256$$


因此，非线性变换τ即可通过掩码、移位、异或、查表操作实现。

$$\tau(R) = S0[R \\& 0xff] \oplus S1 [(R>>8)\\& 0xff] \oplus S2[(R>>16)\\& 0xff] \oplus S3 [R>>24]$$

代码中是通过并行左移（mm256_srli_epi32），并行查表（_mm256_i32gather_epi32），并行异或（_mm256_xor_si256）来实现一轮的操作。

### 存储密文

经过32轮加密得到的结果，经过小端转大端，再用_mm256_storeu_si256函数将其存放到数组中，便可输出的到我们想要的结果。

具体代码如下：
```
#小端变大端
X[0] = _mm256_shuffle_epi8(X[0], vindex);
X[1] = _mm256_shuffle_epi8(X[1], vindex);
X[2] = _mm256_shuffle_epi8(X[2], vindex);
X[3] = _mm256_shuffle_epi8(X[3], vindex);
#存储
_mm256_storeu_si256((__m256i*)c + 0, _mm256_unpacklo_epi64(_mm256_unpacklo_epi32(X[3], X[2]), _mm256_unpacklo_epi32(X[1], X[0])));
_mm256_storeu_si256((__m256i*)c + 1, _mm256_unpackhi_epi64(_mm256_unpacklo_epi32(X[3], X[2]), _mm256_unpacklo_epi32(X[1], X[0])));
_mm256_storeu_si256((__m256i*)c + 2, _mm256_unpacklo_epi64(_mm256_unpackhi_epi32(X[3], X[2]), _mm256_unpackhi_epi32(X[1], X[0])));
_mm256_storeu_si256((__m256i*)c + 3, _mm256_unpackhi_epi64(_mm256_unpackhi_epi32(X[3], X[2]), _mm256_unpackhi_epi32(X[1], X[0])));
```
## 运行结果

![This is an image](https://github.com/ziyizhou0813/Innovation-and-Entrepreneurship-Project/blob/main/SM4-SIMD/test.png)
可以对比在SM4-optimization中未优化前时间提升很大。

## 参考文献

SM4的快速软件实现技术 郎欢, 张蕾, 吴文玲 http://html.rhhz.net/ZGKXYDXXB/20180205.htm#Figure1
