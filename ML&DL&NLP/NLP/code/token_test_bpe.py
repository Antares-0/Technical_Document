from transformers import AutoTokenizer
from collections import defaultdict

# 计算单词的出现频率
def compute_pair_freqs(splits):
    pair_freqs = defaultdict(int)
    for word, freq in word_freqs.items():
        split = splits[word]
        if len(split) == 1:
            continue
        for i in range(len(split) - 1):
            pair = (split[i], split[i + 1])
            pair_freqs[pair] += freq
    return pair_freqs

# 合并词表 u, n, [u n p] --> [un p]
def merge_pair(a, b, splits):
    for word in word_freqs:
        split = splits[word]
        i = 0
        while i < len(split) - 1:
            if split[i] == a and split[i + 1] == b:
                split = split[:i] + [a + b] + split[i + 2 :]
            else:
                i += 1
        splits[word] = split
    return splits

# 应用分词器进行分词
def tokenize(text):
    pre_tokenize_result = tokenizer._tokenizer.pre_tokenizer.pre_tokenize_str(text)
    pre_tokenized_text = [word for word, offset in pre_tokenize_result]
    splits = [[l for l in word] for word in pre_tokenized_text]
    for pair, merge in merges.items():
        for idx, split in enumerate(splits):
            i = 0
            while i < len(split) - 1:
                if split[i] == pair[0] and split[i + 1] == pair[1]:
                    split = split[:i] + [merge] + split[i + 2 :]
                else:
                    i += 1
            splits[idx] = split
    print(splits)
    return sum(splits, [])

# 学习语料库
textList = [
    "This is the Hugging Face Course.",
    "This chapter is about tokenization.",
    "This section shows several tokenizer algorithms.",
    "Hopefully, you will be able to understand how they are trained and generate tokens.",
]

tokenizer = AutoTokenizer.from_pretrained("gpt2")

word_freqs = defaultdict(int)

# 统计词频，每个单词在textList中出现了多少次
for text in textList:
    words_with_offsets = tokenizer.backend_tokenizer.pre_tokenizer.pre_tokenize_str(text)
    new_words = [word for word, offset in words_with_offsets]
    for word in new_words:
        word_freqs[word] += 1

# 计算基础词表
alphabet = []
for word in word_freqs.keys():
    for letter in word:
        if letter not in alphabet:
            alphabet.append(letter)
alphabet.sort()

# 添加一个特殊的token
merges = {}
vocab = ["<|endoftext|>"] + alphabet.copy()

# 将单词切开变成字典，
# bpn = b p n
splits = {word: [c for c in word] for word in word_freqs.keys()}

# 计算相邻的两个token之间的出现频率
pair_freqs = compute_pair_freqs(splits)

# 制定词表上限，进行迭代唇环
vocab_size = 50

while len(vocab) < vocab_size:
    pair_freqs = compute_pair_freqs(splits)
    best_pair = ""
    max_freq = None
    for pair, freq in pair_freqs.items():
        if max_freq is None or max_freq < freq:
            best_pair = pair
            max_freq = freq
    splits = merge_pair(*best_pair, splits)
    merges[best_pair] = best_pair[0] + best_pair[1]
    vocab.append(best_pair[0] + best_pair[1])

# 输出当前词表
print(vocab)
# 输出所有合并规则
print(merges)

# 应用分词
tokenize("This is not a token.")
