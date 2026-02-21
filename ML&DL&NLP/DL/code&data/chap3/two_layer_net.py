import numpy as np

class TwoLayerNet:
    # 初始化
    def __init__(self, input_size, hidden_size, output_size, weight_init_std=0.01):
        self.params = {}
        # W1和W2的参数不应该一样，避免权重同步更新而失效
        # b1和b2不担心
        self.params['W1'] = weight_init_std * np.random.randn(input_size, hidden_size)
        self.params['b1'] = np.zeros(hidden_size)
        self.params['W2'] = weight_init_std * np.random.randn(hidden_size, output_size)
        self.params['b2'] = np.zeros(output_size)
    # 前向传播（预测）
    def forward(self, X):
        W1, W2 = self.params['W1'], self.params['W2']
        b1, b2 = self.params['b1'], self.params['b2']
        a1 = X @ W1 + b1
        z1 = sigmoid(a1)
        a2 = z1 @ W2 + b2
        y = softmax(a2)
        return y
    # 计算损失
    def loss(self, x, t):
        y = self.forward(x)
        loss_value = cross_entropy(y, t)
        return loss_value
    # 计算准确度
    def accuracy(self, x, t):
        y_proba = self.forward(x) # 预测概率
        # 根据最大概率得到预测的分类号
        y = np.argmax(y_proba, axis=1)
        # 与正确解标签对比，得到准确率
        accuracy = np.sum(y == t) / x.shape[0]
        return accuracy
    # 计算梯度
    def numerical_gradient(self, x, t):
        # 定义目标函数
        loss_f = lambda w: self.loss(x, t)
        # 对每个参数，使用数值微分方法计算梯度
        grads = {}
        grads['W1'] = numerical_gradient(loss_f, self.params['W1'])
        grads['b1'] = numerical_gradient(loss_f, self.params['b1'])
        grads['W2'] = numerical_gradient(loss_f, self.params['W2'])
        grads['b2'] = numerical_gradient(loss_f, self.params['b2'])
        return grads

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

# Sigmoid函数
def sigmoid(x):
    return 1/(1+np.exp(-x))