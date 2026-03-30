from torch import nn
from transformers import AutoModel
import config


# 基于原始模型进行改造
class MyModel(nn.Module):
    def __init__(self):
        super(MyModel, self).__init__()
        self.bert = AutoModel.from_pretrained(config.PRE_TRAINED_DIR / 'bert-base-chinese')
        self.linear = nn.Linear(self.bert.config.hidden_size, 1)

    def forward(self, input_ids, attention_mask, token_type_ids):
        output = self.bert(input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
        last_hidden_state = output.last_hidden_state
        cls_hidden_state = last_hidden_state[:, 0, :]
        out_put = self.linear(cls_hidden_state).squeeze(-1)
        return out_put


