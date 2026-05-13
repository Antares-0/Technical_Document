from copy import deepcopy

import numpy as np
import torch
from datasets import load_dataset
from torch.utils.data import DataLoader
from transformers import AutoTokenizer
from transformers import DataCollatorWithPadding

from actor_critic_model import ActorCriticModel
from rm import RewardModel

# 系统配置
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[INFO] 使用设备: {device}")

# 模型配置、分词器配置
baseModelName = 'gpt2'
sftModelName = './gpt2-sft-final'

# 加载分词器
gpt2Tokenizer = AutoTokenizer.from_pretrained(baseModelName)
gpt2Tokenizer.pad_token = gpt2Tokenizer.eos_token
REWARD_TOKEN_ID = gpt2Tokenizer.eos_token_id
print("[INFO] 分词器加载完成")

# 加载数据集
ds = load_dataset("glue", "sst2")
ds_train = ds['train']
ds_test = ds['validation']
print(f"[INFO] 数据集加载完成 | 训练集 {len(ds_train)} 条")

# 系统配置
input_data_length = 3  # 提示词长度
max_new_token_num = 20  # 最多生成多少个token

# 四个模型
# actor_critic_model：同时包含actor和critic两个模型，sft是actor，线性层用于打分就是critic
# reward_model：奖励模型，环境给出的真实奖励
# sft_frozen_model：冻结模型，用于计算KL散度，保证参数不过分偏离
print("[INFO] 加载模型...")
actor_critic_model = ActorCriticModel(sftModelName).to(device)
reward_model = RewardModel(baseModelName).to(device)
sft_frozen_model = deepcopy(actor_critic_model).to(device)
print("[INFO] 模型加载完成")


# 对每一条记录进行处理
def sample_process(record):
    record['input_ids'] = gpt2Tokenizer.encode(record["sentence"])[:input_data_length]
    record['attention_mask'] = [1] * len(record['input_ids'])
    record['query'] = record["sentence"][:input_data_length]
    return record


# 数据处理参数
map_kwargs = {
    "batched": False,
    "remove_columns": ['idx', 'sentence', 'label']
}

# 处理数据
print("[INFO] 开始处理训练数据...")
tokenized_dataset_train = ds_train.map(sample_process, **map_kwargs)
tokenized_dataset_train.set_format(type='torch')
print("[INFO] 开始处理评估数据...")
tokenized_dataset_test = ds_test.map(sample_process, **map_kwargs)
tokenized_dataset_test.set_format(type='torch')


def collator(data_input):
    return dict(
        (key, [d[key] for d in data_input])
        for key in data_input[0]
    )


train_dataloader = DataLoader(
    tokenized_dataset_train,
    batch_size=64,
    collate_fn=collator,
    shuffle=True
)
test_dataloader = DataLoader(
    tokenized_dataset_test,
    batch_size=64,
    collate_fn=collator,
    shuffle=True
)

print("[INFO] DataLoader加载完成")

print("[INFO] 准备生成采样数据")
# 从训练集合中拿出一小批数据，进行简单采样
# 训练集合的数据格式
# 'input_ids'
# 'attention_mask'
# 'query'
data_info = next(iter(train_dataloader))
small_batch_input_ids = data_info['input_ids']
small_batch_attention_mask = data_info['attention_mask']

# 存储采样数据
# 模型回复记录（仅回复）
response_tensors = []
# 提示词 + 回复张量
full_response_tensors = []
# 环境给予的奖励记录
reward_score_tensors = []
# 提示词
query_tensors = []

# 生成参数
generation_kwargs = {
    "min_length": -1,
    "top_k": 50,
    "top_p": 0.9,
    "do_sample": True,
    "pad_token_id": gpt2Tokenizer.eos_token_id,
    "max_new_tokens": max_new_token_num,
    "temperature": 0.7
}

