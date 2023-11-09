import re
import os
import io
from datetime import datetime
from flask import request, Response, stream_with_context, send_file
from requests import get
from server.config import special_instructions
import openai
import json
import logging
from typing import Generator, Union
import time


class Backend_Api:
    def __init__(self, bp, config: dict) -> None:
        """
        Initialize the Backend_Api class.
        :param app: Flask application instance
        :param config: Configuration dictionary
        """
        self.bp = bp
        self.routes = {
            '/backend-api/v2/conversation': {
                'function': self._conversation,
                'methods': ['POST']
            },
            '/backend-api/v2/generate_tts': {
                'function': self._generate_tts,
                'methods': ['POST']
            },
        }

    def _generate_tts(self):
        print(request.json)
        text = request.json['text']
        voice = request.json['voice']
        print(text)
        time1 = time.time()
        response = openai.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text.strip(),
        )

        # Convert the binary response content to a byte stream
        byte_stream = io.BytesIO(response.content)
        byte_stream.name = 'audio.mp3'
        time2 = time.time()
        cost = time2 - time1
        character_num = len(text)
        info = {
            "cost": cost,
            "c_nums": character_num,
        }
        print(info)
        return send_file(byte_stream, mimetype='audio/mp3')

    def _conversation(self):
        """
        Handles the conversation route.

        :return: Response object containing the generated conversation stream
        """
        conversation_id = request.json['conversation_id']

        try:
            model = request.json['model']
            print(request.json)
            conversation = request.json['meta']['content']['conversation']
            prompt = request.json['meta']['content']['parts'][0]
            conversation.append(prompt)
            messages = conversation
            print("=================")
            print("messages:", messages)
            stream = request.json["meta"]["content"]["internet_access"]

            # Generate response
            openai.api_key = os.environ.get("OPENAI_API_KEY_EASY")
            print(openai.api_key)

            response = openai.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.5,
                max_tokens=2048,
                stream=stream,
            )
            print("response==================")
            print(response)
            if stream:
                return compact_response(response)

            answer = response.choices[0].message.content
            return Response(answer)

        except Exception as e:
            print(e)
            print(e.__traceback__.tb_next)

            return {
                       '_action': '_ask',
                       'success': False,
                       "error": f"an error occurred {str(e)}"
                   }, 400

    def _conversation1(self):
        """  
        Handles the conversation route.  

        :return: Response object containing the generated conversation stream  
        """
        conversation_id = request.json['conversation_id']

        try:
            model = request.json['model']

            print(request.json)
            conversation = request.json['meta']['content']['conversation']
            prompt = request.json['meta']['content']['parts'][0]
            conversation.append(prompt)
            messages = conversation
            print("=================")
            print("messages:", messages)
            stream = request.json["meta"]["content"]["internet_access"]

            # Generate response
            openai.api_key = os.environ.get("OPENAI_API_KEY_EASY")
            print(openai.api_key)

            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0.5,
                max_tokens=2048,
                stream=stream,
            )
            print("response==================")
            print(response)
            if stream:
                return compact_response1(response)

            answer = response["choices"][0]["message"]["content"]
            return Response(answer)

        except Exception as e:
            print(e)
            print(e.__traceback__.tb_next)

            return {
                       '_action': '_ask',
                       'success': False,
                       "error": f"an error occurred {str(e)}"
                   }, 400


def compact_response(response: Union[dict, Generator]) -> Response:
    if isinstance(response, dict):
        # 如果响应是一个字典，直接返回JSON响应
        return Response(response=json.dumps(response), status=200, mimetype='application/json')
    else:
        # 如果响应是一个生成器，创建并返回一个流式响应
        def generate() -> Generator:
            try:
                for chunk in response:
                    # print(chunk)
                    # 假设chunk是流式API返回的数据结构
                    # 你可能需要根据实际的数据结构进行调整
                    if chunk.choices[0].finish_reason != 'stop':
                        yield chunk.choices[0].delta.content
            except Exception:
                # 在生产环境中，应使用日志记录此类错误
                logging.exception("internal server error.")

        # 使用stream_with_context确保请求上下文在流生成期间保持激活
        return Response(stream_with_context(generate()), status=200, mimetype='text/event-stream')


