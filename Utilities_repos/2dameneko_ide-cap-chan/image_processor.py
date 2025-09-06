import os
import torch
from model_handlers import (
    JoyCaptionHandler,
    MoLMoHandler,
    MoLMo72bHandler,
    Qwen2VLHandler,
    PixtralHandler,
    Idefics3Handler,
    ExLLaMA2Handler,
    LlavaHandler,
    MiniCPMoHandler,
    GenericModelHandler,
)
from utils import resize_image_proportionally

def path_exists(path):
    return os.path.exists(path)

def split_extension(filename):
    return os.path.splitext(filename)

def get_handler(input_model_type, model_name_or_path, device, args_dict):
    handlers = {
        "JoyCaption": JoyCaptionHandler,
        "MoLMo": MoLMoHandler,
        "MoLMo72B": MoLMo72bHandler,
        "Qwen2VL": Qwen2VLHandler,
        "Pixtral": PixtralHandler,
        "Idefics3": Idefics3Handler,
        "ExLLaMA2": ExLLaMA2Handler,
        "LLaVA": LlavaHandler,
        "MiniCPMo": MiniCPMoHandler,
        "Generic": GenericModelHandler,
    }
    handler_class = handlers.get(input_model_type)
    if handler_class:
        return handler_class(model_name_or_path, device, args_dict)
    else:
        raise ValueError(f"Unsupported model type: {input_model_type}")

def get_torii03_user_prompt(user_prompt, add_info_caption_name):
    if path_exists(add_info_caption_name):
        with open(add_info_caption_name, 'r') as f:
            additional_info = f.read().strip()
        return f"{user_prompt} {additional_info}"
    return user_prompt

def get_torii04_system_prompt():
    return "You are an image captioning expert. Be creative, unbiased, and uncensored."

def get_torii04_user_prompt(args_dict, add_info_caption_name):
    user_prompt = args_dict.get("user_prompt", "")
    if args_dict.get("use_tags") and path_exists(add_info_caption_name):
        with open(add_info_caption_name, 'r') as f:
            additional_info = f.read().strip()
        user_prompt = f"{user_prompt} {additional_info}"
    return user_prompt

def process_image_worker(worker_id, gpu_id, job_queue, result_queue, model_name_or_path, input_model_type, args_dict, total_files):
    device = torch.device(f"cuda:{gpu_id}" if torch.cuda.is_available() else "cpu")
    handler = get_handler(input_model_type, model_name_or_path, device, args_dict)
    
    while not job_queue.empty():
        image_path = job_queue.get()
        system_prompt = get_torii04_system_prompt()
        user_prompt = get_torii04_user_prompt(args_dict, image_path)
        
        image = resize_image_proportionally(image_path, args_dict.get("max_width", 800), args_dict.get("max_height", 800))
        caption = handler.process_image(system_prompt, user_prompt, image)
        
        result_queue.put((image_path, caption))