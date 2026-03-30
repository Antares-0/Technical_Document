from datasets import load_dataset, ClassLabel
from transformers import AutoTokenizer

import config


def process():
    print("start process")
    filePath = str(config.RAW_DATA_DIR / 'online_shopping_10_cats.csv')
    dataset = load_dataset('csv', data_files=filePath)['train']

    # 过滤数据
    dataset = dataset.remove_columns(['cat'])
    dataset = dataset.filter(lambda x: x['review'] is not None)

    # 类型转换，分层抽样类型
    dataset = dataset.cast_column('label', ClassLabel(names=['negative', 'positive']))

    # 划分数据集
    # 按照label列进行分层抽样
    dataset_dict = dataset.train_test_split(test_size=0.2, stratify_by_column='label')
    print(dataset_dict)

    # 创建tokenizer
    tokenizer = AutoTokenizer.from_pretrained(config.PRE_TRAINED_DIR/'bert-base-chinese')

    # 处理数据
    def batch_encode(batch):
        inputs = tokenizer(batch['review'], padding='max_length', truncation=True, max_length=config.SEQ_LEN)
        inputs['labels'] = batch['label']
        return inputs


    dataset_dict = dataset_dict.map(batch_encode, batched=True, remove_columns=['review', 'label'])
    dataset_dict.save_to_disk(config.PROCESSED_DATA_DIR)
    print("finish process")


if __name__ == "__main__":
    process()
