import hashlib

# merkle树节点


class Node:
    def __init__(self, data):
        self.left = None
        self.right = None
        self.f = None
        self.data = data
        self.hash = hashlib.sha256(data.encode('utf-8')).hexdigest()

# 创建merkle树


def createmerkletree(leafNodes):
    merkletree = []
    # 创建节点
    for i in leafNodes:
        merkletree.append(Node(i))
    while(len(merkletree) != 1):
        # 判断节点是奇数还是偶数，然后对merkle树一层一层创建
        if len(merkletree) % 2 == 0:
            temp = []
            while len(merkletree) > 1:
                a = merkletree.pop(0)
                b = merkletree.pop(0)
                node = Node(a.hash + b.hash)
                temp.append(node)
                a.f = node
                b.f = node
                node.left = a
                node.right = b
            merkletree = temp
        else:
            temp = []
            l = merkletree.pop(-1)
            while len(merkletree) > 1:
                a = merkletree.pop(0)
                b = merkletree.pop(0)
                node = Node(a.hash + b.hash)
                temp.append(node)
                a.f = node
                b.f = node
                node.left = a
                node.right = b
            node1 = Node(l.data)
            node1.left = l
            l.f = node1
            temp.append(node1)
            merkletree = temp
    return merkletree[0]

# 先序遍历打印merkle树
def printmerkletree(tree):
    if tree != None:
        print(tree.hash, "   ")  # 当前节点
        printmerkletree(tree.left)  # 打印左树
        printmerkletree(tree.right)  # 打印右树
    else:
        return


if __name__ == "__main__":
    l = ['1', '2', '3', '4', '5']
    printmerkletree(createmerkletree(l))#先序遍历merkle树节点
