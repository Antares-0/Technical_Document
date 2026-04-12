import os
os.environ['UNSLOTH_USE_MODELSCOPE'] = '1'
from unsloth import FastLanguageModel
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset
import torch

local_model_path='pretrained/unsloth/Qwen3-0.6B-unsloth-bnb-4bit'
dataset_path='data/keywords_data_train.jsonl'

myModel, tokenizer = FastLanguageModel.from_pretrained(
    model_name=local_model_path,
    max_seq_length=2048,
    device_map='auto',
    dtype=None,
    load_in_4bit=True,
    load_in_8bit=False,
    full_finetuning=False,
)
print(myModel)



def convert_to_qwen_format(item):
    conversations = []
    for conv_list in item["conversation"]:
        for conv in conv_list:
            conversations.append([
                {"role":"user", "content":conv["human"].strip()},
                {"role":"assistant", "content":conv["assistant"].strip()},
            ])
    return {"conversations":conversations}

dataset = load_dataset("json", data_files=dataset_path)
dataset = dataset['train']
# dataset = dataset['train'].shuffle(seed=42).select(range(100))
dataset = dataset.map(
    convert_to_qwen_format,
    batched=True,
    remove_columns=dataset.column_names,
)
print(dataset)


def format_func(item):
    formatted_texts = []
    for conv in item['conversations']:
        formatted_texts.append(
            tokenizer.apply_chat_template(
                conv,
                tokenize=False,
                add_generation_prompt=False
            )
        )
    return {"text":formatted_texts}


formatted_dataset = dataset.map(
    format_func,
    batched=True,
    remove_columns=dataset.column_names,
)
print(formatted_dataset[0])


newModel = FastLanguageModel.get_peft_model(
    model=myModel,
    r=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha=32,
    lora_dropout=0,
    bias='none',
    use_gradient_checkpointing='unsloth',
    random_state=3407,
    use_rslora=False,
    loftq_config=None,
)

print(newModel)

trainer = SFTTrainer(
    model = newModel,
    # processing_class = tokenizer,
    tokenizer = tokenizer,
    train_dataset = formatted_dataset,
    eval_dataset = None, # Can set up evaluation!
    args = SFTConfig(
        dataset_text_field = "text",
        per_device_train_batch_size = 256,
        gradient_accumulation_steps = 1,
        warmup_steps = 5,
        num_train_epochs = 1, # Set this for 1 full training run.
        # max_steps = 30,
        learning_rate = 2e-4, # Reduce to 2e-5 for long training runs
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        report_to = "none", # Use this for WandB etc
    ),
)

# 统计指标相关的
gpu_stats = torch.cuda.get_device_properties(0)
start_gpu_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
max_memory = round(gpu_stats.total_memory / 1024 / 1024 / 1024, 3)
print(f"GPU = {gpu_stats.name}. Max memory = {max_memory} GB.")
print(f"{start_gpu_memory} GB of memory reserved.")

# 开始训练
trainer_stats = trainer.train()

used_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
used_memory_for_lora = round(used_memory - start_gpu_memory, 3)
used_percentage = round(used_memory / max_memory * 100, 3)
lora_percentage = round(used_memory_for_lora / max_memory * 100, 3)
print(f"{trainer_stats.metrics['train_runtime']} seconds used for training.")
print(
    f"{round(trainer_stats.metrics['train_runtime'] / 60, 2)} minutes used for training."
)
print(f"Peak reserved memory = {used_memory} GB.")
print(f"Peak reserved memory for training = {used_memory_for_lora} GB.")
print(f"Peak reserved memory % of max memory = {used_percentage} %.")
print(f"Peak reserved memory for training % of max memory = {lora_percentage} %.")

trainer.model.save_pretrained('./trained_models/unsloth')
tokenizer.save_pretrained('./trained_models/unsloth')



