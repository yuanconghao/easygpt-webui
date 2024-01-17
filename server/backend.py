import os
import json
import openai
from datetime import datetime
from flask import request, url_for
from werkzeug.utils import secure_filename
from server.utils.imgbb import upload_bb
from server.models.prompter import Prompter
from server.models.asr import ASRGenerator
from server.models.tts import TTSGenerator
from server.models.gpt import GPTGenerator
from server.models.llama2 import LLama2Generator
from server.models.assistant import AssistantGenerator
from server.models.qianfan import QianfanGenerator
from server.models.corpus import CorpusGenerator

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
        self.config = config
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
            '/backend-api/v2/generate_corpus': {
                'function': self._generate_corpus,
                'methods': ['POST', 'GET']
            },
            '/backend-api/v2/uploads': {
                'function': self._uploads,
                'methods': ['POST']
            },
        }

        llama2 = config['llama2']
        self.model = None
        self.tokenizer = None
        # load model if exist
        if llama2["use"]:
            if self.model is None or self.tokenizer is None:
                self.model, self.tokenizer = LLama2Generator.load_model(llama2["lora"])

    def _generate_asr(self):
        """
        generate asr
        """
        try:
            print("asr===================")
            print(request.args)
            lang = request.args.get('lang')
            audio_file = request.files['audio']
            return ASRGenerator.generate_asr(audio_file, lang)
        except Exception as e:
            print(e)
            print(e.__traceback__.tb_next)
            msg = {
                '_action': '_ask',
                'success': False,
                "error": f"an error occurred {str(e)}"
            }
            return msg, 500003

    def _generate_tts(self):
        """
        generate tts
        """
        try:
            print("tts===================")
            print(request.json)
            text = request.json['text']
            voice = request.json['voice']
            return TTSGenerator.generate_tts(text, voice)
        except Exception as e:
            print(e)
            print(e.__traceback__.tb_next)
            msg = {
                '_action': '_ask',
                'success': False,
                "error": f"an error occurred {str(e)}"
            }
            return msg, 500002

    def _generate_corpus(self):
        """
        generate corpus
        """
        try:
            print("corpus===================")
            print(request.json)
            role_name = request.json['role_name']
            role_style = request.json['role_style']
            cefr_level = request.json['cefr_level']
            teaching_steps = request.json['teaching_steps']
            words = request.json['words']
            sentence = request.json['sentence']
            teaching_goal = request.json['teaching_goal']
            teaching_background = request.json['teaching_background']
            teaching_characters = request.json['teaching_characters']
            teaching_example = request.json['teaching_example']
            corpus_nums = request.json['corpus_nums']
            corpus_format = request.json['corpus_format']
            corpus_func = request.json['corpus_func']
            basic_info = {
                "role_name" : role_name,
                "role_style": role_style,
                "cefr_level": cefr_level,
            }
            teaching_knowledge = {
                "teaching_steps": teaching_steps,
                "words": words,
                "sentence": sentence,
            }
            teaching_method = {
                "teaching_goal": teaching_goal,
                "teaching_background": teaching_background,
                "teaching_characters": teaching_characters,
                "teaching_example": teaching_example,
            }
            corpus_info = {
                "corpus_nums": corpus_nums,
                "corpus_format": corpus_format,
                "corpus_func": corpus_func,
            }

            return CorpusGenerator.generate_corpus(basic_info, teaching_knowledge, teaching_method, corpus_info)
        except Exception as e:
            print(e)
            print(e.__traceback__.tb_next)
            msg = {
                '_action': '_ask',
                'success': False,
                "error": f"an error occurred {str(e)}"
            }
            return msg, 500002

    def _conversation(self):
        """
        conversation
        """
        try:
            print(request.json)
            model = request.json['model']
            session_id = request.json['session_id']
            conversation = request.json['meta']['content']['conversation']
            prompt = request.json['meta']['content']['parts'][0]
            send_images = request.json["send_images"]
            images = []
            if send_images:
                send_images = send_images.replace("'", "\"")
                images = json.loads(send_images)

            if not session_id or session_id == "undefined":
                session_id = None

            messages = Prompter.build_messages(model, conversation, prompt, images)
            print("messages==================")
            print(messages)

            stream = request.json["meta"]["content"]["internet_access"]
            # Generate response

            if model == "dall-e-3":
                print("delle3==================")
                return GPTGenerator.request_dalle(messages)
            elif model == "gpt-4-vision-preview":
                print("gpt4v==================")
                return GPTGenerator.request_vision(messages)
            elif model == "llama2-7b":
                print("llama2================")
                if not self.config["llama2"]["use"]:
                    return "LLama2 Not Supported, Needs to Setting Config config[llama2][use] true"
                return LLama2Generator.generate_llama2_text(self.model, self.tokenizer, messages)
            elif model == "llama2-7b-chat":
                print("llama2================")
                if not self.config["llama2"]["use"]:
                    return "LLama2 Not Supported, Needs to Setting Config config[llama2][use] true"
                return LLama2Generator.generate_llama2_chat(self.model, self.tokenizer, messages)
            elif model.startswith("qianfan_"):
                print(f"qianfan_{model}================")
                return QianfanGenerator.request_qianfan(model, messages, stream)
            elif model == "gpt-assistant-ai-teacher":
                print("assistant=================")
                return AssistantGenerator.request_assitant(model, messages, session_id)
            else:
                print("gpt===============")
                return GPTGenerator.request_gpt(model, messages, stream)

        except Exception as e:
            print(e)
            print(e.__traceback__.tb_next)
            msg = {
                '_action': '_ask',
                'success': False,
                "error": f"an error occurred {str(e)}"
            }
            return msg, 500001

    def _uploads(self):
        """
        uploads
        """
        try:
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

            return {'code': 100000, 'msg': 'upload success',
                    'data': {'bb_path': str(bb_urls), 'path': str(file_urls)}}, 200
        except Exception as e:
            print(e)
            print(e.__traceback__.tb_next)
            msg = {
                '_action': '_ask',
                'success': False,
                "error": f"an error occurred {str(e)}"
            }
            return msg, 500004
