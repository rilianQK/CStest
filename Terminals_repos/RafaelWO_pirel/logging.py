# proj_clean/pirel/logging.py

import logging

def setup_logging(verbosity):
    """Sets up the basic logging configuration.

    Args:
        verbosity (int): Configures the log level which defaults to WARNING.
            A `verbosity` of `0` maps to WARNING, `1` -> INFO, and `2` (or more)
            -> DEBUG. Defaults to `0`.
    """
    level = logging.WARNING
    if verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG

    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')