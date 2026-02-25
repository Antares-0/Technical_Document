import torch
import matplotlib.pyplot as plt

from torch import nn, optim    # 神经网络模型和优化器
from torch.utils.data import TensorDataset, DataLoader  # 数据集和数据加载器

# 1. 构建数据集，创建数据加载器
X = torch.randn(100, 1)
# 预设真实系数
w = torch.tensor([2.5])
b = torch.tensor([5.2])
# 定义随机噪声
noise = torch.randn(100, 1) * 0.5
# 定义拟合的目标值y
y = w * X + b + noise
# 构建DataSet
dataset = TensorDataset(X, y)
# 构建DataLoader
# shuffle=True 每个批次打乱数据
dataloader = DataLoader(dataset, batch_size=10, shuffle=True)

# 2. 构建模型
model = nn.Linear(in_features=1, out_features=1)

# 3. 定义损失函数和优化器
loss = nn.MSELoss()
optimizer = optim.SGD(model.parameters(), lr=0.001)

# 4. 模型训练
epoch_num = 200
loss_list = []

# 训练epoch_num轮次
for epoch in range(epoch_num):
    total_loss = 0  # 本轮总损失
    # iter_num = 0    # 本轮迭代次数
    # 一个轮次，遍历DataLoader
    for x_train, y_train in dataloader:
        # 4.1 前向传播（预测）
        y_pred = model(x_train)
        # 4.2 计算损失
        loss_value = loss(y_pred, y_train)
        total_loss += loss_value.item() * x_train.shape[0]
        # iter_num += 1
        # 4.3 反向传播
        loss_value.backward()
        # 4.4 更新参数
        optimizer.step()
        # 4.5 梯度清零
        optimizer.zero_grad()
    # 计算本轮平均损失
    loss_list.append(total_loss / len(dataset))

# 打印参数
print(model.weight)
print(model.bias)

# 画图
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
# 1. 训练损失随轮次epoch的变化
ax[0].plot(loss_list)
ax[0].set_xlabel('epoch')
ax[0].set_ylabel('loss')
# 2. 绘制散点图和拟合直线
ax[1].scatter(X, y)
y_pred = model.weight.item() * X + model.bias.item()
ax[1].plot(X, y_pred, color='red')
plt.show()