# {'loss': '3.878', 'grad_norm': '2.362', 'learning_rate': '0', 'epoch': '0.005155'}
# {'loss': '3.982', 'grad_norm': '2.435', 'learning_rate': '4e-05', 'epoch': '0.01031'}
# {'loss': '3.799', 'grad_norm': '2.274', 'learning_rate': '8e-05', 'epoch': '0.01546'}
# {'loss': '3.698', 'grad_norm': '1.889', 'learning_rate': '0.00012', 'epoch': '0.02062'}
# {'loss': '3.476', 'grad_norm': '1.33', 'learning_rate': '0.00016', 'epoch': '0.02577'}
# {'loss': '3.167', 'grad_norm': '1.08', 'learning_rate': '0.0002', 'epoch': '0.03093'}
# {'loss': '3.089', 'grad_norm': '0.7762', 'learning_rate': '0.0001989', 'epoch': '0.03608'}
# {'loss': '3.081', 'grad_norm': '0.7927', 'learning_rate': '0.0001979', 'epoch': '0.04124'}
# {'loss': '3.011', 'grad_norm': '0.5858', 'learning_rate': '0.0001968', 'epoch': '0.04639'}
# {'loss': '2.923', 'grad_norm': '0.6105', 'learning_rate': '0.0001958', 'epoch': '0.05155'}
# {'loss': '2.992', 'grad_norm': '0.5602', 'learning_rate': '0.0001947', 'epoch': '0.0567'}
# {'loss': '2.918', 'grad_norm': '0.4448', 'learning_rate': '0.0001937', 'epoch': '0.06186'}
# {'loss': '2.89', 'grad_norm': '0.4394', 'learning_rate': '0.0001926', 'epoch': '0.06701'}
# {'loss': '2.857', 'grad_norm': '0.4385', 'learning_rate': '0.0001915', 'epoch': '0.07216'}
# {'loss': '2.744', 'grad_norm': '0.3603', 'learning_rate': '0.0001905', 'epoch': '0.07732'}
# {'loss': '2.8', 'grad_norm': '0.3708', 'learning_rate': '0.0001894', 'epoch': '0.08247'}
# {'loss': '2.746', 'grad_norm': '0.3383', 'learning_rate': '0.0001884', 'epoch': '0.08763'}
# {'loss': '2.712', 'grad_norm': '0.336', 'learning_rate': '0.0001873', 'epoch': '0.09278'}
# {'loss': '2.733', 'grad_norm': '0.3419', 'learning_rate': '0.0001862', 'epoch': '0.09794'}
# {'loss': '2.725', 'grad_norm': '0.3634', 'learning_rate': '0.0001852', 'epoch': '0.1031'}
# {'loss': '2.659', 'grad_norm': '0.3695', 'learning_rate': '0.0001841', 'epoch': '0.1082'}
# {'loss': '2.661', 'grad_norm': '0.3615', 'learning_rate': '0.0001831', 'epoch': '0.1134'}
# {'loss': '2.667', 'grad_norm': '0.3689', 'learning_rate': '0.000182', 'epoch': '0.1186'}
# {'loss': '2.682', 'grad_norm': '0.3838', 'learning_rate': '0.000181', 'epoch': '0.1237'}
# {'loss': '2.658', 'grad_norm': '0.3775', 'learning_rate': '0.0001799', 'epoch': '0.1289'}
# {'loss': '2.607', 'grad_norm': '0.3317', 'learning_rate': '0.0001788', 'epoch': '0.134'}
# {'loss': '2.597', 'grad_norm': '0.2589', 'learning_rate': '0.0001778', 'epoch': '0.1392'}
# {'loss': '2.627', 'grad_norm': '0.2164', 'learning_rate': '0.0001767', 'epoch': '0.1443'}
# {'loss': '2.666', 'grad_norm': '0.2249', 'learning_rate': '0.0001757', 'epoch': '0.1495'}
# {'loss': '2.537', 'grad_norm': '0.2167', 'learning_rate': '0.0001746', 'epoch': '0.1546'}
# {'loss': '2.602', 'grad_norm': '0.2219', 'learning_rate': '0.0001735', 'epoch': '0.1598'}
# {'loss': '2.625', 'grad_norm': '0.1923', 'learning_rate': '0.0001725', 'epoch': '0.1649'}
# {'loss': '2.533', 'grad_norm': '0.2222', 'learning_rate': '0.0001714', 'epoch': '0.1701'}
# {'loss': '2.643', 'grad_norm': '0.2183', 'learning_rate': '0.0001704', 'epoch': '0.1753'}
# {'loss': '2.595', 'grad_norm': '0.2087', 'learning_rate': '0.0001693', 'epoch': '0.1804'}
# {'loss': '2.658', 'grad_norm': '0.2639', 'learning_rate': '0.0001683', 'epoch': '0.1856'}
# {'loss': '2.64', 'grad_norm': '0.2036', 'learning_rate': '0.0001672', 'epoch': '0.1907'}
# {'loss': '2.619', 'grad_norm': '0.206', 'learning_rate': '0.0001661', 'epoch': '0.1959'}
# {'loss': '2.575', 'grad_norm': '0.1879', 'learning_rate': '0.0001651', 'epoch': '0.201'}
# {'loss': '2.576', 'grad_norm': '0.1799', 'learning_rate': '0.000164', 'epoch': '0.2062'}
# {'loss': '2.579', 'grad_norm': '0.1795', 'learning_rate': '0.000163', 'epoch': '0.2113'}
# {'loss': '2.564', 'grad_norm': '0.1968', 'learning_rate': '0.0001619', 'epoch': '0.2165'}
# {'loss': '2.565', 'grad_norm': '0.1894', 'learning_rate': '0.0001608', 'epoch': '0.2216'}
# {'loss': '2.514', 'grad_norm': '0.1732', 'learning_rate': '0.0001598', 'epoch': '0.2268'}
# {'loss': '2.539', 'grad_norm': '0.1727', 'learning_rate': '0.0001587', 'epoch': '0.232'}
# {'loss': '2.48', 'grad_norm': '0.1707', 'learning_rate': '0.0001577', 'epoch': '0.2371'}
# {'loss': '2.587', 'grad_norm': '0.1683', 'learning_rate': '0.0001566', 'epoch': '0.2423'}
# {'loss': '2.583', 'grad_norm': '0.177', 'learning_rate': '0.0001556', 'epoch': '0.2474'}
# {'loss': '2.569', 'grad_norm': '0.1618', 'learning_rate': '0.0001545', 'epoch': '0.2526'}
# {'loss': '2.519', 'grad_norm': '0.1689', 'learning_rate': '0.0001534', 'epoch': '0.2577'}
# {'loss': '2.495', 'grad_norm': '0.1627', 'learning_rate': '0.0001524', 'epoch': '0.2629'}
# {'loss': '2.515', 'grad_norm': '0.1705', 'learning_rate': '0.0001513', 'epoch': '0.268'}
# {'loss': '2.602', 'grad_norm': '0.1681', 'learning_rate': '0.0001503', 'epoch': '0.2732'}
# {'loss': '2.621', 'grad_norm': '0.1649', 'learning_rate': '0.0001492', 'epoch': '0.2784'}
# {'loss': '2.576', 'grad_norm': '0.1645', 'learning_rate': '0.0001481', 'epoch': '0.2835'}
# {'loss': '2.571', 'grad_norm': '0.1674', 'learning_rate': '0.0001471', 'epoch': '0.2887'}
# {'loss': '2.595', 'grad_norm': '0.1663', 'learning_rate': '0.000146', 'epoch': '0.2938'}
# {'loss': '2.527', 'grad_norm': '0.1782', 'learning_rate': '0.000145', 'epoch': '0.299'}
# {'loss': '2.572', 'grad_norm': '0.1698', 'learning_rate': '0.0001439', 'epoch': '0.3041'}
# {'loss': '2.627', 'grad_norm': '0.1658', 'learning_rate': '0.0001429', 'epoch': '0.3093'}
# {'loss': '2.514', 'grad_norm': '0.1762', 'learning_rate': '0.0001418', 'epoch': '0.3144'}
# {'loss': '2.584', 'grad_norm': '0.1772', 'learning_rate': '0.0001407', 'epoch': '0.3196'}
# {'loss': '2.53', 'grad_norm': '0.1666', 'learning_rate': '0.0001397', 'epoch': '0.3247'}
# {'loss': '2.547', 'grad_norm': '0.1755', 'learning_rate': '0.0001386', 'epoch': '0.3299'}
# {'loss': '2.549', 'grad_norm': '0.1736', 'learning_rate': '0.0001376', 'epoch': '0.3351'}
# {'loss': '2.587', 'grad_norm': '0.1621', 'learning_rate': '0.0001365', 'epoch': '0.3402'}
# {'loss': '2.556', 'grad_norm': '0.1702', 'learning_rate': '0.0001354', 'epoch': '0.3454'}
# {'loss': '2.563', 'grad_norm': '0.163', 'learning_rate': '0.0001344', 'epoch': '0.3505'}
# {'loss': '2.493', 'grad_norm': '0.1655', 'learning_rate': '0.0001333', 'epoch': '0.3557'}
# {'loss': '2.51', 'grad_norm': '0.1594', 'learning_rate': '0.0001323', 'epoch': '0.3608'}
# {'loss': '2.517', 'grad_norm': '0.163', 'learning_rate': '0.0001312', 'epoch': '0.366'}
# {'loss': '2.529', 'grad_norm': '0.1656', 'learning_rate': '0.0001302', 'epoch': '0.3711'}
# {'loss': '2.567', 'grad_norm': '0.1615', 'learning_rate': '0.0001291', 'epoch': '0.3763'}
# {'loss': '2.478', 'grad_norm': '0.1558', 'learning_rate': '0.000128', 'epoch': '0.3814'}
# {'loss': '2.531', 'grad_norm': '0.1661', 'learning_rate': '0.000127', 'epoch': '0.3866'}
# {'loss': '2.521', 'grad_norm': '0.1778', 'learning_rate': '0.0001259', 'epoch': '0.3918'}
# {'loss': '2.561', 'grad_norm': '0.1633', 'learning_rate': '0.0001249', 'epoch': '0.3969'}
# {'loss': '2.541', 'grad_norm': '0.1636', 'learning_rate': '0.0001238', 'epoch': '0.4021'}
# {'loss': '2.548', 'grad_norm': '0.1718', 'learning_rate': '0.0001228', 'epoch': '0.4072'}
# {'loss': '2.518', 'grad_norm': '0.1664', 'learning_rate': '0.0001217', 'epoch': '0.4124'}
# {'loss': '2.57', 'grad_norm': '0.1688', 'learning_rate': '0.0001206', 'epoch': '0.4175'}
# {'loss': '2.528', 'grad_norm': '0.1667', 'learning_rate': '0.0001196', 'epoch': '0.4227'}
# {'loss': '2.504', 'grad_norm': '0.1751', 'learning_rate': '0.0001185', 'epoch': '0.4278'}
# {'loss': '2.586', 'grad_norm': '0.1598', 'learning_rate': '0.0001175', 'epoch': '0.433'}
# {'loss': '2.512', 'grad_norm': '0.1631', 'learning_rate': '0.0001164', 'epoch': '0.4381'}
# {'loss': '2.51', 'grad_norm': '0.1742', 'learning_rate': '0.0001153', 'epoch': '0.4433'}
# {'loss': '2.529', 'grad_norm': '0.1626', 'learning_rate': '0.0001143', 'epoch': '0.4485'}
# {'loss': '2.518', 'grad_norm': '0.1733', 'learning_rate': '0.0001132', 'epoch': '0.4536'}
# {'loss': '2.53', 'grad_norm': '0.162', 'learning_rate': '0.0001122', 'epoch': '0.4588'}
# {'loss': '2.483', 'grad_norm': '0.1612', 'learning_rate': '0.0001111', 'epoch': '0.4639'}
# {'loss': '2.585', 'grad_norm': '0.1709', 'learning_rate': '0.0001101', 'epoch': '0.4691'}
# {'loss': '2.514', 'grad_norm': '0.1654', 'learning_rate': '0.000109', 'epoch': '0.4742'}
# {'loss': '2.552', 'grad_norm': '0.1676', 'learning_rate': '0.0001079', 'epoch': '0.4794'}
# {'loss': '2.53', 'grad_norm': '0.1606', 'learning_rate': '0.0001069', 'epoch': '0.4845'}
# {'loss': '2.524', 'grad_norm': '0.1601', 'learning_rate': '0.0001058', 'epoch': '0.4897'}
# {'loss': '2.47', 'grad_norm': '0.1794', 'learning_rate': '0.0001048', 'epoch': '0.4948'}
# {'loss': '2.52', 'grad_norm': '0.175', 'learning_rate': '0.0001037', 'epoch': '0.5'}
# {'loss': '2.481', 'grad_norm': '0.1657', 'learning_rate': '0.0001026', 'epoch': '0.5052'}
# {'loss': '2.537', 'grad_norm': '0.1676', 'learning_rate': '0.0001016', 'epoch': '0.5103'}
# {'loss': '2.543', 'grad_norm': '0.1695', 'learning_rate': '0.0001005', 'epoch': '0.5155'}
# {'loss': '2.57', 'grad_norm': '0.1714', 'learning_rate': '9.947e-05', 'epoch': '0.5206'}
# {'loss': '2.546', 'grad_norm': '0.1737', 'learning_rate': '9.841e-05', 'epoch': '0.5258'}
# {'loss': '2.468', 'grad_norm': '0.1637', 'learning_rate': '9.735e-05', 'epoch': '0.5309'}
# {'loss': '2.462', 'grad_norm': '0.172', 'learning_rate': '9.63e-05', 'epoch': '0.5361'}
# {'loss': '2.549', 'grad_norm': '0.1691', 'learning_rate': '9.524e-05', 'epoch': '0.5412'}
# {'loss': '2.564', 'grad_norm': '0.1625', 'learning_rate': '9.418e-05', 'epoch': '0.5464'}
# {'loss': '2.457', 'grad_norm': '0.1776', 'learning_rate': '9.312e-05', 'epoch': '0.5515'}
# {'loss': '2.489', 'grad_norm': '0.1803', 'learning_rate': '9.206e-05', 'epoch': '0.5567'}
# {'loss': '2.54', 'grad_norm': '0.1661', 'learning_rate': '9.101e-05', 'epoch': '0.5619'}
# {'loss': '2.493', 'grad_norm': '0.1739', 'learning_rate': '8.995e-05', 'epoch': '0.567'}
# {'loss': '2.504', 'grad_norm': '0.1767', 'learning_rate': '8.889e-05', 'epoch': '0.5722'}
# {'loss': '2.522', 'grad_norm': '0.1651', 'learning_rate': '8.783e-05', 'epoch': '0.5773'}
# {'loss': '2.451', 'grad_norm': '0.1722', 'learning_rate': '8.677e-05', 'epoch': '0.5825'}
# {'loss': '2.524', 'grad_norm': '0.1845', 'learning_rate': '8.571e-05', 'epoch': '0.5876'}
# {'loss': '2.557', 'grad_norm': '0.1721', 'learning_rate': '8.466e-05', 'epoch': '0.5928'}
# {'loss': '2.531', 'grad_norm': '0.1672', 'learning_rate': '8.36e-05', 'epoch': '0.5979'}
# {'loss': '2.513', 'grad_norm': '0.1803', 'learning_rate': '8.254e-05', 'epoch': '0.6031'}
# {'loss': '2.557', 'grad_norm': '0.1783', 'learning_rate': '8.148e-05', 'epoch': '0.6082'}
# {'loss': '2.538', 'grad_norm': '0.17', 'learning_rate': '8.042e-05', 'epoch': '0.6134'}
# {'loss': '2.511', 'grad_norm': '0.174', 'learning_rate': '7.937e-05', 'epoch': '0.6186'}
# {'loss': '2.516', 'grad_norm': '0.1733', 'learning_rate': '7.831e-05', 'epoch': '0.6237'}
# {'loss': '2.54', 'grad_norm': '0.1795', 'learning_rate': '7.725e-05', 'epoch': '0.6289'}
# {'loss': '2.513', 'grad_norm': '0.1662', 'learning_rate': '7.619e-05', 'epoch': '0.634'}
# {'loss': '2.505', 'grad_norm': '0.1664', 'learning_rate': '7.513e-05', 'epoch': '0.6392'}
# {'loss': '2.515', 'grad_norm': '0.182', 'learning_rate': '7.407e-05', 'epoch': '0.6443'}
# {'loss': '2.504', 'grad_norm': '0.1838', 'learning_rate': '7.302e-05', 'epoch': '0.6495'}
# {'loss': '2.498', 'grad_norm': '0.1647', 'learning_rate': '7.196e-05', 'epoch': '0.6546'}
# {'loss': '2.521', 'grad_norm': '0.1699', 'learning_rate': '7.09e-05', 'epoch': '0.6598'}
# {'loss': '2.522', 'grad_norm': '0.1703', 'learning_rate': '6.984e-05', 'epoch': '0.6649'}
# {'loss': '2.543', 'grad_norm': '0.173', 'learning_rate': '6.878e-05', 'epoch': '0.6701'}
# {'loss': '2.488', 'grad_norm': '0.1738', 'learning_rate': '6.772e-05', 'epoch': '0.6753'}
# {'loss': '2.513', 'grad_norm': '0.1764', 'learning_rate': '6.667e-05', 'epoch': '0.6804'}
# {'loss': '2.482', 'grad_norm': '0.1722', 'learning_rate': '6.561e-05', 'epoch': '0.6856'}
# {'loss': '2.561', 'grad_norm': '0.1768', 'learning_rate': '6.455e-05', 'epoch': '0.6907'}
# {'loss': '2.639', 'grad_norm': '0.1705', 'learning_rate': '6.349e-05', 'epoch': '0.6959'}
# {'loss': '2.596', 'grad_norm': '0.1701', 'learning_rate': '6.243e-05', 'epoch': '0.701'}
# {'loss': '2.455', 'grad_norm': '0.163', 'learning_rate': '6.138e-05', 'epoch': '0.7062'}
# {'loss': '2.507', 'grad_norm': '0.1739', 'learning_rate': '6.032e-05', 'epoch': '0.7113'}
# {'loss': '2.509', 'grad_norm': '0.1831', 'learning_rate': '5.926e-05', 'epoch': '0.7165'}
# {'loss': '2.48', 'grad_norm': '0.1666', 'learning_rate': '5.82e-05', 'epoch': '0.7216'}
# {'loss': '2.523', 'grad_norm': '0.169', 'learning_rate': '5.714e-05', 'epoch': '0.7268'}
# {'loss': '2.452', 'grad_norm': '0.1627', 'learning_rate': '5.608e-05', 'epoch': '0.732'}
# {'loss': '2.501', 'grad_norm': '0.1686', 'learning_rate': '5.503e-05', 'epoch': '0.7371'}
# {'loss': '2.497', 'grad_norm': '0.1742', 'learning_rate': '5.397e-05', 'epoch': '0.7423'}
# {'loss': '2.508', 'grad_norm': '0.1726', 'learning_rate': '5.291e-05', 'epoch': '0.7474'}
# {'loss': '2.455', 'grad_norm': '0.1632', 'learning_rate': '5.185e-05', 'epoch': '0.7526'}
# {'loss': '2.476', 'grad_norm': '0.165', 'learning_rate': '5.079e-05', 'epoch': '0.7577'}
# {'loss': '2.494', 'grad_norm': '0.1677', 'learning_rate': '4.974e-05', 'epoch': '0.7629'}
# {'loss': '2.566', 'grad_norm': '0.1695', 'learning_rate': '4.868e-05', 'epoch': '0.768'}
# {'loss': '2.557', 'grad_norm': '0.1737', 'learning_rate': '4.762e-05', 'epoch': '0.7732'}
# {'loss': '2.484', 'grad_norm': '0.1681', 'learning_rate': '4.656e-05', 'epoch': '0.7784'}
# {'loss': '2.524', 'grad_norm': '0.1725', 'learning_rate': '4.55e-05', 'epoch': '0.7835'}
# {'loss': '2.486', 'grad_norm': '0.1712', 'learning_rate': '4.444e-05', 'epoch': '0.7887'}
# {'loss': '2.491', 'grad_norm': '0.1716', 'learning_rate': '4.339e-05', 'epoch': '0.7938'}
# {'loss': '2.497', 'grad_norm': '0.1729', 'learning_rate': '4.233e-05', 'epoch': '0.799'}
# {'loss': '2.549', 'grad_norm': '0.1706', 'learning_rate': '4.127e-05', 'epoch': '0.8041'}
# {'loss': '2.517', 'grad_norm': '0.1749', 'learning_rate': '4.021e-05', 'epoch': '0.8093'}
# {'loss': '2.484', 'grad_norm': '0.1725', 'learning_rate': '3.915e-05', 'epoch': '0.8144'}
# {'loss': '2.493', 'grad_norm': '0.1764', 'learning_rate': '3.81e-05', 'epoch': '0.8196'}
# {'loss': '2.488', 'grad_norm': '0.1808', 'learning_rate': '3.704e-05', 'epoch': '0.8247'}
# {'loss': '2.492', 'grad_norm': '0.1738', 'learning_rate': '3.598e-05', 'epoch': '0.8299'}
# {'loss': '2.539', 'grad_norm': '0.1666', 'learning_rate': '3.492e-05', 'epoch': '0.8351'}
# {'loss': '2.447', 'grad_norm': '0.1667', 'learning_rate': '3.386e-05', 'epoch': '0.8402'}
# {'loss': '2.518', 'grad_norm': '0.1806', 'learning_rate': '3.28e-05', 'epoch': '0.8454'}
# {'loss': '2.483', 'grad_norm': '0.1705', 'learning_rate': '3.175e-05', 'epoch': '0.8505'}
# {'loss': '2.49', 'grad_norm': '0.1664', 'learning_rate': '3.069e-05', 'epoch': '0.8557'}
# {'loss': '2.459', 'grad_norm': '0.1664', 'learning_rate': '2.963e-05', 'epoch': '0.8608'}
# {'loss': '2.511', 'grad_norm': '0.1741', 'learning_rate': '2.857e-05', 'epoch': '0.866'}
# {'loss': '2.462', 'grad_norm': '0.1683', 'learning_rate': '2.751e-05', 'epoch': '0.8711'}
# {'loss': '2.561', 'grad_norm': '0.1708', 'learning_rate': '2.646e-05', 'epoch': '0.8763'}
# {'loss': '2.517', 'grad_norm': '0.1727', 'learning_rate': '2.54e-05', 'epoch': '0.8814'}
# {'loss': '2.421', 'grad_norm': '0.1724', 'learning_rate': '2.434e-05', 'epoch': '0.8866'}
# {'loss': '2.518', 'grad_norm': '0.1775', 'learning_rate': '2.328e-05', 'epoch': '0.8918'}
# {'loss': '2.465', 'grad_norm': '0.1646', 'learning_rate': '2.222e-05', 'epoch': '0.8969'}
# {'loss': '2.502', 'grad_norm': '0.1695', 'learning_rate': '2.116e-05', 'epoch': '0.9021'}
# {'loss': '2.558', 'grad_norm': '0.1731', 'learning_rate': '2.011e-05', 'epoch': '0.9072'}
# {'loss': '2.501', 'grad_norm': '0.1738', 'learning_rate': '1.905e-05', 'epoch': '0.9124'}
# {'loss': '2.542', 'grad_norm': '0.1664', 'learning_rate': '1.799e-05', 'epoch': '0.9175'}
# {'loss': '2.512', 'grad_norm': '0.172', 'learning_rate': '1.693e-05', 'epoch': '0.9227'}
# {'loss': '2.491', 'grad_norm': '0.1671', 'learning_rate': '1.587e-05', 'epoch': '0.9278'}
# {'loss': '2.529', 'grad_norm': '0.1697', 'learning_rate': '1.481e-05', 'epoch': '0.933'}
# {'loss': '2.511', 'grad_norm': '0.1675', 'learning_rate': '1.376e-05', 'epoch': '0.9381'}
# {'loss': '2.495', 'grad_norm': '0.1731', 'learning_rate': '1.27e-05', 'epoch': '0.9433'}
# {'loss': '2.544', 'grad_norm': '0.1759', 'learning_rate': '1.164e-05', 'epoch': '0.9485'}
# {'loss': '2.495', 'grad_norm': '0.172', 'learning_rate': '1.058e-05', 'epoch': '0.9536'}
# {'loss': '2.492', 'grad_norm': '0.1656', 'learning_rate': '9.524e-06', 'epoch': '0.9588'}
# {'loss': '2.464', 'grad_norm': '0.1622', 'learning_rate': '8.466e-06', 'epoch': '0.9639'}
# {'loss': '2.456', 'grad_norm': '0.1649', 'learning_rate': '7.407e-06', 'epoch': '0.9691'}
# {'loss': '2.477', 'grad_norm': '0.1775', 'learning_rate': '6.349e-06', 'epoch': '0.9742'}
# {'loss': '2.526', 'grad_norm': '0.1684', 'learning_rate': '5.291e-06', 'epoch': '0.9794'}
# {'loss': '2.488', 'grad_norm': '0.1721', 'learning_rate': '4.233e-06', 'epoch': '0.9845'}
# {'loss': '2.528', 'grad_norm': '0.173', 'learning_rate': '3.175e-06', 'epoch': '0.9897'}
# {'loss': '2.473', 'grad_norm': '0.167', 'learning_rate': '2.116e-06', 'epoch': '0.9948'}
# {'loss': '2.484', 'grad_norm': '0.2756', 'learning_rate': '1.058e-06', 'epoch': '1'}
