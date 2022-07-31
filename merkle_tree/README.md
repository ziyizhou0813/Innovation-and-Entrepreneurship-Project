# merkle tree

## 原理
Merkle树类似二叉树，其叶子节点上的值通常为数据块的哈希值，一个父节点是由其左右子节点的hash值进行拼接再做一次hash运算得到，如下图所示：

![This is an image](https://github.com/ziyizhou0813/Innovation-and-Entrepreneurship-Project/blob/main/merkle_tree/merkle%20tree%E5%8E%9F%E7%90%86%E5%9B%BE.jpg)

从图中我们可以清楚地了解到merkle tree的构建原理，用文字阐述如下：

1.对数据块分别计算哈希值（这里使用地是sha256算法）

2.上层节点的hash值由下层其左右节点hash值拼接之后再做hash所得的值

3.从下到上直至计算到最上层，即只有一个根节点root时，此时merkle tree构建成功

打印merkle tree我们可以采用二叉树先序遍历的思想进行打印。

## 运行结果
其中输入的test数据块为['1','2','3','4','5']

具体代码和注释在python文件中

以下为该数据库打印出merkle树各个节点的hash值（按照先序遍历）

![This is an image](https://github.com/ziyizhou0813/Innovation-and-Entrepreneurship-Project/blob/main/merkle_tree/%E8%BF%90%E8%A1%8C%E7%BB%93%E6%9E%9C.png)
