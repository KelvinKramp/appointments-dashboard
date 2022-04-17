import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from config.email import *


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
