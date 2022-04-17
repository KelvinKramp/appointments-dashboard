import os
from modules.encryption import encrypt_message
"""
PROJECT DEFINITIONS
"""

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) + "/"
empty_byte_string = str(encrypt_message("").decode("utf-8"))
