from definitions import ROOT_DIR, empty_byte_string
import json
import os

def create_empty_secrets_json_file():
    data = {
            "username_1": empty_byte_string,
            "password_1": empty_byte_string,
            "username_WP": empty_byte_string,
            "password_WP": empty_byte_string,
            "email_email_comments": empty_byte_string,
            "password_email_comments": empty_byte_string,
            "email_receive_comments": empty_byte_string}
    with open(os.path.join(ROOT_DIR,"config", "secrets.json"), 'w') as f:
        json.dump(data, f)

create_empty_secrets_json_file()