import torch
from torch import nn
from transformers import AutoModelForCausalLM


# 定义奖励头
class RewardHead(nn.Module):
    def __init__(self, hidden_size):
        super().__init__()
        self.reward_head = nn.Linear(hidden_size, 1)
        # 初始化参数
        nn.init.kaiming_normal_(self.reward_head.weight)
        nn.init.zeros_(self.reward_head.bias)

    def forward(self, ipt):
        return self.reward_head(ipt)


# 定义奖励模型
class RewardModel(nn.Module):
    def __init__(self, model_path):
        super().__init__()
        self.layer1 = AutoModelForCausalLM.from_pretrained(model_path)
        self.layer2 = RewardHead(self.layer1.config.hidden_size)

    def forward(self, input_ids, attention_mask):
        # gpt2的前向传播，但是还要输出隐藏层
        layer1_outputs = self.layer1.forward(
            input_ids=input_ids,
            attention_mask=attention_mask,
            output_hidden_states=True
        )
        last_hidden_state = layer1_outputs.hidden_states[-1]
        # 给出奖励
        reward = self.layer2(last_hidden_state).squeeze(-1)
        # sigmoid
        return torch.sigmoid(reward)
