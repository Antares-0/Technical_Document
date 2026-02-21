import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from two_layer_net import TwoLayerNet   # 两层神经网络类

def get_data():
    # 1. 从文件加载数据集
    data = pd.read_csv("../../../ML/code&data/train.csv")
    # 2. 划分数据集
    X = data.drop("label", axis=1)
    y = data["label"]
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    # 3. 特征工程：归一化
    scaler = MinMaxScaler()
    x_train = scaler.fit_transform(x_train)
    x_test = scaler.transform(x_test)
    # 4. 将数据都转成ndarray
    y_train = y_train.values
    y_test = y_test.values

    return x_train, x_test, y_train, y_test

# 1. 加载数据
x_train, x_test, t_train, t_test = get_data()

# 2. 创建模型
network = TwoLayerNet(input_size=784, hidden_size=50, output_size=10)

# 3. 设置超参数
learning_rate = 0.1
batch_size = 100
num_epochs = 10

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
    grad = network.numerical_gradient(x_batch, t_batch)
    print("grad:======", i)
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
        print('Epoch: {}, Loss: {}, Train Acc: {}, Test Acc: {}'.format(i, loss, train_acc, test_acc))

# 5. 画图
x = np.arange( len(train_acc_list) )
plt.plot(x, train_acc_list, label='Train Acc')
plt.plot(x, test_acc_list, label='Test Acc', linestyle='--')
plt.legend(loc='best')
plt.show()