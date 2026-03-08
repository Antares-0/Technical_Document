import torch
import config
from model import InputMethodModel
from dataset import get_dataloader
from predict import predict_batch
from tokenizer import JiebaTokenizer


def evaluate(model, test_dataloader):
    top1_acc_count = 0
    top5_acc_count = 0
    total_count = 0
    for inputs, targets in test_dataloader:
        # inputs.shape: [batch_size, seq_len]
        targets = targets.tolist()
        # targets.shape: [batch_size] e.g.[1,3,5]
        top5_indexes_list = predict_batch(model, inputs)
        # top5_indexes_list.shape: [batch_size, 5] e.g. [[1,3,5,7,8],[1,3,5,7,8],[1,3,5,7,8]]
        for target, top5_indexes in zip(targets, top5_indexes_list):
            total_count += 1
            if target == top5_indexes[0]:
                top1_acc_count += 1
            if target in top5_indexes:
                top5_acc_count += 1
    return top1_acc_count / total_count, top5_acc_count / total_count


def run_evaluate():
    # 准备资源
    # 1. 确定设备

    # 2.词表
    tokenizer = JiebaTokenizer.from_vocab(config.MODELS_DIR / 'vocab.txt')
    print("词表加载成功")

    # 3. 模型
    model = InputMethodModel(vocab_size=tokenizer.vocab_size)
    model.load_state_dict(torch.load(config.MODELS_DIR / 'best.pth'))
    print("模型加载成功")

    # 4. 数据集
    test_dataloader = get_dataloader(train=False)

    # 5.评估逻辑
    top1_acc, top5_acc = evaluate(model, test_dataloader)
    print("评估结果")
    print(f"top1_acc: {top1_acc}")
    print(f"top5_acc: {top5_acc}")


if __name__ == '__main__':
    run_evaluate()
