from datasets import load_from_disk
from torch.utils.data import DataLoader

import config

def get_dataloader(train=True):
    path = str(config.PROCESSED_DATA_DIR / ('train' if train else 'test'))
    dataset = load_from_disk(path)
    dataset.set_format(type='torch')
    return DataLoader(dataset, batch_size=config.BATCH_SIZE, shuffle=True)


if __name__ == "__main__":
    train_loader = get_dataloader(train=True)
    test_loader = get_dataloader(train=False)
    print(len(train_loader))
    print(len(test_loader))

    for batch in train_loader:
        for k, v in batch.items():
            print(k, v.shape)