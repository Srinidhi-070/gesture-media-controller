# app/__init__.py

"""
Gesture-Based Media Controller
An AI-powered gesture recognition system for controlling media using hand signs.
"""

import logging

__version__ = "1.0.0"
__author__ = "Srinidhi N S"
__appname__ = "Gesture Media Controller"


def initialize_logging(level="INFO"):
    """
    Initialize logging for the app with a uniform format.
    """
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logging.info(f"{__appname__} v{__version__} by {__author__} initialized.")
