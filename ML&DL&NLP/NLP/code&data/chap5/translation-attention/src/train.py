import time

import torch
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm

from dataset import get_dataloader
from tokenizer import ChineseTokenizer, EnglishTokenizer
import config
from model import TranslationModel


def train_one_epoch(model, dataloader, loss_fn, optimizer):
    total_loss = 0
    model.train()
    for inputs, targets in tqdm(dataloader, desc='训练'):
        encoder_inputs = inputs  # inputs.shape: [batch_size, src_seq_len]
        targets = targets  # targets.shape: [batch_size, tgt_seq_len]
        decoder_inputs = targets[:, :-1]  # decoder_inputs.shape: [batch_size, seq_len]
        decoder_targets = targets[:, 1:]  # decoder_targets.shape: [batch_size, seq_len]
        # 前向传播
        # 编码阶段
        encoder_outputs, context_vector = model.encoder(encoder_inputs)
        # context_vector.shape: [batch_size, hidden_size]

        # 解码阶段
        decoder_hidden = context_vector.unsqueeze(0)
        # decoder_hidden_0.shape: [1, batch_size, hidden_size]

        decoder_outputs = []

        seq_len = decoder_inputs.shape[1]
        for i in range(seq_len):
            decoder_input = decoder_inputs[:, i].unsqueeze(1)  # decoder_input.shape: [batch_size, 1]
            decoder_output, decoder_hidden = model.decoder(decoder_input, decoder_hidden, encoder_outputs)
            # decoder_output.shape: [batch_size, 1, vocab_size]
            decoder_outputs.append(decoder_output)

        # decoder_outputs：[tensor([batch_size,1,vocab_size])] -> [batch_size * seq_len, vocab_size]
        decoder_outputs = torch.cat(decoder_outputs, dim=1)
        # decoder_outputs.shape: [batch_size ,seq_len, vocab_size]
        decoder_outputs = decoder_outputs.reshape(-1, decoder_outputs.shape[-1])
        # decoder_outputs.shape: [batch_size * seq_len, vocab_size]

        # decoder_targets：[batch_size, seq_len] -> [batch_size * seq_len]
        decoder_targets = decoder_targets.reshape(-1)

        loss = loss_fn(decoder_outputs, decoder_targets)

        # 反向传播
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        total_loss += loss.item()

    return total_loss / len(dataloader)


def train():
    # 1. 设备
    # 2. 数据
    dataloader = get_dataloader()
    # 3. 分词器
    zh_tokenizer = ChineseTokenizer.from_vocab(config.MODELS_DIR / 'zh_vocab.txt')
    en_tokenizer = EnglishTokenizer.from_vocab(config.MODELS_DIR / 'en_vocab.txt')
    # 4. 模型
    model = TranslationModel(zh_tokenizer.vocab_size, en_tokenizer.vocab_size, zh_tokenizer.pad_token_index,
                             en_tokenizer.pad_token_index)
    # 5. 损失函数
    loss_fn = torch.nn.CrossEntropyLoss(ignore_index=en_tokenizer.pad_token_index)
    # 6. 优化器
    optimizer = torch.optim.Adam(model.parameters(), lr=config.LEARNING_RATE)
    # 7. TensorBoard Writer
    writer = SummaryWriter(log_dir=config.LOGS_DIR / time.strftime('%Y-%m-%d_%H-%M-%S'))

    best_loss = float('inf')
    for epoch in range(1, config.EPOCHS + 1):
        print(f'========== Epoch {epoch} ==========')
        loss = train_one_epoch(model, dataloader, loss_fn, optimizer)
        print(f'Loss: {loss:.4f}')

        # 记录到Tensorboard
        writer.add_scalar('Loss', loss, epoch)

        # 保存模型
        if loss < best_loss:
            best_loss = loss
            torch.save(model.state_dict(), config.MODELS_DIR / 'best.pt')
            print('保存模型')

    writer.close()


if __name__ == '__main__':
    train()
