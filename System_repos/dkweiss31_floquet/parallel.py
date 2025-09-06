import multiprocessing as mp
from typing import Callable, Iterable, Any


def parallel_map(func: Callable, parameters: Iterable, num_cpus: int) -> map:
    """Apply a function to each item in an iterable in parallel using multiple CPU cores for improved performance."""
    if num_cpus == 1:
        return map(func, parameters)
    else:
        with mp.Pool(processes=num_cpus) as pool:
            return pool.map(func, parameters)