import os
import time
import openai
import io
from flask import send_file


class TTSGenerator:

    @staticmethod
    def generate_tts(text, voice, r_format):
        """
        generate tts by openai
        """
        time1 = time.time()
        response = openai.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text.strip(),
            response_format=r_format,
        )

        # Convert the binary response content to a byte stream
        byte_stream = io.BytesIO(response.content)
        byte_stream.name = 'audio.' + r_format
        time2 = time.time()
        cost = time2 - time1
        character_num = len(text)
        info = {
            "cost": cost,
            "c_nums": character_num,
        }
        print(info)
        mimetype = "audio/" + r_format
        return send_file(byte_stream, mimetype=mimetype)
