import jieba
import torch
import config
from model import InputMethodModel
from src.tokenizer import JiebaTokenizer


def predict_batch(model, inputs):
    """
    批量预测
    :param model: 模型
    :param inputs: 输入,shape:[batch_size, sql_len]
    :return: 预测结果,shape:[batch_size,5]
    """
    model.eval()
    with torch.no_grad():
        output = model(inputs)
        # output.shape: [batch_size, vocab_size]
    top5_indexes = torch.topk(output, k=5).indices
    # top5_indexes.shape: [batch_size, 5]

    top5_indexes_list = top5_indexes.tolist()
    return top5_indexes_list


def predict(text, model, tokenizer):
    # 1. 处理输入
    indexes = tokenizer.encode(text)
    input_tensor = torch.tensor([indexes], dtype=torch.long)
    # input_tensor.shape: [batch_size, seq_len]

    # 2.预测逻辑
    top5_indexes_list = predict_batch(model, input_tensor)
    top5_tokens = [tokenizer.index2word[index] for index in top5_indexes_list[0]]
    return top5_tokens


def run_predict():
    # 准备资源
    # 1. 确定设备
    # pass

    # 2.词表
    tokenizer = JiebaTokenizer.from_vocab(config.MODELS_DIR / 'vocab.txt')
    print("词表加载成功")

    # 3. 模型
    model = InputMethodModel(vocab_size=tokenizer.vocab_size)
    model.load_state_dict(torch.load(config.MODELS_DIR / 'best.pth'))
    print("模型加载成功")

    print("欢迎使用输入法模型(输入q或者quit退出)")
    input_history = ''
    while True:
        user_input = input("> ")
        if user_input in ['q', 'quit']:
            print("欢迎下次再来")
            break
        if user_input.strip() == '':
            print("请输入内容")
            continue
        input_history += user_input
        print(f'输入历史:{input_history}')
        top5_tokens = predict(input_history, model, tokenizer)
        print(f'预测结果:{top5_tokens}')


if __name__ == '__main__':
    run_predict()
