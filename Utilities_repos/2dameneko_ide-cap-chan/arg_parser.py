import argparse
import sys

def check_mutually_exclusive(args, arg_names):
    """
    Ensure that only one of the specified arguments in a given set is True, and exit with an error if multiple are True.
    """
    true_args = [arg for arg in arg_names if getattr(args, arg)]
    if len(true_args) > 1:
        sys.stderr.write(f"Error: Arguments {', '.join(true_args)} are mutually exclusive.\n")
        sys.exit(1)

def parse_arguments():
    """
    Parse command-line arguments for configuring image caption generation, including model settings, input/output paths, and optional enhancements like tags and character information.
    """
    parser = argparse.ArgumentParser(description="Image Captioning System")

    # Model selection and path specification
    parser.add_argument('--model', type=str, required=True, help='Model name or path')
    parser.add_argument('--model_type', type=str, required=True, choices=['ExLLaMA2', 'JoyCaption', 'MoLMo', 'MoLMo72B', 'Qwen2VL', 'Pixtral', 'Idefics3', 'LLaVA', 'MiniCPMo', 'Generic'], help='Type of model to use')

    # Input directory for images
    parser.add_argument('--input_dir', type=str, required=True, help='Directory containing input images')

    # GPU device selection (with multi-GPU support)
    parser.add_argument('--gpu', type=int, nargs='+', default=[0], help='GPU device IDs to use')

    # Output file extensions for captions and tags
    parser.add_argument('--caption_ext', type=str, default='.txt', help='File extension for captions')
    parser.add_argument('--tag_ext', type=str, default='.tags', help='File extension for tags')

    # Multiple caption formats (JSON, markdown, short, long, bounding box)
    parser.add_argument('--caption_format', type=str, choices=['json', 'markdown', 'short', 'long', 'bbox'], default='json', help='Format of the generated captions')

    # Enhanced Captioning options
    parser.add_argument('--use_tags', action='store_true', help='Incorporate existing tags from files to improve caption quality')
    parser.add_argument('--character_info', action='store_true', help='Include character information in captions')
    parser.add_argument('--character_traits', action='store_true', help='Include character traits in captions')
    parser.add_argument('--additional_image_info', action='store_true', help='Utilize additional image information')

    # Performance Optimization options
    parser.add_argument('--measure_gpu_speed', action='store_true', help='Automatically measure GPU speed')
    parser.add_argument('--multi_gpu', action='store_true', help='Enable multi-GPU processing with workload distribution')
    parser.add_argument('--memory_management', action='store_true', help='Enable memory management for large models')
    parser.add_argument('--progress_tracking', action='store_true', help='Enable progress tracking with ETA calculation')

    # Image Processing options
    parser.add_argument('--image_formats', type=str, nargs='+', default=['JPG', 'PNG', 'WebP', 'JPEG'], help='Supported image formats')
    parser.add_argument('--resize_images', action='store_true', help='Automatically resize images while maintaining proportions')
    parser.add_argument('--avoid_reprocessing', action='store_true', help='Avoid reprocessing already captioned images')

    # Model-Specific Handling options
    parser.add_argument('--custom_init', action='store_true', help='Custom initialization for each supported model type')
    parser.add_argument('--specialized_pipeline', action='store_true', help='Specialized processing pipelines for different architectures')
    parser.add_argument('--quantization', action='store_true', help='Enable quantization support (4-bit NF4) where applicable')

    args = parser.parse_args()

    # Check mutually exclusive arguments
    check_mutually_exclusive(args, ['measure_gpu_speed', 'multi_gpu'])

    return args

if __name__ == "__main__":
    args = parse_arguments()
    print(args)