# 采样
# 遍历这一小批次数据，获取一批采样数据
for index, sample in enumerate(small_batch_input_ids):
    sample = sample.to(device)
    sample_mask = small_batch_attention_mask[index].to(device)
    query_tensors.append(sample)

    # actor模型生成回复
    response = actor_critic_model.generate(
        input_ids=sample.unsqueeze(0),
        attention_mask=sample_mask.unsqueeze(0),
        **generation_kwargs,
    )

    input_len = sample.shape[0]
    response_only = response[:, input_len:]
    response_tensors.append(response_only.squeeze(0))

    reward_token = torch.tensor([[REWARD_TOKEN_ID]], device=device)
    response_with_reward_token = torch.cat([response, reward_token], dim=-1)

    with torch.no_grad():
        attention_mask = torch.ones_like(response_with_reward_token, dtype=torch.long)
        # 调用奖励模型，判断当前模型回复，给reward
        reward_score = reward_model(
            response_with_reward_token,
            attention_mask
        ).squeeze(0)[-1]
        reward_score = 2 * (reward_score - 0.5)

    reward_score_tensors.append(reward_score)
    full_response_tensors.append(response.squeeze(0))

# 将一批数据补齐到固定的长度
data_collator = DataCollatorWithPadding(tokenizer=gpt2Tokenizer)
trace_data = data_collator([
    {'input_ids': ids,
     'attention_mask': torch.ones_like(ids)}
    for ids in full_response_tensors
]).to(device)


# 给定输入数据，计算对应的reward
def compute_rewards(
        input_message,
        query_message,
        response_message,
        score_message
):
    with torch.no_grad():
        # 调用模型生成logits和对应的价值
        lm_logits, value_callback = actor_critic_model(**input_message)
        sft_lm_logits, _ = sft_frozen_model(**input_message)

        # 从lm_logits获取原始打分，转变为概率分布
        logp = torch.nn.functional.log_softmax(
            lm_logits[:, :-1, :],
            dim=-1
        )
        ref_logp = torch.nn.functional.log_softmax(
            sft_lm_logits[:, :-1, :],
            dim=-1
        )

        labels = input_message['input_ids'][:, 1:]
        logp = torch.gather(
            logp,
            2,
            labels.unsqueeze(-1)
        ).squeeze(-1)
        ref_logp = torch.gather(
            ref_logp,
            2,
            labels.unsqueeze(-1)
        ).squeeze(-1)

        kl = logp - ref_logp
        beta = 0.2
        message_rewards = - beta * kl
        message_attention_mask = input_message['attention_mask']
        message_masks = torch.zeros_like(message_attention_mask[:, 1:])
        message_masks[:, :] = message_attention_mask[:, 1:]

        for j in range(len(query_message)):
            start = len(query_message[j]) - 1
            end = start + len(response_message[j])
            message_masks[j, :start] = 0
            message_masks[j, end:] = 0

            message_rewards[j, end - 1] += score_message[j]
            message_rewards[j, :] *= message_masks[j, :]
            value_callback[j, :-1] *= message_masks[j, :]

    return logp, message_rewards, value_callback[:, :-1], message_masks


# 根据mask计算平均值
def masked_mean(unmasked_values, mask):
    return (unmasked_values * mask).sum() / mask.sum()


# 根据mask计算方差
def masked_var(unmasked_values, mask):
    mean = masked_mean(unmasked_values, mask)
    centred_values = unmasked_values - mean
    return masked_mean(centred_values ** 2, mask)


# 对数据做归一化处理
def masked_whiten(unmasked_values, mask):
    mean, var = masked_mean(unmasked_values, mask), masked_var(unmasked_values, mask)
    whitened = (unmasked_values - mean) * torch.rsqrt(var + 1e-8)
    whitened += mean
    return whitened


def compute_advantage(rewards, values, masks):
    last_gae = 0.0
    advantage_reversed = []
    seq_length = rewards.shape[-1]
    gamma, lam = 1.0, 0.95

    for t in reversed(range(seq_length)):
        nextvalues = values[:, t + 1] if t < seq_length - 1 else 0.0
        delta = rewards[:, t] + gamma * nextvalues - values[:, t]
        last_gae = delta + gamma * lam * last_gae
        advantage_reversed.append(last_gae)
    advantages = torch.stack(advantage_reversed[::-1], dim=1)
    advantages = masked_whiten(advantages, masks)

    returns = advantages + values
    return advantages, returns


## 开始ppo训练
learning_rate = 1e-5
optimizer = torch.optim.AdamW(actor_critic_model.parameters(), lr=learning_rate)
mini_batch_size = 4
ppo_epochs = 4
cliprange_ratio = 0.2
v_loss_coeff = 0.1
ratio_threshold = 10
batch_size = 64


