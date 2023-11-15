import sys
import torch
from transformers import AutoTokenizer
from flask import Flask, request, jsonify

sys.path.append("../../")
from server.utils.model import ModelUtils

app = Flask(__name__)

# 使用合并后的模型进行推理
# model_name_or_path = '/root/llama2/llama2-chat-hf'
# adapter_name_or_path = None

# 使用base model和adapter进行推理
model_name_or_path = '/root/llama2/llama2-chat-hf'
adapter_name_or_path = '/root/llama2/llama2-qlora-ai-teacher'
# 是否使用4bit进行推理，能够节省很多显存，但效果可能会有一定的下降
load_in_4bit = False
device = 'cuda'

# 生成超参配置
max_new_tokens = 500  # 每轮对话最多生成多少个token
history_max_len = 1000  # 模型记忆的最大token长度
top_p = 0.9
temperature = 0.35
repetition_penalty = 1.0

model = None
tokenizer = None


@app.before_request
def load_model():
    global model, tokenizer
    # 加载模型
    model = ModelUtils.load_model(
        model_name_or_path,
        load_in_4bit=load_in_4bit,
        adapter_name_or_path=adapter_name_or_path
    ).eval()
    # 加载tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        model_name_or_path,
        trust_remote_code=True,
        # llama不支持fast
        use_fast=False
    )


@app.route('/easygpt/llama2/generate', methods=['POST'])
def generate():

    # 获取请求数据
    data = request.get_json(force=True)
    query = data[0]["content"]

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
    model_input_ids = history_token_ids[:, -history_max_len:].to(device)
    with torch.no_grad():
        outputs = model.generate(
            input_ids=model_input_ids,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            top_p=top_p,
            temperature=temperature,
            repetition_penalty=repetition_penalty,
            eos_token_id=tokenizer.eos_token_id
        )
    model_input_ids_len = model_input_ids.size(1)
    response_ids = outputs[:, model_input_ids_len:]
    history_token_ids = torch.concat((history_token_ids, response_ids.cpu()), dim=1)
    print(history_token_ids)
    response = tokenizer.batch_decode(response_ids)
    return response


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9002, debug=True)
