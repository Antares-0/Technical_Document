import numpy as np

# 使用数值微分求解梯度
# 数值微分求梯度，传入x是一个向量
def _numerical_gradient(f, x):
    h = 1e-4
    grad = np.zeros_like(x)
    # 遍历x中的特征xi
    for i in range(x.size):
        tmp = x[i]
        x[i] = tmp + h
        fxh1 = f(x)
        x[i] = tmp - h
        fxh2 = f(x)
        # 利用中心差分公式计算偏导数
        grad[i] = (fxh1 - fxh2) / (2*h)
        # 恢复x[i]的值
        x[i] = tmp
    return grad

# 传入X是一个矩阵
def numerical_gradient(f, X):
    # 判断维度
    if X.ndim == 1:
        return _numerical_gradient(f, X)
    else:
        grad = np.zeros_like(X)
        # 遍历X中的每一行数据，分别求梯度
        for i, x in enumerate(X):
            grad[i] = _numerical_gradient(f, x)
        return grad

# 激活函数，用于计算分类问题的分类概率
def softmax(x):
    # 如果是二维矩阵
    if x.ndim == 2:
        x = x.T
        x = x - np.max(x, axis=0)
        y = np.exp(x) / np.sum(np.exp(x), axis=0)
        return y.T
    # 溢出处理策略
    x = x - np.max(x)
    return np.exp(x) / np.sum(np.exp(x))

# 用于计算交叉熵损失
def cross_entropy(y, t):
    # 将y转为二维
    if y.ndim == 1:
        t = t.reshape(1, t.size)
        y = y.reshape(1, y.size)
    # 将t转换为顺序编码（类别标签）
    if t.size == y.size:
        t = t.argmax(axis=1)
    n = y.shape[0]
    return -np.sum( np.log(y[np.arange(n), t] + 1e-10) ) / n

# 定义一个简单神经网络类
class SimpleNet:
    # 初始化
    def __init__(self):
        self.W = np.random.randn(2, 3)
    # 前向传播
    def forward(self, X):
        a = X @ self.W
        y = softmax(a)
        return y
    # 计算损失值
    def loss(self, x, t):
        y = self.forward(x)
        loss = cross_entropy(y, t)
        return loss

# 主流程
if __name__ == '__main__':
    # 1. 定义数据
    x = np.array([0.6, 0.9])
    t = np.array([0, 0, 1])
    # 2. 定义神经网络模型
    net = SimpleNet()
    # 3. 计算梯度
    f = lambda _: net.loss(x, t)
    # 传入损失函数和当前点
    gradw = numerical_gradient(f, net.W)

    print(gradw)