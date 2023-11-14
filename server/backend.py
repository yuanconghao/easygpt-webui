import os
import json
import openai
from datetime import datetime
from flask import request, url_for
from werkzeug.utils import secure_filename
from server.utils.imgbb import upload_bb
from server.models.asr import generate_asr
from server.models.tts import generate_tts
from server.models.gpt import request_gpt, request_dalle, request_vision, build_messages

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

    def _generate_asr(self):
        """
        generate asr
        """
        try:
            print("asr===================")
            print(request.args)
            lang = request.args.get('lang')
            audio_file = request.files['audio']
            return generate_asr(audio_file, lang)
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
            return generate_tts(text, voice)
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
            conversation = request.json['meta']['content']['conversation']
            prompt = request.json['meta']['content']['parts'][0]
            send_images = request.json["send_images"]
            images = []
            if send_images:
                send_images = send_images.replace("'", "\"")
                images = json.loads(send_images)

            messages = build_messages(model, conversation, prompt, images)
            print("messages==================")
            print(messages)

            stream = request.json["meta"]["content"]["internet_access"]
            # Generate response

            if model == "dall-e-3":
                print("delle3==================")
                return request_dalle(messages)
            elif model == "gpt-4-vision-preview":
                print("gpt4v==================")
                return request_vision(messages)
            else:
                print("gpt===============")
                return request_gpt(model, messages, stream)

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

            return {'code': 100000, 'msg': 'upload success', 'data': {'bb_path': str(bb_urls), 'path': str(file_urls)}}, 200
        except Exception as e:
            print(e)
            print(e.__traceback__.tb_next)
            msg = {
                '_action': '_ask',
                'success': False,
                "error": f"an error occurred {str(e)}"
            }
            return msg, 500004
