import torch
from torch import nn
from transformers import AutoModelForCausalLM

# 奖励头
class ValueHead(nn.Module):
    def __init__(self, hidden_size):
        super().__init__()
        self.valueHead = nn.Linear(hidden_size, 1)
        # 初始化参数
        nn.init.kaiming_normal_(self.valueHead.weight)
        nn.init.zeros_(self.valueHead.bias)

    def forward(self, ipt):
        return self.valueHead(ipt)

# 评论家模型
class ActorCriticModel(nn.Module):
    def __init__(self, model_path):
        super().__init__()
        self.layer1 = AutoModelForCausalLM.from_pretrained(model_path)
        self.layer2 = ValueHead(self.layer1.config.hidden_size)

    def forward(self, input_ids, attention_mask) -> tuple[torch.FloatTensor, torch.FloatTensor]:
        # gpt2-sft模型的输出
        layer1_outputs = self.layer1.forward(
            input_ids=input_ids,
            attention_mask=attention_mask,
            output_hidden_states=True
        )
        lm_logits = layer1_outputs.logits
        last_hidden_state = layer1_outputs.hidden_states[-1]
        # 评估token的价值，评估的是最后一个隐藏层的价值
        value = self.layer2(last_hidden_state).squeeze(-1)
        # 返回输出的token的logits和token的价值
        return lm_logits, value

    def generate(self, *args, **kwargs):
        return self.layer1.generate(*args, **kwargs)



