import re
import imaplib

from mailbox import Mailbox
from utf import encode as encode_utf7, decode as decode_utf7
import smtplib


class Gmail:
    # GMail IMAP defaults
    GMAIL_IMAP_HOST = 'imap.gmail.com'
    GMAIL_IMAP_PORT = 993

    # GMail SMTP defaults
    GMAIL_SMTP_HOST = "smtp.gmail.com"
    # 465 or 587
    GMAIL_SMTP_PORT = 465

    def __init__(self):
        self.username = None
        self.password = None
        self.access_token = None

        self.imap = None
        self.smtp = None
        self.logged_in = False
        self.mailboxes = {}
        self.current_mailbox = None

    def connect(self, raise_errors=True):
        self.imap = imaplib.IMAP4_SSL(self.GMAIL_IMAP_HOST, self.GMAIL_IMAP_PORT)
        return self.imap

    def fetch_mailboxes(self):
        response, mailbox_list = self.imap.list()
        if response == 'OK':
            for mailbox in mailbox_list:
                mailbox_name = mailbox.split('"/"')[-1].replace('"', '').strip()
                mailbox = Mailbox(self)
                mailbox.external_name = mailbox_name
                self.mailboxes[mailbox_name] = mailbox

    def use_mailbox(self, mailbox):
        if mailbox:
            self.imap.select(mailbox)
        self.current_mailbox = mailbox

    def mailbox(self, mailbox_name):
        if mailbox_name not in self.mailboxes:
            mailbox_name = encode_utf7(mailbox_name)
        mailbox = self.mailboxes.get(mailbox_name)

        if mailbox and not self.current_mailbox == mailbox_name:
            self.use_mailbox(mailbox_name)

        return mailbox

    def login(self, username, password):
        self.username = username
        self.password = password

        if not self.imap:
            self.connect()

        try:
            imap_login = self.imap.login(self.username, self.password)
            self.logged_in = (imap_login and imap_login[0] == 'OK')
            if self.logged_in:
                self.fetch_mailboxes()
        except imaplib.IMAP4.error:
            raise RuntimeError

        return self.logged_in

    def authenticate(self, username, access_token):
        self.username = username
        self.access_token = access_token

        if not self.imap:
            self.connect()

        try:
            auth_string = 'user=%s\1auth=Bearer %s\1\1' % (username, access_token)
            imap_auth = self.imap.authenticate('XOAUTH2', lambda x: auth_string)
            self.logged_in = (imap_auth and imap_auth[0] == 'OK')
            if self.logged_in:
                self.fetch_mailboxes()
        except imaplib.IMAP4.error:
            raise RuntimeError

        return self.logged_in

    def logout(self):
        self.imap.logout()
        self.logged_in = False

    def label(self, label_name):
        return self.mailbox(label_name)

    def find(self, mailbox_name="[Gmail]/All Mail", **kwargs):
        box = self.mailbox(mailbox_name)
        return box.mail(**kwargs)

    def fetch_multiple_messages(self, messages):
        fetch_str = ','.join(messages.keys())
        response, results = self.imap.uid('FETCH', fetch_str, '(BODY.PEEK[] FLAGS X-GM-THRID X-GM-MSGID X-GM-LABELS)')
        for index in xrange(len(results) - 1):
            raw_message = results[index]
            if re.search(r'UID (\d+)', raw_message[0]):
                uid = re.search(r'UID (\d+)', raw_message[0]).groups(1)[0]
                messages[uid].parse(raw_message)

        return messages

    def labels(self, require_unicode=False):
        keys = self.mailboxes.keys()
        if require_unicode:
            keys = [decode_utf7(key) for key in keys]
        return keys

    # imap extension: https://developers.google.com/gmail/imap/imap-extensions
    def inbox(self):
        return self.mailbox("INBOX")

    def all_mail(self):
        return self.mailbox("[Gmail]/All Mail")

    def send_mail(self, data):
        data["From"] = self.username
        self.smtp = smtplib.SMTP_SSL(self.GMAIL_SMTP_HOST, self.GMAIL_SMTP_PORT)
        self.smtp.ehlo()
        self.smtp.login(self.username, self.password)
        self.smtp.mail(self.username)
        self.smtp.rcpt(data["To"])
        self.smtp.data(data.as_string())
        self.smtp.quit()
