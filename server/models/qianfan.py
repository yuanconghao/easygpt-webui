import json
import requests
import logging
from flask import request, Response, stream_with_context
from typing import Generator, Union


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
            return QianfanGenerator.generate_ernie_bot_8k(messages, stream)
        elif model == "qianfan_ernie_bot_4":
            return QianfanGenerator.generate_ernie_bot_4(messages, stream)
        elif model == "qianfan_llama2-7b-food-v1":
            return QianfanGenerator.generate_llama2_chat_food(messages, stream)

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
    def generate_llama2_chat_food(messages, stream):
        stream = False
        print("generate_llama2_chat_food==============")
        print(messages)
        """
        request gpt
        """
        url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/dat2p0c0_llama2_food_v1_loss2?access_token=" + QianfanGenerator.get_access_token()
        print(url)
        query_messages = {
            "messages": messages
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
