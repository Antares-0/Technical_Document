import os

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from transformers import AutoModelForCausalLM, TrainingArguments, Trainer, AutoTokenizer
from datasets import load_dataset

modelName = 'gpt2'
max_seq_len = 64

# 分词器
tokenizer = AutoTokenizer.from_pretrained(modelName)
tokenizer.pad_token = tokenizer.eos_token

# 模型
model = AutoModelForCausalLM.from_pretrained(modelName)
model.config.pad_token_id = tokenizer.pad_token_id

# 加载数据
ds = load_dataset("glue", "sst2")
ds_train = ds['train']
ds_test = ds['validation']


# ===================== 终极修复：关闭 batched，逐行处理 =====================
def tokenize_function(example):
    sent = example["sentence"]
    # 分词
    enc = tokenizer(
        sent,
        truncation=True,
        padding="max_length",
        max_length=max_seq_len,
    )
    enc["labels"] = enc["input_ids"]
    return enc


tokenized_train = ds_train.map(tokenize_function, batched=False)
tokenized_test = ds_test.map(tokenize_function, batched=False)

# 训练参数
training_args = TrainingArguments(
    output_dir="./gpt2-sft",
    num_train_epochs=1,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    gradient_checkpointing=True,
    fp16=False,
    logging_steps=10,
    eval_strategy="epoch",
    save_strategy="epoch",
    report_to="none",
    dataloader_num_workers=0,
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_test,
)

# 开始训练 ✅
trainer.train()
trainer.save_model("./gpt2-sft-final")
print("🎉 训练成功！")
