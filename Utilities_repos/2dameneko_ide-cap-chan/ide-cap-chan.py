import os
import sys
import torch
import multiprocessing
from queue import Queue
from arg_parser import parse_arguments
from image_processor import process_image_worker
from utils import measure_gpu_speed, resize_image_proportionally

def split_extension(filename):
    """
    Split the filename into the name and extension parts.
    """
    return os.path.splitext(filename)

def main():
    args = parse_arguments()

    # Validate input directory
    if not os.path.isdir(args.input_dir):
        sys.stderr.write(f"Error: Input directory {args.input_dir} does not exist.\n")
        sys.exit(1)

    # Initialize job and result queues
    job_queue = Queue()
    result_queue = Queue()

    # Populate job queue with image files
    for root, _, files in os.walk(args.input_dir):
        for file in files:
            if split_extension(file)[1].lower() in args.image_formats:
                job_queue.put(os.path.join(root, file))

    total_files = job_queue.qsize()
    if total_files == 0:
        sys.stderr.write("Error: No images found in the input directory.\n")
        sys.exit(1)

    # Initialize worker processes
    workers = []
    for i, gpu_id in enumerate(args.gpu):
        worker = multiprocessing.Process(
            target=process_image_worker,
            args=(i, gpu_id, job_queue, result_queue, args.model, args.model_type, vars(args), total_files)
        )
        workers.append(worker)
        worker.start()

    # Collect results
    for _ in range(total_files):
        result = result_queue.get()
        print(result)

    # Wait for all workers to finish
    for worker in workers:
        worker.join()

if __name__ == "__main__":
    main()