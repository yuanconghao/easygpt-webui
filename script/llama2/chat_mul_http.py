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

    # 对每个query进行推理
    predictions = []
    conversation_history = ''
    for query in data:
        # 将之前的对话历史和新的用户输入组合在一起
        conversation_history += f"{query['role']}: {query['content']}\n"

        # 对输入进行编码
        inputs = tokenizer.encode(conversation_history, return_tensors='pt', add_special_tokens=False)

        # 生成输出
        outputs = model.generate(inputs, max_new_tokens=max_new_tokens, do_sample=True, top_p=top_p,
                                 temperature=temperature, repetition_penalty=repetition_penalty, num_return_sequences=1)

        # 解码输出
        new_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
        new_output = new_output[len(conversation_history):].strip()

        # 添加新的输出到对话历史
        conversation_history += f"assistant: {new_output}\n"

        predictions.append({'content': new_output, 'role': 'bot'})

    # 返回推理结果
    return jsonify(predictions)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9002, debug=True)
