import smtplib
from credentials.creds import EMAIL_SMTP_SERVER, EMAIL_SENDER, EMAIL_PASSWORD

smtp_server = EMAIL_SMTP_SERVER
sender = EMAIL_SENDER
password = EMAIL_PASSWORD


def send_mail(receiver, subject, message, sender=sender):
    email = """\
From: {}\r
To: {}\r
Subject: {}\r
\r
{}\r""".format(sender, receiver, subject, message)

    with smtplib.SMTP(smtp_server) as server:
        server.login(sender, password)
        server.sendmail(sender, [receiver], email)

# send_mail("example@mail.com", "Test_subject", "Test messsage is sent from Python")