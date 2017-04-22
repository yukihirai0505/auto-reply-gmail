import datetime
import email
import re
import time
import os
import base64
from email.header import decode_header
from email.mime.text import MIMEText
from imaplib import ParseFlags


class Message:
    def __init__(self, mailbox, uid):
        self.uid = uid
        self.mailbox = mailbox
        self.gmail = mailbox.gmail if mailbox else None
        self.message = None
        self.headers = {}
        self.subject = None
        self.body = None
        self.html = None
        self.id = None
        self.to = None
        self.fr = None
        self.cc = None
        self.date = None
        self.delivered_to = None
        self.content_transfer_encoding = None
        self.sent_at = None
        self.flags = []
        self.labels = []
        self.thread_id = None
        self.thread = []
        self.message_id = None
        self.attachments = None

    def read(self):
        flag = '\\Seen'
        self.gmail.imap.uid('STORE', self.uid, '+FLAGS', flag)
        if flag not in self.flags: self.flags.append(flag)

    def reply(self, message):
        new = MIMEText(message)
        new["Message-ID"] = email.utils.make_msgid()
        new["In-Reply-To"] = self.message_id
        new["References"] = self.message_id
        new["Subject"] = "Re: " + self.subject
        new["To"] = self.fr
        new["Cc"] = self.cc
        self.gmail.send_mail(new)

    def parse_headers(self, message):
        hdrs = {}
        for hdr in message.keys():
            hdrs[hdr] = message[hdr]
        return hdrs

    def parse_flags(self, headers):
        return list(ParseFlags(headers))

    def parse_labels(self, headers):
        if re.search(r'X-GM-LABELS \(([^\)]+)\)', headers):
            labels = re.search(r'X-GM-LABELS \(([^\)]+)\)', headers).groups(1)[0].split(' ')
            return map(lambda l: l.replace('"', '').decode("string_escape"), labels)
        else:
            return list()

    def parse_subject(self, encoded_subject):
        dh = decode_header(encoded_subject)
        default_charset = 'UTF-8'
        return ''.join([unicode(t[0], t[1] or default_charset) for t in dh])

    def parse(self, raw_message):
        raw_headers = raw_message[0]
        raw_email = raw_message[1]

        self.message = email.message_from_string(raw_email)
        self.headers = self.parse_headers(self.message)
        self.to = self.message['to']
        self.fr = self.message['from']
        self.delivered_to = self.message['delivered_to']
        self.subject = self.parse_subject(self.message['subject'])
        self.date = self.message["Date"]
        self.content_transfer_encoding = self.message["Content-Transfer-Encoding"]

        if self.message.get_content_maintype() == "multipart":
            for content in self.message.walk():
                if content.get_content_type() == "text/plain":
                    self.body = content.get_payload(decode=True)
                elif content.get_content_type() == "text/html":
                    self.html = content.get_payload(decode=True)
        elif self.message.get_content_maintype() == "text":
            self.body = self.message.get_payload()

        if self.content_transfer_encoding == "base64":
            self.body = base64.b64decode(self.body)

        self.sent_at = datetime.datetime.fromtimestamp(time.mktime(email.utils.parsedate_tz(self.message['date'])[:9]))

        self.flags = self.parse_flags(raw_headers)

        self.labels = self.parse_labels(raw_headers)

        if re.search(r'X-GM-THRID (\d+)', raw_headers):
            self.thread_id = re.search(r'X-GM-THRID (\d+)', raw_headers).groups(1)[0]
        if re.search(r'X-GM-MSGID (\d+)', raw_headers):
            self.message_id = re.search(r'X-GM-MSGID (\d+)', raw_headers).groups(1)[0]

        self.attachments = [
            Attachment(attachment) for attachment in self.message._payload
            if not isinstance(attachment, basestring) and attachment.get('Content-Disposition') is not None
        ]


class Attachment:
    def __init__(self, attachment):
        self.name = attachment.get_filename()
        self.payload = attachment.get_payload(decode=True)
        self.size = int(round(len(self.payload) / 1000.0))

    def save(self, path=None):
        if path is None:
            path = self.name
        elif os.path.isdir(path):
            path = os.path.join(path, self.name)

        with open(path, 'wb') as f:
            f.write(self.payload)
