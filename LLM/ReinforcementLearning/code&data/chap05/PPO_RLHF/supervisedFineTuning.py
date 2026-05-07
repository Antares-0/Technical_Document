from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, DataCollatorForLanguageModeling
import torch
from datasets import load_dataset

model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

dataset_path = "glue"
ds = load_dataset(dataset_path, "sst2")
ds_train, ds_test = ds['train'], ds['validation']

# ====================== 新增：Tokenizer 配置（必须） ======================
tokenizer.pad_token = tokenizer.eos_token  # gpt2 没有pad，用eos代替
model.config.pad_token_id = model.config.eos_token_id


# ====================== 新增：数据预处理函数 ======================
def preprocess_function(examples):
    # 构造指令格式（让因果LM做情感分类）
    texts = [
        f"Sentence: {sentence}\nSentiment: {'positive' if label == 1 else 'negative'}"
        for sentence, label in zip(examples['sentence'], examples['label'])
    ]

    # 分词
    tokenized = tokenizer(
        texts,
        truncation=True,
        max_length=128,
        padding="max_length",
        return_tensors="pt"
    )

    # 标签 = 输入_ids（语言模型自监督训练）
    tokenized["labels"] = tokenized["input_ids"].clone()
    return tokenized


# 对训练集 / 测试集批量预处理
tokenized_train = ds_train.map(preprocess_function, batched=True)
tokenized_test = ds_test.map(preprocess_function, batched=True)

# 数据收集器（自动做因果语言建模掩码）
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False  # GPT2 是自回归，不是掩码LM
)

# ====================== 新增：训练参数 ======================
training_args = TrainingArguments(
    output_dir="./gpt2-sst2-finetuned",
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    learning_rate=2e-5,
    num_train_epochs=2,
    weight_decay=0.01,

    # 旧版 transformers 用这个，不是 evaluation_strategy！
    eval_strategy="epoch",

    save_strategy="epoch",
    logging_steps=10,
    fp16=False,  # Mac 没有 CUDA，必须关
    push_to_hub=False,
    report_to="none",  # 避免 wandb 报错
)

# ====================== 新增：Trainer 训练 ======================
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_test,
    data_collator=data_collator,
)

# 开始训练
trainer.train()

# ====================== 训练完成：保存模型 ======================
model.save_pretrained("./gpt2-sst2-final")
tokenizer.save_pretrained("./gpt2-sst2-final")
print("训练完成！模型已保存到 ./gpt2-sst2-final")


# ====================== 可选：推理测试 ======================
def predict_sentiment(sentence):
    inputs = tokenizer(
        f"Sentence: {sentence}\nSentiment:",
        return_tensors="pt",
        truncation=True
    ).to("cuda" if torch.cuda.is_available() else "cpu")

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=3,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)


# 测试一句
test_sentence = "This movie is amazing!"
print("\n测试结果：", predict_sentiment(test_sentence))


