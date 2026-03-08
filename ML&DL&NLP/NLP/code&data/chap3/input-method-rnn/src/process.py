import jieba
import pandas as pd
from sklearn.model_selection import train_test_split
from tqdm import tqdm
from tokenizer import JiebaTokenizer
import config


def build_dataset(sentences, tokenizer):
    indexed_sentences = [tokenizer.encode(sentence) for sentence in sentences]

    dataset = []
    # [{'input':[1,2,3,4,5],'target':5},{'input':[2,3,4,5,6],'target':7}]
    for sentence in tqdm(indexed_sentences, desc="构建数据集"):
        for i in range(len(sentence) - config.SEQ_LEN):
            input = sentence[i:i + config.SEQ_LEN]
            target = sentence[i + config.SEQ_LEN]
            dataset.append({'input': input, 'target': target})
    return dataset


def process():
    print("开始处理数据")
    # 1.读取文件
    df = pd.read_json(config.RAW_DATA_DIR / "synthesized_.jsonl", lines=True,
                      orient="records").sample(frac=0.01)

    # 2.提取句子
    sentences = []
    for dialog in df['dialog']:
        for sentence in dialog:
            sentences.append(sentence.split('：')[1])
    print(f'句子总数:{len(sentences)}')

    # 3.划分数据集
    train_sentences, test_sentences = train_test_split(sentences, test_size=0.2)

    # 4.构建词表
    JiebaTokenizer.build_vocab(train_sentences, config.MODELS_DIR / 'vocab.txt')

    # 6.构建训练集
    tokenizer = JiebaTokenizer.from_vocab(config.MODELS_DIR / 'vocab.txt')
    train_dataset = build_dataset(train_sentences, tokenizer)

    # 7.保存训练集
    pd.DataFrame(train_dataset).to_json(config.PROCESSED_DATA_DIR / 'train.jsonl', orient='records', lines=True)

    # 8.构建测试集
    test_dataset = build_dataset(test_sentences, tokenizer)

    # 9.保存测试集
    pd.DataFrame(test_dataset).to_json(config.PROCESSED_DATA_DIR / 'test.jsonl', orient='records', lines=True)

    print("数据处理完成")


if __name__ == '__main__':
    process()
