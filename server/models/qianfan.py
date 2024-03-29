import json
import requests
import logging
from flask import request, Response, stream_with_context
from typing import Generator, Union

qianfan_urls = {
    # "qianfan_llama2_13b_food": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/h5t0irbl_llama2_13_food_pull",
    "qianfan_llama2_13b_teacher": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/qp7smcbs_order_food_v3",
    "qianfan_llama2_7b_teacher": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/tyz3x2d7_ai_teacher_0130",
    "qianfan_ernie_bot_4": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro",
    "qianfan_ernie_bot_8k": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie_bot_8k",
}


class QianfanGenerator:

    @staticmethod
    def get_access_token():
        """
        使用 API Key，Secret Key 获取access_token，替换下列示例中的应用API Key、应用Secret Key
        """
        api_key = "6XdqvUoscZfTaorjiPXMoj7K"
        secret_key = "lRUb9Hpo8xy1uQmKPfU1o1s0HoLD8Syc"

        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"

        payload = json.dumps("")
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json().get("access_token")

    @staticmethod
    def request_qianfan(model, messages, stream):
        if model == "qianfan_ernie_bot_8k":
            print("request_qianfan_ernie_bot_8k")
            return QianfanGenerator.generate_ernie_bot(model, messages, stream)
            # return QianfanGenerator.generate_ernie_bot_8k(messages, stream)
        elif model == "qianfan_ernie_bot_4":
            print("request_qianfan_ernie_bot_4")
            # return QianfanGenerator.generate_ernie_bot_4(messages, stream)
            return QianfanGenerator.generate_ernie_bot(model, messages, stream)
        elif model == "qianfan_llama2_7b_teacher":
            print("request_qianfan_llama2_7b_teacher")
            # return "暂停服务，联系yuanconghao开通"
            return QianfanGenerator.generate_llama2_chat(model, messages, stream)
        elif model == "qianfan_llama2_13b_teacher":
            print("request_qianfan_llama2_13b_teacher")
            return "暂停服务，联系yuanconghao开通"
            # return QianfanGenerator.generate_llama2_chat(model, messages, stream)
        elif model == "qianfan_ernie_food":
            print("request_qianfan_ernie_food")
            return "暂停服务，联系yuanconghao开通"
            # return QianfanGenerator.generate_ernie_bot(model, messages, stream)

    @staticmethod
    def generate_ernie_bot(model, messages, stream):
        url = qianfan_urls[model]
        url += "?access_token=" + QianfanGenerator.get_access_token()
        query_messages = {
            "messages": messages
        }
        if stream:
            query_messages["stream"] = True

        payload = json.dumps(query_messages)

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload, stream=stream)
        print(response)

        if stream:
            print(type(response))
            return QianfanGenerator.compact_response(response)

        answer = response.json()['result']

        return Response(answer)

    @staticmethod
    def generate_llama2_chat(model, messages, stream):
        url = qianfan_urls[model]
        url += "?access_token=" + QianfanGenerator.get_access_token()
        # system = "You will play my English teacher, Now simulate a scene of ordering food, you role is a waiter, my role is a customer who wants to order food."
        system = ""
        query_messages = {
            "messages": messages,
            "system": system,
            "temperature": 0.5
        }
        if stream:
            query_messages["stream"] = True

        payload = json.dumps(query_messages)

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response)

        if stream:
            return QianfanGenerator.compact_response(response)

        print(response.text)
        answer = json.loads(response.text)['result']

        return Response(answer)

    @staticmethod
    def generate_ernie_bot_4(messages, stream):
        url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token=" + QianfanGenerator.get_access_token()
        query_messages = {
            "messages": messages
        }
        if stream:
            query_messages["stream"] = True

        payload = json.dumps(query_messages)

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload, stream=stream)
        print(response)

        if stream:
            print(type(response))
            return QianfanGenerator.compact_response(response)

        answer = response.json()['result']

        return Response(answer)

    @staticmethod
    def generate_ernie_bot_8k(messages, stream):

        url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie_bot_8k?access_token=" + QianfanGenerator.get_access_token()
        query_messages = {
            "messages": messages
        }
        if stream:
            query_messages["stream"] = True

        payload = json.dumps(query_messages)

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload, stream=stream)
        print(response)

        if stream:
            print(type(response))
            return QianfanGenerator.compact_response(response)

        answer = response.json()['result']

        return Response(answer)

    @staticmethod
    def generate_ernie_chat_food(messages, stream):
        url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/w9pj7qpt_order_food_15_ernie4?access_token=" + QianfanGenerator.get_access_token()
        system = "As an English teacher you will give an oral lesson to a young learner. The user is at a restaurant and wants to order food. You need to correct students when they get off topic. Communicate in English"
        query_messages = {
            "messages": messages,
            "system": system
        }
        if stream:
            query_messages["stream"] = True

        payload = json.dumps(query_messages)

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload, stream=stream)
        print("ernie============")
        print(response)

        if stream:
            print(type(response))
            return QianfanGenerator.compact_response(response)

        answer = response.json()['result']

        return Response(answer)

    @staticmethod
    def generate_llama2_chat_food(messages, stream):
        print("generate_llama2_chat_food==============")
        print(messages)
        """
        request gpt
        """
        system = "As an English teacher you will give an oral lesson to a young learner. The user is at a restaurant and wants to order food. You need to correct students when they get off topic."
        url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/rlxj7x8a_llama2_food_v2?access_token=" + QianfanGenerator.get_access_token()
        print(url)
        query_messages = {
            "messages": messages,
            "system": system
        }
        if stream:
            query_messages["stream"] = True

        payload = json.dumps(query_messages)

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response)

        if stream:
            return QianfanGenerator.compact_response(response)

        print(response.text)
        answer = json.loads(response.text)['result']

        return Response(answer)

    @staticmethod
    def compact_response(response: Union[dict, requests.models.Response, Generator]) -> Response:
        pass
        """
        return stream response
        """
        if isinstance(response, dict):
            # 如果响应是一个字典，直接返回JSON响应
            return Response(response=json.dumps(response), status=200, mimetype='application/json')

        # 如果响应是一个生成器，创建并返回一个流式响应
        def generate() -> Generator:
            try:
                for chunk in response.iter_lines():
                    chunk = chunk.decode("utf-8")
                    print(chunk)
                    if chunk.startswith('data:'):
                        completion = json.loads(chunk[5:])
                        if not completion['is_end'] or completion['result']:
                            # yield json.dumps(completion)
                            yield completion['result']

            except Exception as e:
                # 在生产环境中，应使用日志记录此类错误
                logging.exception("Error while streaming response: %s", e)

        # 使用stream_with_context确保请求上下文在流生成期间保持激活
        return Response(stream_with_context(generate()), status=200, mimetype='text/event-stream')
