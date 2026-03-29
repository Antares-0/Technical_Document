import jieba
import torch
from transformers import AutoTokenizer

import config
from model import MyModel


def predict_batch(model, inputs):
    """
    批量预测
    :param model: 模型
    :param inputs: 输入,shape:[batch_size, sql_len]
    :return: 预测结果,shape:[batch_size]
    """
    model.eval()
    with torch.no_grad():
        output = model(**inputs)
        # output.shape: [batch_size]
    batch_result = torch.sigmoid(output)
    return batch_result.tolist()


def predict(text, model, tokenizer):
    # 1. 处理输入
    inputs =  tokenizer(text,padding='max_length', truncation=True,max_length=config.SEQ_LEN,return_tensors='pt')

    # 2.预测逻辑
    inputs = {k: v for k, v in inputs.items()}
    batch_result = predict_batch(model, inputs)

    return batch_result[0]


def run_predict():
    # 准备资源


    # 2. 分词器
    tokenizer = AutoTokenizer.from_pretrained(config.PRE_TRAINED_DIR/'bert-base-chinese')
    # 3. 模型
    model = MyModel()
    model.load_state_dict(torch.load(config.MODELS_DIR / 'best.pt'))
    print("模型加载成功")

    print("欢迎情感分析模型(输入q或者quit退出)")

    while True:
        user_input = input("> ")
        if user_input in ['q', 'quit']:
            print("欢迎下次再来")
            break
        if user_input.strip() == '':
            print("请输入内容")
            continue

        result = predict(user_input, model, tokenizer)
        if result > 0.5:
            print(f"正向（置信度：{result}）")
        else:
            print(f"负向（置信度：{1 - result}）")


if __name__ == '__main__':
    run_predict()
