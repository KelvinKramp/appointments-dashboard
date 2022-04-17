import re
from cryptography.fernet import Fernet
import keyring
import os
import json
from dotenv import load_dotenv

load_dotenv()

# DEFINE FUNCTIONS FOR ENCRYPTING FROM https://devqa.io/encrypt-decrypt-data-python/
def load_key():
    """
    Load the previously generated key
    """
    key = os.environ.get("PASSWORD")
    return key

def encrypt_message(message):
    """
    Encrypts a message
    """
    key = load_key()
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)

    return encrypted_message

def decrypt_message(encrypted_message):
    """
    Decrypts an encrypted message
    """
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)

    return decrypted_message.decode()

if __name__ == "__main__":
    pass