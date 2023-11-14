import tempfile
import openai
import os


class ASRGenerator:

    @staticmethod
    def generate_asr(audio_file, lang=""):
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        audio_file.save(temp_file.name)

        print(audio_file)
        print(temp_file.name)

        file_data = open(temp_file.name, "rb")
        # with open(temp_file.name, 'rb') as f:
        #     file_data = f.read()

        if lang:
            response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=file_data,
                language=lang
            )
        else:
            response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=file_data,
            )
        os.unlink(temp_file.name)

        print(response)
        return response.text
