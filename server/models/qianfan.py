import json
import requests
import logging
import openai
from flask import request, Response, stream_with_context, send_file, url_for
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
    def compact_response(response: Union[dict, Generator]) -> Response:
        """
        return stream response
        """
        if isinstance(response, dict):
            # 如果响应是一个字典，直接返回JSON响应
            return Response(response=json.dumps(response), status=200, mimetype='application/json')

        # 如果响应是一个生成器，创建并返回一个流式响应
        def generate() -> Generator:
            try:
                for chunk in response:
                    print(chunk)
                    chunk_str = chunk.decode()
                    print(chunk_str)
                    yield chunk_str['result']
                    # if chunk_str.startswith('data: '):
                    #     chunk_str = chunk_str[6:]
                    # chunk_dict = json.loads(chunk_str)
                    # if chunk_dict['is_end'] != True:
                    #     yield chunk_dict["result"]
                    # 假设chunk是流式API返回的数据结构
                    # 你可能需要根据实际的数据结构进行调整
                    # if chunk.is_end != True:
                    #     yield chunk.result
            except Exception:
                # 在生产环境中，应使用日志记录此类错误
                logging.exception("internal server error.")

        # 使用stream_with_context确保请求上下文在流生成期间保持激活
        return Response(stream_with_context(generate()), status=200, mimetype='text/event-stream')
