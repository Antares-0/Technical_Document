import numpy as np
from common.functions import softmax, sigmoid, cross_entropy
from common.gradient import numerical_gradient
from common.layers import *     # 引入神经网络的层
from collections import OrderedDict     # 有序字典，用来保存层结构

class TwoLayerNet:
    # 初始化
    def __init__(self, input_size, hidden_size, output_size, weight_init_std=0.01):
        self.params = {}
        self.params['W1'] = weight_init_std * np.random.randn(input_size, hidden_size)
        self.params['b1'] = np.zeros(hidden_size)
        self.params['W2'] = weight_init_std * np.random.randn(hidden_size, output_size)
        self.params['b2'] = np.zeros(output_size)
        # 定义层结构
        self.layers = OrderedDict()
        self.layers['Affine1'] = Affine(self.params['W1'], self.params['b1'])
        self.layers['ReLU1'] = Relu()
        self.layers['Affine2'] = Affine(self.params['W2'], self.params['b2'])
        # 单独定义最后一层：SoftmaxWithLoss
        self.lastLayer = SoftmaxWithLoss()
    # 前向传播（预测）
    def forward(self, X):
        # 对于神经网络中的每一层，依次调用forward方法
        for layer in self.layers.values():
            X = layer.forward(X)
        return X
    # 计算损失
    def loss(self, x, t):
        y = self.forward(x)
        loss_value = self.lastLayer.forward(y, t)
        return loss_value
    # 计算准确度
    def accuracy(self, x, t):
        y_pred = self.forward(x) # 预测分类数值
        # 根据最大概率得到预测的分类号
        y = np.argmax(y_pred, axis=1)
        # 与正确解标签对比，得到准确率
        accuracy = np.sum(y == t) / x.shape[0]
        return accuracy
    # 计算梯度：使用数值微分方法
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
    # 计算梯度：使用反向传播法
    def gradient(self, x, t):
        # 前向传播，直到计算损失
        self.loss(x, t)
        # 反向传播
        dy = 1
        dy = self.lastLayer.backward(dy)
        # 将神经网络中的所有层翻转处理
        layers = list(self.layers.values())
        layers.reverse()
        for layer in layers:
            dy = layer.backward(dy)
        # 提取各层参数的梯度
        grads = {}
        grads['W1'], grads['b1'] = self.layers['Affine1'].dW, self.layers['Affine1'].db
        grads['W2'], grads['b2'] = self.layers['Affine2'].dW, self.layers['Affine2'].db
        return grads