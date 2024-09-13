import json
import logging
import openai
from flask import request, Response, stream_with_context, send_file, url_for
from typing import Generator, Union


class GPTGenerator:

    @staticmethod
    def request_o(model, messages, stream):
        """
        request o1
        """
        response = openai.chat.completions.create(
            model=model,
            messages=messages
        )
        print("response==================")
        print(response)

        answer = response.choices[0].message.content
        return Response(answer)

    @staticmethod
    def request_gpt(model, messages, stream):
        """
        request gpt
        """
        response = openai.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.5,
            max_tokens=4096,
            stream=stream,
        )
        print("response==================")
        print(response)
        if stream:
            return GPTGenerator.compact_response(response)

        answer = response.choices[0].message.content

        result = {
            "id": "",
            "content": answer
        }
        return Response(answer)

    @staticmethod
    def request_dalle(messages):
        """
        request dalle
        """
        response = openai.images.generate(
            model="dall-e-3",
            prompt=messages,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        revised_prompt = response.data[0].revised_prompt
        image_url = response.data[0].url
        link_image_url = f"![图片)]({image_url})"

        result = {
            "id": "",
            "content": revised_prompt + "\n\n" + link_image_url
        }
        return Response(revised_prompt + "\n\n" + link_image_url)

    @staticmethod
    def request_vision(messages):
        """
        request vision
        """
        response = openai.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=1024,
            stream=False,
        )
        answer = response.choices[0].message.content

        link_image_url = ""
        for content in messages[0]["content"]:
            if content["type"] != "image_url":
                continue
            link_image_url += f"![图片)]({content['image_url']['url']}) "

        result = {
            "id": "",
            "content": answer + "\n\n" + link_image_url
        }
        return Response(answer + "\n\n" + link_image_url)

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
                    # 假设chunk是流式API返回的数据结构
                    # 你可能需要根据实际的数据结构进行调整
                    if chunk.choices[0].finish_reason != 'stop':
                        yield chunk.choices[0].delta.content
            except Exception:
                # 在生产环境中，应使用日志记录此类错误
                logging.exception("internal server error.")

        # 使用stream_with_context确保请求上下文在流生成期间保持激活
        return Response(stream_with_context(generate()), status=200, mimetype='text/event-stream')
