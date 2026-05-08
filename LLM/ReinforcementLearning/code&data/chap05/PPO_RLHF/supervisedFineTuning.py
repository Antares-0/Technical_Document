import torch
from datasets import load_dataset
from torch.optim import AdamW
from torch.utils.data import DataLoader
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import DataCollatorForLanguageModeling

model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

dataset_path = "glue"
ds = load_dataset(dataset_path, "sst2")
ds_train, ds_test = ds['train'], ds['validation']

# ====================== 新增：Tokenizer 配置（必须） ======================
tokenizer.pad_token = tokenizer.eos_token  # gpt2 没有pad，用eos代替
model.config.pad_token_id = model.config.eos_token_id

num_epochs = 1


# ====================== 新增：数据预处理函数 ======================
def preprocess_function(examples):
    return tokenizer(examples['sentence'])


map_kwargs = {
    'batched': True,
    'batch_size': 512,
    'remove_columns': ['idx', 'sentence', 'label']
}

# 对训练集 / 测试集批量预处理
tokenized_dataset_train = ds_train.map(preprocess_function, **map_kwargs)
tokenized_dataset_val = ds_test.map(preprocess_function, **map_kwargs)

# 去掉少于6个token的文本
tokenized_dataset_train = tokenized_dataset_train.filter(
    lambda x: len(x['input_ids']) > 5)
tokenized_dataset_val = tokenized_dataset_val.filter(
    lambda x: len(x['input_ids']) > 5)

data_collator = DataCollatorForLanguageModeling(
    tokenizer,
    mlm=False
)
dataloader_params = {
    'batch_size': 16,  # 6G显存正好够用
    'collate_fn': data_collator
}
train_dataloader = DataLoader(
    tokenized_dataset_train,
    **dataloader_params
)
val_dataloader = DataLoader(
    tokenized_dataset_val,
    **dataloader_params
)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def validate(epoch):
    """验证函数"""
    model.eval()  # 禁用模型的随机性，例如dropout等特性
    total_loss = 0.0
    for i, batch in enumerate(val_dataloader):
        batch = batch.to(device)
        with torch.no_grad():
            outputs = model(**batch)
            loss = outputs.loss  # 损失
            total_loss += loss.item()
    print(f'val_loss at {epoch} epoch:', total_loss / len(val_dataloader))


optimizer = AdamW(model.parameters(), lr=2e-5)
model.to(device)
validate(0)
for epoch in range(num_epochs):
    model.train()
    for i, batch in enumerate(train_dataloader):
        batch = batch.to(device)
        outputs = model(**batch)
        batch = batch.to(device)
        outputs = model(**batch)
        loss = outputs.loss
        print(f'Loss: {loss.item()}')
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    validate(epoch + 1)

# ====================== 训练完成：保存模型 ======================
model.save_pretrained("./gpt2-sst2-final")
tokenizer.save_pretrained("./gpt2-sst2-final")

# ====================== 可选：推理测试 ======================
from transformers import pipeline, set_seed
from pprint import pprint

g = pipeline('text-generation', model='./gpt2-sst2-final')
set_seed(42)
pprint(g("this is a", max_length=30, num_return_sequences=1))
