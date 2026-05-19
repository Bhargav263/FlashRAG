import os
import logging
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

os.makedirs("logs", exist_ok=True)

def get_logger(name):

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formate = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler("logs/agent.log")
    file_handler.setFormatter(formate)

    consle_handler = logging.StreamHandler()
    consle_handler.setFormatter(formate)

    if not logger.hasHandlers():

        logger.addHandler(file_handler)
        logger.addHandler(consle_handler)
    
    return logger