import torch
from torch import nn
import config


class MyModel(nn.Module):
    def __init__(self, vocab_size, padding_index):
        super(MyModel, self).__init__()
        # padding_idx 指明pad的索引
        self.embedding = nn.Embedding(vocab_size, config.EMBEDDING_DIM, padding_idx=padding_index)
        self.lstm = nn.LSTM(input_size=config.EMBEDDING_DIM,
                            hidden_size=config.HIDDEN_SIZE,
                            batch_first=True)
        self.linear = nn.Linear(config.HIDDEN_SIZE, 1)

    def forward(self, x: torch.Tensor):
        # x的形状[batch_size, seq_len]
        embed = self.embedding(x)
        output, (_,_) = self.lstm(embed)
        # 存在<pad>，怎么获取最后一个非零的合法状态呢
        batch_indexes = torch.arange(0, output.shape[0])
        lengths = (x != self.embedding.padding_idx).sum(dim=1)
        last_hidden = output[batch_indexes, lengths - 1]
        output = self.linear(last_hidden).squeeze(-1)
        return output