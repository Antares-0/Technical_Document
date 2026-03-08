import time

import torch
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm

from dataset import get_dataloader
from model import InputMethodModel
import config
from src.tokenizer import JiebaTokenizer


def train_one_epoch(model, dataloader, loss_fn, optimizer):
    """
    训练一个轮次
    :param model: 模型
    :param dataloader: 数据集
    :param loss_fn: 损失函数
    :param optimizer: 优化器
    :return: 当前epoch的平均loss
    """
    model.train()
    total_loss = 0
    for inputs, targets in tqdm(dataloader, desc='训练'):
        # inputs.shape: [batch_size, seq_len]
        # targets.shape: [batch_size]

        # 前向传播
        outputs = model(inputs)
        # outputs.shape: [batch_size, vocab_size]
        loss = loss_fn(outputs, targets)

        # 反向传播
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        total_loss += loss.item()
    return total_loss / len(dataloader)


def train():
    # 1. 确定设备
    # pass

    # 2. 数据集
    dataloader = get_dataloader()

    # 3.词表
    tokenizer = JiebaTokenizer.from_vocab(config.MODELS_DIR / 'vocab.txt')

    # 4. 模型
    model = InputMethodModel(vocab_size=tokenizer.vocab_size)

    # 5. 损失函数
    loss_fn = torch.nn.CrossEntropyLoss()

    # 6. 优化器
    optimizer = torch.optim.Adam(model.parameters(), lr=config.LEARNING_RATE)

    # 7. tensorboard writer
    writer = SummaryWriter(log_dir=config.LOGS_DIR / time.strftime("%Y-%m-%d_%H-%M-%S"))

    # 开始训练
    best_loss = float('inf')
    for epoch in range(1, 1 + config.EPOCHS):
        print("=" * 10, f" Epoch: {epoch} ", "=" * 10)
        # 训练一个epoch的逻辑
        loss = train_one_epoch(model, dataloader, loss_fn, optimizer)
        print(f"loss:{loss}")

        # 记录训练结果
        writer.add_scalar('loss', loss, epoch)

        # 保存模型
        if loss < best_loss:
            best_loss = loss
            torch.save(model.state_dict(), config.MODELS_DIR / 'best.pth')
            print("模型保存成功")

    writer.close()


if __name__ == '__main__':
    train()
