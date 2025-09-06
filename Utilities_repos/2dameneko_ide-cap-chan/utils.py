import torch
import time
from PIL import Image

GPU_TEST_ITERATIONS = 100
GPU_TEST_SIZE = 1024

def measure_gpu_speed(device):
    """
    Measure the speed of a GPU by performing matrix operations.
    
    Args:
        device: The CUDA device to measure
        
    Returns:
        float: A score representing the relative speed of the GPU
    """
    torch.cuda.set_device(device)
    A = torch.randn(GPU_TEST_SIZE, GPU_TEST_SIZE, device=device)
    B = torch.randn(GPU_TEST_SIZE, GPU_TEST_SIZE, device=device)
    
    start_time = time.time()
    for _ in range(GPU_TEST_ITERATIONS):
        C = torch.matmul(A, B)
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    speed_score = GPU_TEST_ITERATIONS / elapsed_time
    return speed_score

def resize_image_proportionally(image, max_width, max_height):
    """
    Resize an image proportionally to fit within the specified dimensions.
    
    Args:
        image: PIL Image to resize
        max_width: Maximum width
        max_height: Maximum height
        
    Returns:
        PIL Image: Resized image
    """
    width, height = image.size
    aspect_ratio = width / height
    
    if width > max_width or height > max_height:
        if width / max_width > height / max_height:
            new_width = max_width
            new_height = int(max_width / aspect_ratio)
        else:
            new_height = max_height
            new_width = int(max_height * aspect_ratio)
        image = image.resize((new_width, new_height), Image.ANTIALIAS)
    
    return image