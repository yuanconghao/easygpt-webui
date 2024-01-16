from flask import render_template, redirect, url_for, request, session, send_from_directory
from flask_babel import refresh
from time import time
from os import urandom
from server.babel import get_locale, get_languages


class Website:
    def __init__(self, bp, app, url_prefix) -> None:
        self.bp = bp
        self.app = app
        self.url_prefix = url_prefix
        self.routes = {
            '/': {
                'function': lambda: redirect(url_for('._index')),
                'methods': ['GET', 'POST']
            },
            '/chat/': {
                'function': self._index,
                'methods': ['GET', 'POST']
            },
            '/chat/<conversation_id>': {
                'function': self._chat,
                'methods': ['GET', 'POST']
            },
            '/prompt/': {
                'function': self._prompt,
                'methods': ['GET', 'POST']
            },
            '/tts/': {
                'function': self._tts,
                'methods': ['GET', 'POST']
            },
            '/asr/': {
                'function': self._asr,
                'methods': ['GET', 'POST']
            },
            '/teacher/': {
                'function': self._teacher,
                'methods': ['GET', 'POST']
            },
            '/corpus/': {
                'function': self._corpus,
                'methods': ['GET', 'POST']
            },
            '/convert/': {
                'function': self._convert,
                'methods': ['GET', 'POST']
            },
            '/change-language': {
                'function': self.change_language,
                'methods': ['POST']
            },
            '/get-locale': {
                'function': self.get_locale,
                'methods': ['GET']
            },
            '/get-languages': {
                'function': self.get_languages,
                'methods': ['GET']
            },
            '/uploads/<filename>': {
                'function': self._uploaded_file,
                'methods': ['GET']
            },
        }

    def _uploaded_file(self, filename):
        return send_from_directory(self.app.static_folder, filename)

    def _chat(self, conversation_id):
        if '-' not in conversation_id:
            return redirect(url_for('._index'))

        return render_template('index.html', chat_id=conversation_id, url_prefix=self.url_prefix)

    def _index(self):
        return render_template('index.html', chat_id=f'{urandom(4).hex()}-{urandom(2).hex()}-{urandom(2).hex()}-{urandom(2).hex()}-{hex(int(time() * 1000))[2:]}', url_prefix=self.url_prefix)

    def _prompt(self):
        print("prompt=========")
        return render_template('prompt1.html', url_prefix=self.url_prefix)

    def _tts(self):
        print("tts=========")
        return render_template('tts.html', url_prefix=self.url_prefix)

    def _asr(self):
        print("asr=========")
        return render_template('asr.html', url_prefix=self.url_prefix)

    def _teacher(self):
        print("teacher=========")
        return render_template('teacher.html', url_prefix=self.url_prefix)

    def _corpus(self):
        print("corpus=========")
        return render_template('corpus.html', url_prefix=self.url_prefix)

    def _convert(self):
        print("convert=========")
        return render_template('convert.html', url_prefix=self.url_prefix)

    def change_language(self):
        data = request.get_json()
        session['language'] = data.get('language')
        refresh()
        return '', 204

    def get_locale(self):
        return get_locale()
    
    def get_languages(self):  
        return get_languages()

