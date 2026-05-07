from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, DataCollatorForLanguageModeling
import torch
from datasets import load_dataset
import torch
from torch import nn
import numpy as np
from transformers import AutoModelForCausalLM

class rewardModel(nn.Module):
    def __init__(self):
        super(rewardModel, self).__init__()
        self.baseModel = AutoModelForCausalLM.from_pretrained('bert')

