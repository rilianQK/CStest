import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

class ModelHandler:
    def __init__(self, model_name_or_path, device, args_dict):
        self.model_name_or_path = model_name_or_path
        self.device = device
        self.args_dict = args_dict
        self.model = None
        self.processor = None
        self.tokenizer = None
        self.quantization_config = self._get_quantization_config()
        self._initialize_model()

    def _get_quantization_config(self):
        if self.args_dict.get("quantization"):
            return BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.float16
            )
        return None

    def _initialize_model(self):
        raise NotImplementedError("Subclasses should implement this method")

    def model_loader(self, model_name_or_path):
        return model_name_or_path

    def process_image(self, system_prompt, user_prompt, image):
        raise NotImplementedError("Subclasses should implement this method")

    def save_caption(self, caption, caption_path, encoding="utf-8", errors="ignore"):
        with open(caption_path, 'w', encoding=encoding, errors=errors) as f:
            f.write(caption)

class JoyCaptionHandler(ModelHandler):
    def __init__(self, model_name_or_path, device, args_dict):
        super().__init__(model_name_or_path, device, args_dict)

    def _initialize_model(self):
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name_or_path, quantization_config=self.quantization_config).to(self.device)
        self.processor = AutoTokenizer.from_pretrained(self.model_name_or_path)

    def process_image(self, system_prompt, user_prompt, image):
        inputs = self.processor(system_prompt + user_prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(**inputs)
        return self.processor.decode(outputs[0], skip_special_tokens=True)

class MoLMoHandler(ModelHandler):
    def __init__(self, model_name_or_path, device, args_dict):
        super().__init__(model_name_or_path, device, args_dict)

    def _initialize_model(self):
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name_or_path).to(self.device)
        self.processor = AutoTokenizer.from_pretrained(self.model_name_or_path)

    def process_image(self, system_prompt, user_prompt, image):
        inputs = self.processor(system_prompt + user_prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(**inputs)
        return self.processor.decode(outputs[0], skip_special_tokens=True)

class MoLMo72bHandler(MoLMoHandler):
    def __init__(self, model_name_or_path, device, args_dict):
        super().__init__(model_name_or_path, device, args_dict)

    def _initialize_model(self):
        super()._initialize_model()
        # Additional initialization for MoLMo72B

class Qwen2VLHandler(ModelHandler):
    def __init__(self, model_name_or_path, device, args_dict):
        super().__init__(model_name_or_path, device, args_dict)

    def _initialize_model(self):
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name_or_path, quantization_config=self.quantization_config).to(self.device)
        self.processor = AutoTokenizer.from_pretrained(self.model_name_or_path)

    def process_image(self, system_prompt, user_prompt, image):
        inputs = self.processor(system_prompt + user_prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(**inputs)
        return self.processor.decode(outputs[0], skip_special_tokens=True)

class PixtralHandler(ModelHandler):
    def __init__(self, model_name_or_path, device, args_dict):
        super().__init__(model_name_or_path, device, args_dict)

    def _get_quantization_config(self):
        return BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.float16
        )

    def _initialize_model(self):
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name_or_path, quantization_config=self.quantization_config).to(self.device)
        self.processor = AutoTokenizer.from_pretrained(self.model_name_or_path)

    def process_image(self, system_prompt, user_prompt, image):
        inputs = self.processor(system_prompt + user_prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(**inputs)
        return self.processor.decode(outputs[0], skip_special_tokens=True)

class Idefics3Handler(ModelHandler):
    def __init__(self, model_name_or_path, device, args_dict):
        super().__init__(model_name_or_path, device, args_dict)

    def _initialize_model(self):
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name_or_path).to(self.device)
        self.processor = AutoTokenizer.from_pretrained(self.model_name_or_path)

    def process_image(self, system_prompt, user_prompt, image):
        inputs = self.processor(system_prompt + user_prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(**inputs)
        return self.processor.decode(outputs[0], skip_special_tokens=True)

class ExLLaMA2Handler(ModelHandler):
    def __init__(self, model_name_or_path, device, args_dict):
        super().__init__(model_name_or_path, device, args_dict)

    def _initialize_model(self):
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name_or_path, quantization_config=self.quantization_config).to(self.device)
        self.processor = AutoTokenizer.from_pretrained(self.model_name_or_path)

    def process_image(self, system_prompt, user_prompt, image):
        inputs = self.processor(system_prompt + user_prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(**inputs)
        return self.processor.decode(outputs[0], skip_special_tokens=True)

class LlavaHandler(ModelHandler):
    def __init__(self, model_name_or_path, device, args_dict):
        super().__init__(model_name_or_path, device, args_dict)

    def _initialize_model(self):
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name_or_path).to(self.device)
        self.processor = AutoTokenizer.from_pretrained(self.model_name_or_path)

    def process_image(self, system_prompt, user_prompt, image):
        inputs = self.processor(system_prompt + user_prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(**inputs)
        return self.processor.decode(outputs[0], skip_special_tokens=True)

class MiniCPMoHandler(ModelHandler):
    def __init__(self, model_name_or_path, device, args_dict):
        super().__init__(model_name_or_path, device, args_dict)

    def _initialize_model(self):
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name_or_path, quantization_config=self.quantization_config).to(self.device)
        self.processor = AutoTokenizer.from_pretrained(self.model_name_or_path)

    def process_image(self, system_prompt, user_prompt, image):
        inputs = self.processor(system_prompt + user_prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(**inputs)
        return self.processor.decode(outputs[0], skip_special_tokens=True)

class GenericModelHandler(ModelHandler):
    def __init__(self, model_name_or_path, device, args_dict):
        super().__init__(model_name_or_path, device, args_dict)

    def _initialize_model(self):
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name_or_path, quantization_config=self.quantization_config).to(self.device)
        self.processor = AutoTokenizer.from_pretrained(self.model_name_or_path)

    def process_image(self, system_prompt, user_prompt, image):
        inputs = self.processor(system_prompt + user_prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(**inputs)
        return self.processor.decode(outputs[0], skip_special_tokens=True)