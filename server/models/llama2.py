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

            outputs = model.generate(**inputs, max_length=1024)
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
    def generate_llama2_chat(model, tokenizer, query):
        print("llama2_chat===========")
        utterance_id = 0
        try:
            history_token_ids = torch.tensor([[tokenizer.bos_token_id]], dtype=torch.long)
            utterance_id += 1
            input_ids = tokenizer(query, return_tensors="pt", add_special_tokens=False).input_ids
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
            response = tokenizer.batch_decode(response_ids)
            print("Assistant：" + response[0].strip().replace(tokenizer.eos_token, ""))

            # Decode the response
            answer = response[0].strip().replace(tokenizer.eos_token, "")

            result = {
                "id": "",
                "content": answer
            }
            return Response(json.dumps(result))

        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def generate_llama2_chat_ids(model, tokenizer, query, history_token_ids=None):
        print("history_token_ids1:", history_token_ids)
        if history_token_ids is None:
            # Initialize conversation history if not provided
            history_token_ids = [tokenizer.encode(tokenizer.bos_token, add_special_tokens=False)]

        print("history_token_ids2:", history_token_ids)
        # Append user input to history
        user_input_ids = tokenizer.encode(query, add_special_tokens=True)

        print(tokenizer.encode("helo", add_special_tokens=True))
        print(tokenizer.encode("helo, I'm glad you're here! How are you?", add_special_tokens=True))

        history_token_ids.append(user_input_ids)
        print("history_token_ids3:", history_token_ids)

        # Flatten the history_token_ids list
        flat_history = [item for sublist in history_token_ids for item in sublist]
        print("flat_history:", flat_history)
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

        print(response_ids)
        # Append response to history
        history_token_ids.append(response_ids[0].tolist())
        print("history_token_ids4:", history_token_ids)
        # Decode the response
        answer = tokenizer.decode(response_ids[0], skip_special_tokens=True)

        result = {
            "id": history_token_ids,
            "content": answer
        }
        return Response(json.dumps(result))

    import textwrap

    def display_response(prompt, generated_response, max_width=120):
        # Function to print a bordered text box
        def print_boxed(text):
            lines = textwrap.wrap(text, max_width)  # Wrap text to desired width
            border = '+' + '-' * (max_width + 2) + '+'
            print(border)
            for line in lines:
                print('| ' + line.ljust(max_width) + ' |')
            print(border)

        # Extract the instruction and the patient's query from the prompt
        instruction_start = prompt.find("[INST]") + len("[INST]")
        instruction_end = prompt.find("[/INST]")
        instruction = prompt[instruction_start:instruction_end].strip()

        prefix = "As a medical doctor, respond to this patient query: Patient: "
        if instruction.startswith(prefix):
            instruction = instruction[len(prefix):].strip()

        # Extract the generated text from the response dictionary
        response_text = generated_response[0]['generated_text']

        # Extract the medical doctor's response from the generated text
        doctor_response_start = response_text.find("[/INST]") + len("[/INST]")
        doctor_response = response_text[doctor_response_start:].strip()

        # Display the information with a wrapper
        print("Human:")
        print_boxed(instruction)
        print("\nAssistance:")
        print_boxed(doctor_response)


