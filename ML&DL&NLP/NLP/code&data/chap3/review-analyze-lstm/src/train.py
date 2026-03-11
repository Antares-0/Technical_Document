import time

import torch
from torch import nn
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm

from tokenizer import JiebaTokenizer
from dataset import get_dataloader
import config
from model import MyModel


def train():
    # 数据
    loader = get_dataloader()
    # 分词器
    tokenizer = JiebaTokenizer.from_vocab(config.MODELS_DIR / 'vocab.txt')
    # 模型
    model = MyModel(tokenizer.vocab_size, tokenizer.pad_token_index)
    # 损失函数
    loss_fn = nn.BCEWithLogitsLoss()
    # 优化器
    optimizer = torch.optim.Adam(model.parameters(), lr=config.LEARNING_RATE)
    # TensorBoard Writer
    writer = SummaryWriter(log_dir=config.LOGS_DIR / time.strftime('%Y-%m-%d_%H-%M-%S'))

    best_loss = float('inf')
    for epoch in range(1, config.EPOCHS + 1):
        print(f'========== Epoch {epoch} ==========')
        loss = train_one_epoch(model, loader, loss_fn, optimizer)
        print(f'Loss: {loss:.4f}')

        # 记录到Tensorboard
        writer.add_scalar('Loss', loss, epoch)

        # 保存模型
        if loss < best_loss:
            best_loss = loss
            torch.save(model.state_dict(), config.MODELS_DIR / 'best.pt')
            print('保存模型')

    writer.close()


def train_one_epoch(model, loader, loss_fn, optimizer):
    total_loss = 0
    model.train()
    for inputs, targets in tqdm(loader):
        outputs = model(inputs)
        loss = loss_fn(outputs, targets)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        total_loss += loss.item()
    return total_loss / len(loader)


if __name__ == '__main__':
    train()