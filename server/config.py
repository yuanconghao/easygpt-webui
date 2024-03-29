import os
models = {
    'gpt-3.5-turbo',
    'gpt-3.5-turbo-16k-0613',
    'gpt-3.5-turbo-16k',
    'gpt-4',
}

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(ROOT_DIR, "uploads")
OUTPUTS_DIR = os.path.join(ROOT_DIR, "outputs")
CORPUS_DIR = os.path.join(ROOT_DIR, "outputs/corpus")
CORPUS_UPLOAD_DIR = os.path.join(ROOT_DIR, "uploads/corpus")
CORPUS_CONVERT_DIR = os.path.join(ROOT_DIR, "outputs/convert")
