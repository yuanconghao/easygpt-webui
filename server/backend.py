import os
import json
import openai
from datetime import datetime
from flask import request, url_for
from werkzeug.utils import secure_filename
from flask import Flask, jsonify
from server.utils.imgbb import upload_bb
from server.models.prompter import Prompter
from server.models.asr import ASRGenerator
from server.models.tts import TTSGenerator
from server.models.gpt import GPTGenerator
from server.models.llama2 import LLama2Generator
from server.models.assistant import AssistantGenerator
from server.models.qianfan import QianfanGenerator
from server.models.corpus import CorpusGenerator
from server.models.txdh import TXDHGenerator

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
        self.ws = None

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
            '/backend-api/v2/uploads_corpus': {
                'function': self._uploads_corpus,
                'methods': ['POST']
            },
            '/backend-api/v2/convert_corpus': {
                'function': self._convert_corpus,
                'methods': ['POST']
            },
            '/backend-api/v2/user_info_bind': {
                'function': self._user_info_bind,
                'methods': ['POST']
            },
            '/backend-api/v2/geshui_calc': {
                'function': self._geshui_calc,
                'methods': ['POST']
            },
            '/backend-api/v2/create_session': {
                'function': self._dh_create_session,
                'methods': ['POST']
            },
            '/backend-api/v2/list_session': {
                'function': self._dh_list_session,
                'methods': ['POST']
            },
            '/backend-api/v2/detail_session': {
                'function': self._dh_detail_session,
                'methods': ['POST']
            },
            '/backend-api/v2/start_session': {
                'function': self._dh_start_session,
                'methods': ['POST']
            },
            '/backend-api/v2/close_session': {
                'function': self._dh_close_session,
                'methods': ['POST']
            },
            '/backend-api/v2/create_ws': {
                'function': self._dh_create_ws,
                'methods': ['POST']
            },
            '/backend-api/v2/dh_send_text': {
                'function': self._dh_send_text,
                'methods': ['POST']
            },
            '/backend-api/v2/dh_send_audio': {
                'function': self._dh_send_audio,
                'methods': ['POST']
            }
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
            r_format = request.json['r_format']
            sample_rate = int(request.json['sample_rate'])
            model = request.json['model']
            return TTSGenerator.generate_tts(text, voice, r_format, sample_rate, model)
        except Exception as e:
            print(e)
            print(e.__traceback__.tb_next)
            msg = {
                '_action': '_ask',
                'success': False,
                "error": f"an error occurred {str(e)}"
            }
            return msg, 500002

    def _dh_create_session(self):
        """
        create session
        """
        try:
            print("create_session===================")
            print(request.json)
            appkey = request.json['appkey']
            access_token = request.json['access_token']
            virtualmankey = request.json['virtualmankey']

            return TXDHGenerator.create_session(appkey, access_token, virtualmankey)
        except Exception as e:
            print(e)
            print(e.__traceback__.tb_next)
            msg = {
                '_action': '_ask',
                'success': False,
                "error": f"an error occurred {str(e)}"
            }
            return msg, 500002

    def _dh_list_session(self):
        """
        create session
        """
        try:
            print("create_session===================")
            print(request.json)
            appkey = request.json['appkey']
            access_token = request.json['access_token']
            virtualmankey = request.json['virtualmankey']

            return TXDHGenerator.list_session(appkey, access_token, virtualmankey)
        except Exception as e:
            print(e)
            print(e.__traceback__.tb_next)
            msg = {
                '_action': '_ask',
                'success': False,
                "error": f"an error occurred {str(e)}"
            }
            return msg, 500002

    def _dh_detail_session(self):
        """
        detail session
        """
        try:
            print("detail_session===================")
            print(request.json)
            appkey = request.json['appkey']
            access_token = request.json['access_token']
            virtualmankey = request.json['virtualmankey']
            sessionid = request.json['sessionid']

            return TXDHGenerator.detail_session(appkey, access_token, sessionid)
        except Exception as e:
            print(e)
            print(e.__traceback__.tb_next)
            msg = {
                '_action': '_ask',
                'success': False,
                "error": f"an error occurred {str(e)}"
            }
            return msg, 500002

    def _dh_start_session(self):
        """
        start session
        """
        try:
            print("start_session===================")
            print(request.json)
            appkey = request.json['appkey']
            access_token = request.json['access_token']
            virtualmankey = request.json['virtualmankey']
            sessionid = request.json['sessionid']

            return TXDHGenerator.start_session(appkey, access_token, sessionid)
        except Exception as e:
            print(e)
            print(e.__traceback__.tb_next)
            msg = {
                '_action': '_ask',
                'success': False,
                "error": f"an error occurred {str(e)}"
            }
            return msg, 500002

    def _dh_close_session(self):
        """
        close session
        """
        try:
            print("close_session===================")
            print(request.json)
            appkey = request.json['appkey']
            access_token = request.json['access_token']
            virtualmankey = request.json['virtualmankey']
            sessionid = request.json['sessionid']

            return TXDHGenerator.close_session(appkey, access_token, sessionid)
        except Exception as e:
            print(e)
            print(e.__traceback__.tb_next)
            msg = {
                '_action': '_ask',
                'success': False,
                "error": f"an error occurred {str(e)}"
            }
            return msg, 500002

    def _dh_create_ws(self):
        """
        create session
        """
        try:
            print("create_ws===================")
            print(request.json)
            appkey = request.json['appkey']
            access_token = request.json['access_token']
            virtualmankey = request.json['virtualmankey']
            sessionid = request.json['sessionid']

            ws = TXDHGenerator.create_ws(appkey, access_token, virtualmankey, sessionid)
            self.ws = ws
            print(ws)
            return jsonify({"msg": "ws connected"})
        except Exception as e:
            print(e)
            print(e.__traceback__.tb_next)
            msg = {
                '_action': '_ask',
                'success': False,
                "error": f"an error occurred {str(e)}"
            }
            return msg, 500002

    def _dh_send_text(self):
        """
        create session
        """
        try:
            print("send_text===================")
            print(request.json)
            appkey = request.json['appkey']
            access_token = request.json['access_token']
            virtualmankey = request.json['virtualmankey']
            sessionid = request.json['sessionid']
            text = request.json['text']

            TXDHGenerator.send_text(appkey, access_token, sessionid, text)

            return jsonify({"text": text})
        except Exception as e:
            print(e)
            print(e.__traceback__.tb_next)
            msg = {
                '_action': '_ask',
                'success': False,
                "error": f"an error occurred {str(e)}"
            }
            return msg, 500002

    def _dh_send_audio(self):
        """
        create session
        """
        try:
            print("send_audio===================")
            print(request.json)
            appkey = request.json['appkey']
            access_token = request.json['access_token']
            virtualmankey = request.json['virtualmankey']
            sessionid = request.json['sessionid']
            voice = request.json['tts_voice']
            model = request.json['tts_model']
            text = request.json['text']

            TXDHGenerator.send_audio(appkey, access_token, sessionid, text, voice, model)

            return jsonify({"text": text})
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
                "role_name": role_name,
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
                "corpus_nums": int(corpus_nums),
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

    def _convert_corpus(self):
        """
        convert corpus
        """
        try:
            print("convert corpus===================")
            print(request.json)
            datatype = request.json['datatype']
            corpus_path = request.json['corpus_path']
            print(datatype)
            print(corpus_path)

            return CorpusGenerator.convert_corpus(datatype, corpus_path)
        except Exception as e:
            print(e)
            print(e.__traceback__.tb_next)
            msg = {
                '_action': '_ask',
                'success': False,
                "error": f"an error occurred {str(e)}"
            }
            print(msg)
            return {'code': 100001, 'msg': 'convert error'}, 500001

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
            print(conversation)
            print(prompt)
            print(images)
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
            elif model.startswith("o1-"):
                print("gpt o===============")
                return GPTGenerator.request_o(model, messages, stream)
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

    def _uploads_corpus(self):
        """
        uploads corpus
        """
        try:
            print("uploads corpus===============")
            file_path = os.path.join(self.app.static_folder, 'corpus')
            print(file_path)
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            print(request.files)

            file = request.files['up_file']
            print(file)

            # ext = os.path.splitext(file.filename)[1]
            # new_filename = datetime.now().strftime("%Y%m%d%H%M%S%f") + ('-%d') + ext
            new_filename = secure_filename(file.filename)
            new_file_path = os.path.join(file_path, new_filename)
            file.save(new_file_path)

            url_name = "corpus/" + new_filename
            file_url = url_for('static', filename=url_name)

            return {'code': 100000, 'msg': 'upload success',
                    'data': {'path': str(file_url)}}, 200
        except Exception as e:
            print(e)
            print(e.__traceback__.tb_next)
            msg = {
                '_action': '_ask',
                'success': False,
                "error": f"an error occurred {str(e)}"
            }
            return msg, 500004

    def _user_info_bind(self):
        phone = request.json['phone']
        return {
            "url": "https://kcs.51talk.com/easygpt/uploads/51_test.jpg",
            "message": "感谢您的确认。已经为您安排了课程顾问，会第一时间联系您。您也可以扫描下面的二维码添加课程顾问。课程顾问会为您提供详细的课程介绍和咨询服务。"
        }


    def _geshui_calc(self):
        income = float(request.json['income'])
        zhuanxiang = int(request.json['zhuanxiang'])

        yijin = income * 0.12
        wuxian = income * 0.1

        rate = [0.03, 0.1, 0.2, 0.25, 0.3, 0.35, 0.45]
        base = [0, 36000, 144000, 300000, 420000, 660000, 960000]
        temp_total = []
        susuan = []

        for i in range(0, 6, 1):
            temp_total.append((base[i + 1] - base[i]) * rate[i])

        for i in range(1, 7, 1):
            sub_total = 0
            for j in range(i, 0, -1):
                sub_total = sub_total + temp_total[j - 1]
            susuan.append(base[i] * rate[i] - sub_total)

        income = income - wuxian - yijin - zhuanxiang - 5000

        # print("%.2f" % income)
        pre_tax = 0
        for k in range(1, 13, 1):
            income = (18000 - wuxian - yijin - zhuanxiang - 5000) * k
            #	print("第 %d 月应纳税额：%.2f" % (k, income))

            for i in range(len(base)):
                if income > base[i]:
                    continue
                else:
                    if i < 2:
                        tax = income * 0.03 - pre_tax
                        pre_tax = income * 0.03
                        # print("tax: %.2f" % tax)
                    else:
                        tax = income * rate[i - 1] - susuan[i - 2] - pre_tax
                        pre_tax = pre_tax + tax
                        # print("tax: %.2f" % tax)
                    #			print("%d, %d, %d" % (i, base[i], susuan[i-2]))
                    break

        # print("total tax : %.2f" % pre_tax)
        return {
            'total_tax': pre_tax
        }


