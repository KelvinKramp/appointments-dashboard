import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime as dt
from modules.encryption import *
import json
import sys
from definitions import ROOT_DIR

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
msg['From'] = "Keuringsarts"
msg['To'] = toaddr
msg['Subject'] = "Opmerkingen van het spreekuur "+str(dt.now().day)+"-"+str(dt.now().month)
date = str(dt.now().month)+"-"+str(dt.now().day)+"-"+str(dt.now().year)
filename = "Opmerkingen-"+date+".xlsx"
developer = "dr.kramp.rijbewijskeuringen@gmail.com"

def send_email(text, attachment_file):
    body = "Automatisch gegenereerd bericht met opmerkingen van spreekuur op " + date + "\n"+"\n"+"Dit zijn de notities: "+"\n"+text
    msg.attach(MIMEText(body, 'plain'))
    attachment = open(attachment_file, "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(part)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, password)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
    print("EMAIL SENT")

def send_email_developer(text, attachment_file):
    body = "Automatisch gegenereerd bericht met opmerkingen van spreekuur op " + date + "\n"+"\n"+"Dit zijn de notities: "+"\n"+text
    msg.attach(MIMEText(body, 'plain'))
    attachment = open(attachment_file, "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(part)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, password)
    text = msg.as_string()
    server.sendmail(fromaddr, developer, text)
    server.quit()
    print("EMAIL SENT")

if __name__ == '__main__':
    send_email()
