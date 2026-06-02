"""Logger module for application logging."""

import logging
import sys
from pathlib import Path

logger = logging.getLogger("JarvisAgent")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"))
    logger.addHandler(handler)

def get_logger(name: str = "JarvisAgent") -> logging.Logger:
    return logging.getLogger(name)