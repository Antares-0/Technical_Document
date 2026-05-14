import numpy as np
import torch
from datasets import load_dataset
from torch import nn
from torch.utils.data import DataLoader
from transformers import AutoTokenizer
from transformers import DataCollatorWithPadding

from rm import RewardModel

print("=" * 60)
print("✅ 开始执行奖励模型训练脚本")
print("=" * 60)

# 分词器
baseModelName = 'gpt2'
print(f"🔤 加载分词器：{baseModelName}")
gpt2Tokenizer = AutoTokenizer.from_pretrained(baseModelName)

# 固定配置
gpt2Tokenizer.pad_token = gpt2Tokenizer.eos_token
REWARD_TOKEN_ID = gpt2Tokenizer.eos_token_id
print(f"✅ 配置奖励 token ID：{REWARD_TOKEN_ID}")

# 数据处理函数
def processData(data):
    outputs = gpt2Tokenizer(data['sentence'])
    batch_size = len(data['sentence'])
    outputs['score'] = np.zeros(batch_size, dtype=np.float32)
    outputs['score_index'] = np.zeros(batch_size, dtype=np.int32)

    for idx in range(len(outputs['input_ids'])):
        outputs['input_ids'][idx].append(REWARD_TOKEN_ID)
        outputs['attention_mask'][idx].append(1)
        outputs['score'][idx] = float(data['label'][idx])
        outputs['score_index'][idx] = len(outputs['input_ids'][idx]) - 1
    return outputs

# 数据处理参数
map_kwargs = {
    "batched": True,
    "batch_size": 512,
    "remove_columns": ['idx', 'sentence', 'label']
}

# 加载数据集
print("📥 正在加载 SST-2 数据集...")
ds = load_dataset("glue", "sst2")
ds_train = ds['train']
ds_test = ds['validation']
print(f"✅ 数据集加载完成：训练集 {len(ds_train)} 条，测试集 {len(ds_test)} 条")

# 数据处理
print("🔧 开始处理训练数据...")
tokenized_dataset_train = ds_train.map(processData, **map_kwargs)
print("✅ 训练数据处理完成！")

print("🔧 开始处理测试数据...")
tokenized_dataset_test = ds_test.map(processData, **map_kwargs)
print("✅ 测试数据处理完成！")

tokenized_dataset_train.set_format(type='torch')
tokenized_dataset_test.set_format(type='torch')

data_collator = DataCollatorWithPadding(gpt2Tokenizer)
dataloader_params = {
    'batch_size': 64,
    'shuffle': True,
    'collate_fn': data_collator
}

print("📦 构建 DataLoader...")
train_dataloader = DataLoader(tokenized_dataset_train, **dataloader_params)
test_dataloader = DataLoader(tokenized_dataset_test, **dataloader_params)
print("✅ DataLoader 构建完成")

# 创建奖励模型
print("🤖 初始化奖励模型...")
reward_model = RewardModel(baseModelName)
print("✅ 奖励模型初始化完成")

# 训练必备参数
optimizer = torch.optim.AdamW(reward_model.parameters(), lr=1e-4)
criterion = nn.BCEWithLogitsLoss()
num_epochs = 1

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
reward_model.to(device)
print(f"🚀 模型已加载到设备：{device}")


# 评估函数
def validate():
    print("\n📌 开始验证集评估...")
    reward_model.eval()
    total_loss = 0
    for idx, input_data in enumerate(test_dataloader):
        input_data = input_data.to(device)
        reward_model_inputs = {
            'input_ids': input_data['input_ids'],
            'attention_mask': input_data['attention_mask']
        }
        with torch.no_grad():
            reward_model_output = reward_model(**reward_model_inputs)
            index = torch.arange(reward_model_output.shape[0], device=device)
            validate_output_score = reward_model_output[index, input_data['score_index']]
            validate_target_score = input_data['score']
            score_loss = criterion(validate_output_score, validate_target_score)
        total_loss += score_loss.item()

    avg_loss = total_loss / len(test_dataloader)
    print(f"✅ 验证完成 | 平均验证损失：{avg_loss:.4f}")
    return avg_loss


# 训练循环
print("\n" + "=" * 60)
print("🔥 开始训练奖励模型")
print("=" * 60)

for epoch in range(num_epochs):
    print(f"\n📆 Epoch {epoch + 1}/{num_epochs} 开始")
    reward_model.train()
    total_step = len(train_dataloader)

    for idx, input_data in enumerate(train_dataloader):
        inputs = input_data.to(device)
        model_inputs = {
            'input_ids': inputs['input_ids'],
            'attention_mask': inputs['attention_mask']
        }

        reward_scores = reward_model(**model_inputs)
        # ✅ 修复：把 index 放到 cuda 上
        reward_index = torch.arange(reward_scores.shape[0], device=device)
        output_score = reward_scores[reward_index, inputs['score_index']]
        target_score = inputs['score']

        loss_item = criterion(output_score, target_score)
        optimizer.zero_grad()
        loss_item.backward()
        optimizer.step()

        if idx % 10 == 0:
            print(f"🔸 Step [{idx + 1}/{total_step}] | 损失：{loss_item.item():.4f}")

    print(f"📆 Epoch {epoch + 1} 训练完成")
    validate()

print("\n" + "=" * 60)
print("🎉 训练全部完成！正在保存模型...")
torch.save(reward_model.state_dict(), 'reward_model.pt')
print("✅ 模型已保存为：reward_model.pt")
print("=" * 60)
