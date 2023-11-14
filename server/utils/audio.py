from pydub import AudioSegment


def convert_audio_to_wav(file_path):
    audio = AudioSegment.from_file(file_path)
    new_file_path = file_path + ".wav"
    audio.export(new_file_path, format="wav")
    return new_file_path
