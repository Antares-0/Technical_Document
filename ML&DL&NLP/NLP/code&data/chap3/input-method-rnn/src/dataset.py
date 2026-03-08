# 1.定义Dataset
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
import config


class InputMethodDataset(Dataset):
    def __init__(self, path):
        self.data = pd.read_json(path, lines=True, orient='records').to_dict(orient='records')

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        input_tensor = torch.tensor(self.data[index]['input'], dtype=torch.long)
        target_tensor = torch.tensor(self.data[index]['target'], dtype=torch.long)
        return input_tensor, target_tensor


# 2. 提供一个获取dataloader的方法
def get_dataloader(train=True):
    path = config.PROCESSED_DATA_DIR / ('train.jsonl' if train else 'test.jsonl')
    dataset = InputMethodDataset(path)
    return DataLoader(dataset, batch_size=config.BATCH_SIZE, shuffle=True)


if __name__ == '__main__':
    train_dataloader = get_dataloader()
    test_dataloader = get_dataloader(train=False)
    print(len(train_dataloader))
    print(len(test_dataloader))

    for input_tensor, target_tensor in train_dataloader:
        # 这里的数据是词向量的编号，不是真正的词向量，后面的enbeding层将
        print(input_tensor.shape)  # input_tensor.shape: [batch_size, seq_len]
        print(target_tensor.shape)  # target_tensor.shape : [batch_size]
        break
