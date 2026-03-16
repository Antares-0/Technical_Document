import torch

import config
from model import TranslationModel
from tokenizer import ChineseTokenizer, EnglishTokenizer


def predict_batch(model, inputs, en_tokenizer):
    """
    批量预测
    :param model: 模型
    :param inputs: 输入,shape:[batch_size, seq_len]
    :return: 预测结果: [[*,*,*,*,*],[*,*,*,*],[*,*,*]]
    """
    model.eval()
    with torch.no_grad():
        # 编码
        encoder_outputs, context_vector = model.encoder(inputs)
        # context_vector.shape: [batch_size, hidden_size]

        # 解码
        batch_size = inputs.shape[0]
        device = inputs.device

        # 隐藏状态
        decoder_hidden = context_vector.unsqueeze(0)
        # decoder_hidden.shape: [1, batch_size, hidden_size]
        decoder_input = torch.full([batch_size, 1], en_tokenizer.sos_token_index, device=device)
        # decoder_input.shape: [batch_size, 1]

        # 预测结果缓存
        generated = []

        # 记录每个样本是否已经生成结束符
        is_finished = torch.full([batch_size], False, device=device)

        # 自回归生成
        for i in range(config.MAX_SEQ_LENGTH):
            # 解码
            decoder_output, decoder_hidden = model.decoder(decoder_input, decoder_hidden, encoder_outputs)
            # decoder_output.shape: [batch_size, 1, vocab_size]

            # 保存预测结果
            next_token_indexes = torch.argmax(decoder_output, dim=-1)
            # next_token_indexes.shape: [batch_size, 1]
            generated.append(next_token_indexes)

            # 更新输入(decoder_input)
            decoder_input = next_token_indexes

            # 判断是否应该结束
            is_finished |= (next_token_indexes.squeeze(1) == en_tokenizer.eos_token_index)
            if is_finished.all():
                break

        # 处理预测结果
        # 整理预测结果形状
        # generated：[tensor([batch_size, 1])]
        generated_tensor = torch.cat(generated, dim=1)
        # generated_tensor.shape: [batch_size,seq_len]
        generated_list = generated_tensor.tolist()
        # generated_list：[[*,*,*,*,*],[*,*,*,eos,*],[*,*,eos,*,*]]

        # 去掉eos之后的token id
        for index, sentence in enumerate(generated_list):
            if en_tokenizer.eos_token_index in sentence:
                eos_pos = sentence.index(en_tokenizer.eos_token_index)
                generated_list[index] = sentence[:eos_pos]
        # generated_list：[[*,*,*,*,*],[*,*,*],[*,*]]
        return generated_list


def predict(text, model, zh_tokenizer, en_tokenizer, device):
    # 1. 处理输入
    indexes = zh_tokenizer.encode(text)
    input_tensor = torch.tensor([indexes], dtype=torch.long)
    input_tensor = input_tensor.to(device)
    # input_tensor.shape: [batch_size, seq_len]

    # 2.预测逻辑
    batch_result = predict_batch(model, input_tensor, en_tokenizer)
    return en_tokenizer.decode(batch_result[0])


def run_predict():
    # 准备资源
    # 1. 确定设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # 2.分词器
    zh_tokenizer = ChineseTokenizer.from_vocab(config.MODELS_DIR / 'zh_vocab.txt')
    en_tokenizer = EnglishTokenizer.from_vocab(config.MODELS_DIR / 'en_vocab.txt')
    print("分词器加载成功")

    # 3. 模型
    model = TranslationModel(zh_tokenizer.vocab_size, en_tokenizer.vocab_size, zh_tokenizer.pad_token_index,
                             en_tokenizer.pad_token_index).to(device)
    model.load_state_dict(torch.load(config.MODELS_DIR / 'best.pt'))
    print("模型加载成功")

    print("欢迎使用中英翻译模型(输入q或者quit退出)")

    while True:
        user_input = input("中文：")
        if user_input in ['q', 'quit']:
            print("欢迎下次再来")
            break
        if user_input.strip() == '':
            print("请输入内容")
            continue

        result = predict(user_input, model, zh_tokenizer, en_tokenizer, device)
        print("英文：", result)


if __name__ == '__main__':
    run_predict()