def compact_response1(response: Union[dict, Generator]) -> Response:
    if isinstance(response, dict):
        # 如果响应是一个字典，直接返回JSON响应
        return Response(response=json.dumps(response), status=200, mimetype='application/json')
    else:
        # 如果响应是一个生成器，创建并返回一个流式响应
        def generate() -> Generator:
            try:
                for chunk in response:
                    # 假设chunk是流式API返回的数据结构
                    # 你可能需要根据实际的数据结构进行调整
                    yield chunk.choices[0].delta.get("content", "")
            except Exception:
                # 在生产环境中，应使用日志记录此类错误
                logging.exception("internal server error.")

        # 使用stream_with_context确保请求上下文在流生成期间保持激活
        return Response(stream_with_context(generate()), status=200, mimetype='text/event-stream')


def build_messages(jailbreak):
    """  
    Build the messages for the conversation.  

    :param jailbreak: Jailbreak instruction string  
    :return: List of messages for the conversation  
    """
    print(request.json)
    _conversation = request.json['meta']['content']['conversation']
    internet_access = request.json['meta']['content']['internet_access']
    prompt = request.json['meta']['content']['parts'][0]

    # Add the existing conversation
    conversation = _conversation

    # Add web results if enabled
    if internet_access:
        current_date = datetime.now().strftime("%Y-%m-%d")
        query = f'Current date: {current_date}. ' + prompt["content"]
        search_results = fetch_search_results(query)
        conversation.extend(search_results)

    print("=======================")
    # Add jailbreak instructions if enabled
    if jailbreak_instructions := getJailbreak(jailbreak):
        conversation.extend(jailbreak_instructions)

    # Add the prompt
    conversation.append(prompt)

    # Reduce conversation size to avoid API Token quantity error
    if len(conversation) > 3:
        conversation = conversation[-4:]

    return conversation


def fetch_search_results(query):
    """  
    Fetch search results for a given query.  

    :param query: Search query string  
    :return: List of search results  
    """
    search = get('https://ddg-api.herokuapp.com/search',
                 params={
                     'query': query,
                     'limit': 3,
                 })

    snippets = ""
    for index, result in enumerate(search.json()):
        snippet = f'[{index + 1}] "{result["snippet"]}" URL:{result["link"]}.'
        snippets += snippet

    response = "Here are some updated web searches. Use this to improve user response:"
    response += snippets

    return [{'role': 'system', 'content': response}]


def generate_stream(response):
    """
    Generate the conversation stream.

    :param response: Response object from ChatCompletion.create
    :param jailbreak: Jailbreak instruction string
    :return: Generator object yielding messages in the conversation
    """
    yield from response


def response_jailbroken_success(response: str) -> bool:
    """Check if the response has been jailbroken.

    :param response: Response string
    :return: Boolean indicating if the response has been jailbroken
    """
    act_match = re.search(r'ACT:', response, flags=re.DOTALL)
    return bool(act_match)


def response_jailbroken_failed(response):
    """
    Check if the response has not been jailbroken.

    :param response: Response string
    :return: Boolean indicating if the response has not been jailbroken
    """
    return False if len(response) < 4 else not (response.startswith("GPT:") or response.startswith("ACT:"))


def getJailbreak(jailbreak):
    """  
    Check if jailbreak instructions are provided.  

    :param jailbreak: Jailbreak instruction string  
    :return: Jailbreak instructions if provided, otherwise None  
    """
    if jailbreak != "default":
        special_instructions[jailbreak][0]['content'] += special_instructions['two_responses_instruction']
        if jailbreak in special_instructions:
            special_instructions[jailbreak]
            return special_instructions[jailbreak]
        else:
            return None
    else:
        return None
