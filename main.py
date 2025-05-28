# main.py
import sys
import logging
from PyQt5.QtWidgets import QApplication
from app.ui import MediaControllerUI
from app import initialize_logging, __appname__, __version__
from app.config import LOGGING_LEVEL

def configure_logging():
    """Configure logging with file and console output"""
    # Set up file handler
    file_handler = logging.FileHandler("app.log")
    # Set up console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Add handlers to the root logger
    logging.getLogger().addHandler(file_handler)
    logging.getLogger().addHandler(console_handler)

def main():
    # Initialize logging with the level from config
    initialize_logging(LOGGING_LEVEL)
    # Add file and console handlers
    configure_logging()
    
    logging.info(f"Starting {__appname__} v{__version__}")

    app = QApplication(sys.argv)
    window = MediaControllerUI()
    window.show()
    exit_code = app.exec_()

    logging.info(f"Application exited with code {exit_code}")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
