import numpy as np
import matplotlib.pyplot as plt
from two_layer_net import TwoLayerNet   # 两层神经网络类
from common.load_data import get_data   # 加载数据集函数

# 1. 加载数据
x_train, x_test, t_train, t_test = get_data()

# 2. 创建模型
network = TwoLayerNet(input_size=784, hidden_size=50, output_size=10)

# 3. 设置超参数
learning_rate = 0.1
batch_size = 100
num_epochs = 30

train_size = x_train.shape[0]
iter_per_epoch = np.ceil(train_size/batch_size)
iters_num = int(num_epochs * iter_per_epoch)

train_loss_list = []
train_acc_list = []
test_acc_list = []

# 4. 循环迭代，用梯度下降法训练模型
for i in range(iters_num):
    # 4.1 随机选取批量数据
    batch_mask = np.random.choice(train_size, batch_size)
    x_batch = x_train[batch_mask]
    t_batch = t_train[batch_mask]
    # 4.2 计算梯度
    # grad = network.numerical_gradient(x_batch, t_batch)
    grad = network.gradient(x_batch, t_batch)
    # print("grad:======", i)
    # 4.3 更新参数
    for key in ('W1', 'b1', 'W2', 'b2'):
        network.params[key] -= learning_rate * grad[key]
    # 4.4 计算并保存当前的训练损失
    loss = network.loss(x_batch, t_batch)
    train_loss_list.append(loss)
    # 4.5 每完成一个epoch的迭代，就计算并保存训练和测试准确率
    if i % iter_per_epoch == 0:
        train_acc = network.accuracy(x_train, t_train)
        test_acc = network.accuracy(x_test, t_test)
        train_acc_list.append(train_acc)
        test_acc_list.append(test_acc)
        print('Epoch: {}, Loss: {}, Train Acc: {}, Test Acc: {}'.format(i//iter_per_epoch + 1, loss, train_acc, test_acc))

# 5. 画图
x = np.arange( len(train_acc_list) )
plt.plot(x, train_acc_list, label='Train Acc')
plt.plot(x, test_acc_list, label='Test Acc', linestyle='--')
plt.legend(loc='best')
plt.show()