"""
OS Resource Management Simulator - Global Configuration & Logging
Phase 1 & Phase 4 Compliance: Modular architecture & Activity Logging
"""

import os
import sys
import logging
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
CHARTS_DIR = OUTPUT_DIR / "charts"
TRACES_DIR = OUTPUT_DIR / "traces"
LOGS_DIR = BASE_DIR / "logs"
DOCS_DIR = BASE_DIR / "docs"

# Ensure output directories exist
for path in [DATA_DIR, OUTPUT_DIR, CHARTS_DIR, TRACES_DIR, LOGS_DIR, DOCS_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Logger Setup
LOG_FILE = LOGS_DIR / "os_simulator.log"

def setup_logger(name: str = "OS_Simulator", level: int = logging.INFO) -> logging.Logger:
    """
    Configures and returns a structured logger with both file and console handlers.
    Records timestamp, log level, module name, and message for auditability.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers if setup_logger is called repeatedly
    if not logger.handlers:
        file_handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)-8s] [%(name)s:%(funcName)s:%(lineno)d]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(
            fmt='%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
    return logger

logger = setup_logger()
