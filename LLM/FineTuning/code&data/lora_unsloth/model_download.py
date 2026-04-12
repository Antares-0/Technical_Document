#模型下载
from modelscope import snapshot_download
model_dir = snapshot_download('unsloth/Qwen3-0.6B-unsloth-bnb-4bit', cache_dir='./pretrained')
