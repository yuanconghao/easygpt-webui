import json
import torch
from transformers import AutoTokenizer
from peft import PeftModel
from flask import request, Response, stream_with_context, send_file, url_for
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
            load_in_4bit=True,
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
    def generate_llama2_text(model, tokenizer, query):
        print("llama2_text===========")

        try:
            inputs = tokenizer(query, return_tensors="pt").to(device)
            print(inputs)

            outputs = model.generate(**inputs, max_length=512)
            print(outputs)

            if len(outputs) > 0:
                answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
                print(answer)
                result = {
                    "id": "",
                    "content": answer
                }
                return Response(json.dumps(result))
            else:
                return "No text generated."
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def generate_llama2_chat(model, tokenizer, query, history_token_ids=None):
        if history_token_ids is None:
            # Initialize conversation history if not provided
            history_token_ids = [tokenizer.encode(tokenizer.bos_token, add_special_tokens=False)]

        # Append user input to history
        user_input_ids = tokenizer.encode(query, add_special_tokens=True)
        history_token_ids.append(user_input_ids)

        # Flatten the history_token_ids list
        flat_history = [item for sublist in history_token_ids for item in sublist]

        # Generate a response
        with torch.no_grad():
            response_ids = model.generate(
                input_ids=torch.tensor([flat_history], dtype=torch.long).to(device),
                max_length=LLama2Generator.max_new_tokens,
                do_sample=True,
                top_p=LLama2Generator.top_p,
                temperature=LLama2Generator.temperature,
                repetition_penalty=LLama2Generator.repetition_penalty,
                eos_token_id=tokenizer.eos_token_id
            )

        # Append response to history
        history_token_ids.append(response_ids[0].tolist())

        # Decode the response
        answer = tokenizer.decode(response_ids[0], skip_special_tokens=True)

        result = {
            "id": history_token_ids,
            "content": answer
        }
        return Response(json.dumps(result))
