import torch
from torch import nn
import config


class TranslationEncoder(nn.Module):
    def __init__(self, vocab_size, padding_index):
        super().__init__()
        self.embedding = nn.Embedding(num_embeddings=vocab_size,
                                      embedding_dim=config.EMBEDDING_DIM,
                                      padding_idx=padding_index)

        self.gru = nn.GRU(input_size=config.EMBEDDING_DIM,
                          hidden_size=config.HIDDEN_SIZE,
                          batch_first=True)

    def forward(self, x):
        # x.shape: [batch_size, seq_len]
        embed = self.embedding(x)
        # embed.shape: [batch_size, seq_len, embedding_dim]
        output, _ = self.gru(embed)
        # output.shape: [batch_size, seq_len, hidden_size]

        lengths = (x != self.embedding.padding_idx).sum(dim=1)
        last_hidden_state = output[torch.arange(output.shape[0]), lengths - 1]
        # last_hidden_state.shape: [batch_size, hidden_size]
        return last_hidden_state


class TranslationDecoder(nn.Module):
    def __init__(self, vocab_size, padding_index):
        super().__init__()
        self.embedding = nn.Embedding(num_embeddings=vocab_size,
                                      embedding_dim=config.EMBEDDING_DIM,
                                      padding_idx=padding_index)

        self.gru = nn.GRU(input_size=config.EMBEDDING_DIM,
                          hidden_size=config.HIDDEN_SIZE,
                          batch_first=True)

        self.linear = nn.Linear(in_features=config.HIDDEN_SIZE,
                                out_features=vocab_size)

    # 前向传播写的是单次的
    def forward(self, x, hidden_0):
        # x.shape: [batch_size, 1]
        # hidden.shape: [1, batch_size, hidden_size]
        embed = self.embedding(x)
        # embed.shape: [batch_size, 1, embedding_dim]
        output, hidden_n = self.gru(embed, hidden_0)
        # output.shape: [batch_size, 1, hidden_size]
        output = self.linear(output)
        # output.shape: [batch_size, 1, vocab_size]
        return output, hidden_n


class TranslationModel(nn.Module):
    def __init__(self, zh_vocab_size, en_vocab_size, zh_padding_index, en_padding_index):
        super().__init__()
        self.encoder = TranslationEncoder(vocab_size=zh_vocab_size, padding_index=zh_padding_index)
        self.decoder = TranslationDecoder(vocab_size=en_vocab_size, padding_index=en_padding_index)
