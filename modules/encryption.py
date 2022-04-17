from cryptography.fernet import Fernet
import keyring
from dotenv import load_dotenv
from dev_switch import dev_switch

load_dotenv()
generated_key = str(Fernet.generate_key())[2:-1]

# ENCRYPTING FROM https://devqa.io/encrypt-decrypt-data-python/


def load_key():
    """
    Load the previously generated key
    """
    if dev_switch:
        # use generated fake key
        key = 'lKgtB0ZlND2CSbeZUS5ACfP10JKuXkYyVWnXajI8lx0='
    else:
        key = keyring.get_password("system", "username")
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
    # m = decrypt_message(b"gAAAAABhGgq6EOcbszKzW7KuYq8-Ns8mZGEnqj051zWeR4-wUT5Clq51JD-2sZ-EDDKEVdZ3QuHCjtjVKGkmBA3CPcfpG0Mszg==")
    # print(m)
    # m = encrypt_message("TEST")
    # print(m)
    pass