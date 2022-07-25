
# SM3-birthday_attack

## 算法思路

生日攻击是在n/2的时间里找到一个碰撞。

首先我们想要创建一个n/2个随机消息的列表，这里编写def getRandomList(n)函数来创建这个范围在[0,n)内的列表。然后创建好这个碰撞列表我们将列表的值依次求出加密后sm3的结果，并取出前n比特放入一个新的列表中，每次放入前判断是否列表中已经有该元素，若有则碰撞成功，没有则碰撞失败，具体流程参照以下步骤。

## 代码流程
```
令H: M => {0, 1} n为散列函数 ( |M| >> 2 n ) 

以下是在时间O(2 n/2 )散列 中找到冲突的通用算法。

算法： 
 

1.在 M 中选择 n/2条随机消息： $m_1 , m_2 , ...., m,n/2$

2.对于 i = 1, 2, ..., 2 n/2计算$t_i = H(m_i)$ => {0, 1}n

3.寻找碰撞 ($t_i = t_j$ )。如果没有找到，返回步骤 1

```

## 运行结果
本次实验我们设n为16-bit进行运行，得到以下结果。
![This is an image](https://github.com/ziyizhou0813/Innovation-and-Entrepreneurship-Project/blob/main/SM3-birthday_attack/%E8%BF%90%E8%A1%8C%E7%BB%93%E6%9E%9C.png)
## 项目路径

该项目路径在"SM3-birthday_attack"文件夹中。
