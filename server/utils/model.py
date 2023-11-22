from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import torch
from peft import PeftModel


class ModelUtils(object):

    @classmethod
    def load_model(cls, model_name_or_path, load_in_4bit=False, adapter_name_or_path=None):
        # 是否使用4bit量化进行推理
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            # bnb_4bit_use_double_quant=True,
            # llm_int8_threshold=6.0,
            # llm_int8_has_fp16_weight=False,
        )
        if load_in_4bit:
            pass
        else:
            quantization_config = None

        # 加载base model
        model = AutoModelForCausalLM.from_pretrained(
            model_name_or_path,
            quantization_config=quantization_config,
            trust_remote_code=True,
            # load_in_4bit=load_in_4bit,
            # low_cpu_mem_usage=True,
            # torch_dtype=torch.float16,
            # device_map='auto',

        )

        # 加载adapter
        if adapter_name_or_path is not None:
            model = PeftModel.from_pretrained(model, adapter_name_or_path)

        return model
