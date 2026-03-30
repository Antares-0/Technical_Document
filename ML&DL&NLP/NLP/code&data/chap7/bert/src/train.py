import torch
from datasets import tqdm
from transformers import AutoTokenizer
from model import MyModel
import config

from dataset import get_dataloader

def train_one_epoch(model, dataloader, loss_fn, optimizer):
    total_loss = 0
    model.train()
    for batch in tqdm(dataloader, desc='训练'):

        inputs = {k: v for k,v in batch.items()}
        labels= inputs.pop('labels').to(dtype=torch.float)

        outputs = model(**inputs)
        # outputs.shape: [batch_size]
        loss = loss_fn(outputs, labels)

        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        total_loss += loss.item()
    return total_loss / len(dataloader)

def train():
    dataloader = get_dataloader()
    tokenizer = AutoTokenizer.from_pretrained(config.PRE_TRAINED_DIR/'bert-base-chinese')
    model = MyModel()
    loss_fn = torch.nn.CrossEntropyLoss()
    # 参数越多，学习率要越小
    optimizer = torch.optim.Adam(model.parameters(), lr=config.LEARNING_RATE)

    best_loss = float('inf')
    for epoch in range(1, config.EPOCHS + 1):
        print(f'========== Epoch {epoch} ==========')
        loss = train_one_epoch(model, dataloader, loss_fn, optimizer)
        print(f'Loss: {loss:.4f}')

        # 保存模型
        if loss < best_loss:
            best_loss = loss
            torch.save(model.state_dict(), config.MODELS_DIR / 'best.pt')
            print('保存模型')

if __name__ == '__main__':
    train()