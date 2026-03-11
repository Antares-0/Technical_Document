import torch
import config
from model import MyModel
from dataset import get_dataloader
from predict import predict_batch
from tokenizer import JiebaTokenizer


def evaluate(model, test_dataloader, device):
    total_count = 0
    correct_count = 0
    for inputs, targets in test_dataloader:
        inputs = inputs.to(device)
        # inputs.shape: [batch_size, seq_len]
        targets = targets.tolist()
        # targets.shape: [batch_size] e.g.[0,1,0,1]
        batch_result = predict_batch(model, inputs)
        # batch_result.shape: [batch_size] e.g. [0.1, 0.2, 0.9, 0.3]

        for result, target in zip(batch_result, targets):
            result = 1 if result > 0.5 else 0
            if result == target:
                correct_count += 1
            total_count += 1
    return correct_count / total_count


def run_evaluate():
    # 准备资源
    # 1. 确定设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # 2.词表
    tokenizer = JiebaTokenizer.from_vocab(config.MODELS_DIR / 'vocab.txt')
    print("词表加载成功")

    # 3. 模型
    model = MyModel(vocab_size=tokenizer.vocab_size, padding_index=tokenizer.pad_token_index).to(device)
    model.load_state_dict(torch.load(config.MODELS_DIR / 'best.pt'))
    print("模型加载成功")

    # 4. 数据集
    test_dataloader = get_dataloader(train=False)

    # 5.评估逻辑
    acc = evaluate(model, test_dataloader, device)
    print("评估结果")
    print(f"acc: {acc}")


if __name__ == '__main__':
    run_evaluate()
