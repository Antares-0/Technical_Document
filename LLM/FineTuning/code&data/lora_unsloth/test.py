import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["UNSLOTH_MODELSCOPE"] = "0"
from peft import PeftModel
from unsloth import FastLanguageModel

local_model_path="pretrained/unsloth/Qwen3-0.6B-unsloth-bnb-4bit"
lora_path = "trained_models/unsloth"
myModel, tokenizer = FastLanguageModel.from_pretrained(
    local_files_only = True,
    model_name=local_model_path,
    max_seq_length=2048,
    device_map='auto',
    dtype=None,
    load_in_4bit=True,
    load_in_8bit=False,
    full_finetuning=False,
)

myModel = PeftModel.from_pretrained(myModel, lora_path)
myModel = myModel.to(myModel.device)

FastLanguageModel.for_inference(myModel)
myModel.eval()

messages = [
    {"role": "user", "content": "关键词识别：\n采用粉末冶金结合热等静压技术制备27%-38%-50%Si/Al三层准梯度硅铝合金，研究其组织、弯曲和冲击性能，分析冲击断口形貌和形成机理。结果表明，热等静压后，梯度硅铝合金接近完全致密，组织细小均匀，梯度层方向抗弯强度最高能达到314 MPa,高于其垂直方向最大的258 MPa。冲击试验显示材料较大的脆性，冲击断口显示梯度材料多重断口特征。"}
]

formatMessage = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
)

inputs = tokenizer(formatMessage, return_tensors="pt").to(myModel.device)

outputs = myModel.generate(**inputs, max_new_tokens=1024)

res = tokenizer.decode(outputs[0], skip_special_tokens=True)

print(res)


