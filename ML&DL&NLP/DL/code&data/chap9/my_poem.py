import torch
from torch import nn, optim
from torch.nn import CrossEntropyLoss
from torch.utils.data import DataLoader, Dataset

# 正则化库
import re

# 文件预处理
def preprocess_poems(file_path):
    # 定义字的集合
    char_set = set()
    # 定义诗id之后的列表
    poems = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            # 数据清洗
            line = re.sub(r'[，。？！、：]', "", line).strip()
            # 将文本拆分成字
            char_set.update(line)
            poems.append(list(line))

    # 构建词表
    id2word = list(char_set) + ["<UNK>"]
    word2id = {word: id for id, word in enumerate(id2word)}

    # 将诗句id化
    id_seqs = []
    for poem in poems:
        id_seq = [ word2id.get(word) for word in poem ]
        id_seqs.append(id_seq)
    return id_seqs, id2word, word2id

# 构建训练数据集
class PoetryDataset(Dataset):
    # 初始化：传入原诗的id列表，以及序列长度L
    def __init__(self, id_seqs, seq_len):
        self.seq_len = seq_len
        self.data = []  # 保存数据元组（x, y）的列表
        # 遍历所有诗
        for id_seq in id_seqs:
            # 遍历当前诗的所有字（id）
            for i in range(0, len(id_seq) - self.seq_len):
                # 以当前字id为起始，截取x和y序列
                # 使用前6个字 床前明月光疑 预测 前明月光疑是 后六个字，所以x是前面，y是x的窗口后移1的
                self.data.append( (id_seq[i:i+self.seq_len], id_seq[i+1:i+1+self.seq_len]) )
    # 返回数据集的大小
    def __len__(self):
        return len(self.data)
    # 通过索引idx获取元素值
    def __getitem__(self, idx):
        x = torch.LongTensor(self.data[idx][0])
        y = torch.LongTensor(self.data[idx][1])
        return x, y

# 创建预测模型
class MyPoemNN(nn.Module):
    def __init__(self, vocab_size, embedding_size, hidden_size, num_layers=1):
        super(MyPoemNN, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_size)
        # N * L * 词向量
        self.RNN = nn.RNN(embedding_size, hidden_size, num_layers, batch_first=True)
        self.linear = nn.Linear(hidden_size, vocab_size)

    # 定义前向传播
    def forward(self, input, hx=None):
        embedding = self.embedding(input)
        output, hx = self.RNN(embedding, hx)
        output = self.linear(output)
        return output, hx

# 开始训练
def train(model, dataset, lr, epoch_num, batch_size):
    # 开启训练模式
    model.train()
    loss = CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    # 开启迭代
    for epoch in range(epoch_num):
        train_loss = 0
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        for batch_idx, (x, y) in enumerate(dataloader):
            # 预测
            predict, _ = model(x)
            # 计算损失
            loss_value = loss(predict.transpose(1,2), y)
            # 损失反向传播计算梯度
            loss_value.backward()
            # 更新参数
            optimizer.step()
            # 梯度清零
            optimizer.zero_grad()
            train_loss += loss_value.detach().item() * x.shape[0]
            print(f"\rEpoch:{epoch + 1:0>2}[{'=' * int((batch_idx + 1) / len(dataloader) * 50)}]", end="")

        # 计算本轮损失
        this_loss = train_loss / len(dataset)
        print(f"train loss: {this_loss:.4f}")




# 主流程
id_seqs, id2word, word2id = preprocess_poems("poems.txt")
dataset = PoetryDataset(id_seqs, 24)

# 创建模型
model = MyPoemNN(len(word2id), 256, 128, num_layers=2)

lr = 1e-3
epoch_num = 20
batch_size = 32
train(model, dataset, lr, epoch_num, batch_size)

# 训练的时候使用固定24的长度，但是输出的时候不依赖固定长度
# 生成新诗
def generate(model, id2word, word2id, start_token, line_num=4, line_len=7):
    # 模型测试
    poems = []
    model.eval()
    start_token_log = start_token
    for i in range(line_num):
        # 忽略不存在的情况
        start_id = word2id[start_token_log]
        for j in range(line_len):
            # 定义输入数据
            input = torch.LongTensor([[start_id]])
            with torch.no_grad():
                output, _ = model(input)
                # softmax计算概率值
                prob = torch.softmax(output[0,0], dim=-1)
                # 基于概率分布，获得下一个
                next_id = torch.multinomial(prob, num_samples=1)
                poem_word = id2word[next_id]
            poems.append(poem_word)
            start_id = word2id[poem_word]
            if j == line_len - 1:
                poems.append(",")
        start_token_log = id2word[start_id]

    return poems


poem = generate(model, id2word, word2id, start_token="与")
print(poem)





