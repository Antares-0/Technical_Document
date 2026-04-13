from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TextStreamer
)
import torch
from peft import PeftModel

local_model_path = '/root/autodl-tmp/pretrained/Qwen/Qwen3-8B'
lora_adapter_path = '/root/autodl-tmp/outputs/Qwen3-8B-sft-lora-adapter'

# 1、加载基座模型、tokenizer
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,  # 启用4-bit量化
    bnb_4bit_quant_type="nf4",  # 量化类型
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True  # 嵌套量化节省更多内存
)

# 加载模型
model = AutoModelForCausalLM.from_pretrained(
    local_model_path,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)
# 加载分词器
tokenizer = AutoTokenizer.from_pretrained(
    local_model_path,
    trust_remote_code=True
)

# 注入lora适配器
model = PeftModel.from_pretrained(model,lora_adapter_path)
# model.merge_and_unload()
model.eval()
# print(model)

# 3、构造数据  {text:<im_start>\nsystem....<im_end>} ==> tokenizer.apply_chat_template
messages = [
    {"role": "user",
     "content": "关键词识别：\n梯度功能材料是基于一种全新的材料设计概念而开发的新型功能材料.陶瓷-金属FGM的主要结构特点是各梯度层由不同体积浓度的陶瓷和金属组成,材料在升温和降温过程中宏观梯度层间产生热应力,每一梯度层中细观增强相和基体的热物性失配将产生单层热应力,从而导致材料整体的破坏.采用云纹干涉法,对具有四个梯度层的SiC/A1梯度功能材料分别在机载、热载及两者共同作用下进行了应变测试,分别得到了这三种情况下每梯度层同一位置的纵向应变,横向应变和剪应变值."}
]
"""
期待回复："云纹干涉法;梯度功能材料;应变;热载荷"
"""
format_messages = tokenizer.apply_chat_template(
    messages,
    tokenize=False,  # 训练时部分词，true返回的是张量
    add_generation_prompt=True,  # 训练期间要关闭，如果是推理则设为True
)

# 4、调用tokenizer得到input
inputs = tokenizer(format_messages, return_tensors='pt').to(model.device)

# 5、调用model.generate()  ======== 一次性输出
outputs = model.generate(
    **inputs,
    max_new_tokens=1024,
)
# 只输出回答部分
response = tokenizer.decode(outputs[0][inputs.input_ids.shape[-1]:], skip_special_tokens=True)
print(response)

# 5、调用model.generate()  ======== 流式输出
# streamer = TextStreamer(tokenizer,skip_prompt=True,skip_special_tokens=True)
# outputs = model.generate(
#     **inputs,
#     max_new_tokens=1024,
#     streamer=streamer,
# )
