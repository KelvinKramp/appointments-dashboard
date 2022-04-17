from datetime import datetime as dt
from modules.encryption import *
import json
import sys
from definitions import ROOT_DIR
from email.mime.multipart import MIMEMultipart

# DEFINE PATH
if getattr(sys, 'frozen', False):
    path_dir = str(os.path.dirname(sys.executable))
else:
    path_dir = os.path.join(ROOT_DIR, "config")

# DEFINE VARIABLES
secrets = path_dir+'/secrets.json'
with open(secrets) as f:
    secret = json.load(f)

fromaddr = decrypt_message(secret["email_email_comments"].encode('utf-8'))
password = decrypt_message(secret["password_email_comments"].encode('utf-8'))
toaddr = decrypt_message(secret["email_receive_comments"].encode('utf-8'))


msg = MIMEMultipart()
msg['From'] = "Worker"
msg['To'] = toaddr
msg['Subject'] = "Comments on appointments"+str(dt.now().day)+"-"+str(dt.now().month)
date = str(dt.now().month)+"-"+str(dt.now().day)+"-"+str(dt.now().year)
filename = "Comments-"+date+".xlsx"
developer = "emailadrestosendcommentsfrom@email.com"

