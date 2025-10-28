# backend/utils/logger.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(log_dir: str = "data/logs"):
    os.makedirs(log_dir, exist_ok=True)
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    handler = RotatingFileHandler(os.path.join(log_dir, "backend.log"), maxBytes=5*1024*1024, backupCount=3)
    handler.setFormatter(logging.Formatter(fmt))
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    # also print to console
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter(fmt))
    root.addHandler(ch)

def get_logger(name: str):
    return logging.getLogger(name)
