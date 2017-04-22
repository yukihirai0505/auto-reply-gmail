# -*- coding: utf-8 -*-

"""
This is simple email send example

Usage:

in command line

$ export GMAIL_USERNAME=[Your Gmail Account Email Address]
$ export GMAIL_PASSWORD=[Your Gmail Account Password]

"""

import smtplib
from email.mime.text import MIMEText

import os

GMAIL_USERNAME = os.getenv("GMAIL_USERNAME")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

def send_gmail(to, sub, body):
    host, port = 'smtp.gmail.com', 465
    msg = MIMEText(body)
    msg['Subject'] = sub
    msg['From'] = GMAIL_USERNAME
    msg['To'] = to
    smtp = smtplib.SMTP_SSL(host, port)
    smtp.ehlo()
    smtp.login(GMAIL_USERNAME, GMAIL_PASSWORD)
    smtp.mail(GMAIL_USERNAME)
    smtp.rcpt(to)
    smtp.data(msg.as_string())
    smtp.quit()


if __name__ == '__main__':
    to = 'example@example.com'
    sub = 'subject'
    body = 'body1\nbody2'
    send_gmail(to, sub, body)
