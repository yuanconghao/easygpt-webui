import os
import time
import openai
import io
from flask import send_file
from pydub import AudioSegment


class TTSGenerator:

    @staticmethod
    def generate_tts(text, voice, r_format, sample_rate=24000, model="tts-1"):
        """
        generate tts by openai
        """
        time1 = time.time()
        response = openai.audio.speech.create(
            model=model,
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

        if sample_rate == 24000 or r_format == "pcm":
            #openai 默认返回24k
            print("24k output")
            return send_file(byte_stream, mimetype=mimetype)

        # Use pydub to read the audio data and convert the sample rate to 16kHz
        audio = AudioSegment.from_file(byte_stream)
        audio_16k = audio.set_frame_rate(sample_rate)

        # Export the converted audio to a new byte stream
        output_stream = io.BytesIO()
        audio_16k.export(output_stream, format=r_format)
        output_stream.seek(0)  # Reset the stream position to the beginning
        print("16k output")
        return send_file(output_stream, mimetype=mimetype)


