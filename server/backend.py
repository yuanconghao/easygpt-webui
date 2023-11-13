import re
import os
import io
from datetime import datetime
from flask import request, Response, stream_with_context, send_file, url_for
from requests import get
from server.config import special_instructions
import openai
import json
import logging
from typing import Generator, Union
import time
import tempfile
from pydub import AudioSegment
from werkzeug.utils import secure_filename
from .utils.imgbb import upload_bb

openai.api_key = os.environ.get("OPENAI_API_KEY_EASY")
print(openai.api_key)


class Backend_Api:
    def __init__(self, bp, app, config: dict) -> None:
        """
        Initialize the Backend_Api class.
        :param app: Flask application instance
        :param config: Configuration dictionary
        """
        self.app = app
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
            '/backend-api/v2/generate_asr': {
                'function': self._generate_asr,
                'methods': ['POST', 'GET']
            },
            '/backend-api/v2/uploads': {
                'function': self._uploads,
                'methods': ['POST']
            },
        }

    def _uploads(self):
        print("uploads===============")
        images_path = os.path.join(self.app.static_folder)
        print(images_path)
        if not os.path.exists(images_path):
            os.makedirs(images_path)
        print(request.files)

        if 'files' not in request.files:
            return {'code': 100001, 'msg': 'No file part'}, 400

        files = request.files.getlist('files')
        print(files)
        if not files or files[0].filename == '':
            return {'code': 100002, 'msg': 'No selected file'}, 400

        file_urls = []
        bb_urls = []
        for i, file in enumerate(files):
            print(i)
            ext = os.path.splitext(file.filename)[1]
            new_filename = datetime.now().strftime("%Y%m%d%H%M%S%f") + ('-%d' % i) + ext
            new_filename = secure_filename(new_filename)
            file.save(os.path.join(images_path, new_filename))
            file_url = url_for('static', filename=new_filename)
            file_urls.append(file_url)

            # upload bb
            upload_bb_url = "https://kcs.51talk.com/easygpt" + file_url
            # upload_bb_url = "http://127.0.0.1:8060/easygpt" + file_url
            print(upload_bb_url)
            bb_url = upload_bb(os.path.join(images_path, new_filename))
            bb_urls.append(bb_url)

        return {'code': 100000, 'msg': 'upload success', 'data': {'bb_path': str(bb_urls), 'path': str(file_urls)}}, 200

    def _generate_asr(self):
        print(request.args)
        lang = request.args.get('lang')
        audio_file = request.files['audio']
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        audio_file.save(temp_file.name)

        print(audio_file)
        print(temp_file.name)

        file_data = open(temp_file.name, "rb")
        # with open(temp_file.name, 'rb') as f:
        #     file_data = f.read()

        if lang:
            print("lang----------------")
            response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=file_data,
                language=lang
            )
        else:
            print('default----------------')
            response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=file_data,
            )
        os.unlink(temp_file.name)

        print(response)
        return response.text

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
            print(request.json)
            model = request.json['model']
            conversation = request.json['meta']['content']['conversation']
            prompt = request.json['meta']['content']['parts'][0]
            send_images = request.json["send_images"]
            images = []
            if send_images:
                send_images = send_images.replace("'", "\"")
                images = json.loads(send_images)

            messages = build_messages(model, conversation, prompt, images)
            print("conversation==================")
            print(messages)

            stream = request.json["meta"]["content"]["internet_access"]
            # Generate response

            if model == "dall-e-3":
                print("delle3==================")
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
                return Response(revised_prompt + "\n\n" + link_image_url)

            elif model == "gpt-4-vision-preview":
                print("gpt4v==================")
                response = openai.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=1024,
                    stream=stream,
                )
                answer = response.choices[0].message.content
                return Response(answer)

            else:
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


def convert_audio_to_wav(file_path):
    audio = AudioSegment.from_file(file_path)
    new_file_path = file_path + ".wav"
    audio.export(new_file_path, format="wav")
    return new_file_path


def build_messages(model, conversation, prompt, images=[]):
    if model == "dall-e-3":
        return prompt['content']
    elif model == "gpt-4-vision-preview":
        new_content = []

        new_text = {
            "type": "text",
            "text": prompt["content"]
        }
        new_content.append(new_text)

        if not images:
            new_messages = {
                "role": "user",
                "content": new_content
            }
            # return conversation.append(new_messages)
            # 不要历史记录
            return [new_messages]

        for image in images:
            new_img_url = {
                "type": "image_url",
                "image_url": {
                    "url": image
                }
            }
            new_content.append(new_img_url)

        new_messages = {
            "role": "user",
            "content": new_content
        }
        return [new_messages]

    else:
        conversation.append(prompt)
        messages = conversation
        return messages


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
