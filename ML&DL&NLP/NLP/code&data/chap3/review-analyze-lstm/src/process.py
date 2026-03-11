import pandas as pd
from sklearn.model_selection import train_test_split
from tokenizer import JiebaTokenizer
import config


def process():
    # 读取文件
    df = pd.read_csv(config.RAW_DATA_DIR / 'online_shopping_10_cats.csv', usecols=['label', 'review'], encoding='utf-8').dropna().sample(frac=0.1)
    # 划分数据集，stratify参数表示按照label分层抽样
    train_df, test_df = train_test_split(df, test_size=0.2, stratify=df['label'], random_state=42)
    # 构建词表
    JiebaTokenizer.build_vocab(train_df['review'].tolist(), config.MODELS_DIR / 'vocab.txt')


    tokenizer = JiebaTokenizer.from_vocab(config.MODELS_DIR / 'vocab.txt')

    # 构建训练集
    train_df['review'] = train_df['review'].apply(lambda x: tokenizer.encode(x, config.SEQ_LEN))
    # 保存训练集合
    train_df.to_json(config.PROCESSED_DATA_DIR / 'train.jsonl', orient='records', lines=True)

    # 构建测试集
    test_df['review'] = test_df['review'].apply(lambda x: tokenizer.encode(x, config.SEQ_LEN))
    # 保存测试集
    test_df.to_json(config.PROCESSED_DATA_DIR / 'test.jsonl', orient='records', lines=True)


if __name__ == '__main__':
    process()