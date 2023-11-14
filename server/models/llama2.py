from transformers import AutoTokenizer
from peft import PeftModel
import torch
from server.utils.model import ModelUtils

if torch.cuda.is_available():
    device = "cuda"


class LLama2Generator:
    # 使用合并后的模型进行推理
    base_model = '/root/llama2/llama2-chat-hf'
    lora_weights = '/root/llama2/llama2-qlora-ai-teacher'
    adapter_name_or_path = None

    # 使用base model和adapter进行推理
    # model_name_or_path = 'baichuan-inc/Baichuan-7B'
    # adapter_name_or_path = 'YeungNLP/firefly-baichuan-7b-qlora-sft'

    # 是否使用4bit进行推理，能够节省很多显存，但效果可能会有一定的下降
    load_in_4bit = False
    if torch.cuda.is_available():
        device = "cuda"

    # 生成超参配置
    max_new_tokens = 500  # 每轮对话最多生成多少个token
    history_max_len = 1000  # 模型记忆的最大token长度
    top_p = 0.9
    temperature = 0.35
    repetition_penalty = 1.0

    def __init__(self):
        LLama2Generator.load_model()

    @staticmethod
    def load_model(lora=False):
        model, tokenizer = LLama2Generator.huggingface_loader(), LLama2Generator.load_tokenizer()
        if lora:
            # 加载lora权重
            model = PeftModel.from_pretrained(
                model,
                LLama2Generator.lora_weights,
                torch_dtype=torch.float16,
            )
        return model, tokenizer

    @staticmethod
    def huggingface_loader():
        # 加载模型
        model = ModelUtils.load_model(
            LLama2Generator.base_model,
            load_in_4bit=False,
            adapter_name_or_path=LLama2Generator.adapter_name_or_path
        )
        return model

    @staticmethod
    def load_tokenizer():
        # 加载tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            LLama2Generator.base_model,
            trust_remote_code=True,
            # llama不支持fast
            use_fast=False,
        )
        return tokenizer

    @staticmethod
    def generate_llama2(model, tokenizer, query):
        # 记录所有历史记录
        history_token_ids = torch.tensor([[tokenizer.bos_token_id]], dtype=torch.long)

        # 开始对话
        utterance_id = 0  # 记录当前是第几轮对话，为了契合chatglm的数据组织格式
        user_input = query
        utterance_id += 1
        input_ids = tokenizer(user_input, return_tensors="pt", add_special_tokens=False).input_ids
        eos_token_id = torch.tensor([[tokenizer.eos_token_id]], dtype=torch.long)
        user_input_ids = torch.concat([input_ids, eos_token_id], dim=1)
        history_token_ids = torch.concat((history_token_ids, user_input_ids), dim=1)
        model_input_ids = history_token_ids[:, -LLama2Generator.history_max_len:].to(device)
        with torch.no_grad():
            outputs = model.generate(
                input_ids=model_input_ids,
                max_new_tokens=LLama2Generator.max_new_tokens,
                do_sample=True,
                top_p=LLama2Generator.top_p,
                temperature=LLama2Generator.temperature,
                repetition_penalty=LLama2Generator.repetition_penalty,
                eos_token_id=tokenizer.eos_token_id
            )
        model_input_ids_len = model_input_ids.size(1)
        response_ids = outputs[:, model_input_ids_len:]
        history_token_ids = torch.concat((history_token_ids, response_ids.cpu()), dim=1)
        print(history_token_ids)
        response = tokenizer.batch_decode(response_ids)
        return response