def compute_loss(
        old_logprobs,
        values,
        logprobs,
        vpreds,
        masks,
        advantages,
        returns
):
    ratio = torch.exp(logprobs - old_logprobs)
    pg_loss1 = - ratio * advantages
    pg_loss2 = - torch.clamp(
        ratio,
        1 - cliprange_ratio,
        1 + cliprange_ratio
    ) * advantages
    pg_loss = masked_mean(torch.max(pg_loss1, pg_loss2), masks)
    v_loss = masked_mean((vpreds - returns) ** 2, masks)
    loss = pg_loss + v_loss_coeff * v_loss
    avg_ratio = masked_mean(ratio, masks)

    if avg_ratio > ratio_threshold:
        pg_loss = pg_loss * 0.0
        v_loss = v_loss * 0.0
        loss = loss * 0.0

    return loss, v_loss


def mini_batch_train():
    print(f"[TRAIN] 开始 PPO 训练，共 {ppo_epochs} 个轮次")
    for ep in range(ppo_epochs):
        batch_inds = np.random.permutation(batch_size)
        for start in range(0, batch_size, mini_batch_size):
            end = start + mini_batch_size
            mini_batch_inds = batch_inds[start:end]

            mb_model_inputs = {
                'input_ids': input_data['input_ids'][mini_batch_inds],
                'attention_mask': input_data['attention_mask'][mini_batch_inds]
            }
            mb_logits, mb_vpreds = actor_critic_model(**mb_model_inputs)
            mb_logits = torch.nn.functional.log_softmax(
                mb_logits[:, :-1, :],
                dim=-1
            )
            mb_logprobs = torch.gather(
                mb_logits,
                2,
                mb_model_inputs['input_ids'][:, 1:].unsqueeze(-1)
            ).squeeze(-1)

            loss, loss_v = compute_loss(
                logprobs[mini_batch_inds],
                values[mini_batch_inds],
                mb_logprobs,
                mb_vpreds[:, :-1],
                masks[mini_batch_inds],
                advantages[mini_batch_inds],
                returns[mini_batch_inds]
            )

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        print(f"[TRAIN] PPO 轮次 {ep + 1}/{ppo_epochs} 完成")
    print("[TRAIN] mini-batch 训练完成")


num_epochs = 1
total_batches = len(train_dataloader)
print(f"\n[START] 开始训练，总 Epoch：{num_epochs}，总批次：{total_batches}")

for epoch in range(num_epochs):
    print(f"\n===== Epoch {epoch + 1}/{num_epochs} =====")
    for batch_idx, batch in enumerate(train_dataloader):
        print(f"[PROCESS] 处理批次 {batch_idx + 1}/{total_batches}")

        query_tensors = batch['input_ids']
        query_attention_masks = batch['attention_mask']

        response_tensors = []
        query_response_tensors = []
        score_tensors = []

        for i, query in enumerate(query_tensors):
            query = query.to(device)
            query_attention_mask = query_attention_masks[i].to(device)
            new_tokens = 20
            generation_kwargs["max_new_tokens"] = new_tokens

            query_response = actor_critic_model.generate(
                input_ids=query.unsqueeze(0),
                attention_mask=query_attention_mask.unsqueeze(0),
                **generation_kwargs
            ).squeeze(0)
            response_len = len(query_response) - len(query)
            response_tensors.append(query_response[-response_len:])
            query_response_tensors.append(query_response)

            with torch.no_grad():
                query_response_score = torch.cat([
                    query_response,
                    torch.tensor([REWARD_TOKEN_ID]).to(device)])
                attention_mask = torch.ones_like(query_response_score, dtype=torch.long)
                score = reward_model(
                    query_response_score.unsqueeze(0),
                    attention_mask.unsqueeze(0)
                ).squeeze(0)[-1]
                score = 2 * (score - 0.5)
            score_tensors.append(score)

        input_data = data_collator([
            {
                'input_ids': ids,
                'attention_mask': torch.ones_like(ids)
            }
            for ids in query_response_tensors
        ]).to(device)

        # 计算奖励
        logprobs, rewards, values, masks = compute_rewards(
            input_data,
            query_tensors,
            response_tensors,
            score_tensors
        )
        advantages, returns = compute_advantage(rewards, values, masks)

        # 训练
        mini_batch_train()

    print(f"\n[INFO] Epoch {epoch + 1} 完成")

# 保存模型
print("\n[SAVE] 训练完成，正在保存模型...")
torch.save(actor_critic_model.state_dict(), 'gpt2-ppo.pt')
print("[SUCCESS] 模型已保存：gpt2-ppo.pt")
