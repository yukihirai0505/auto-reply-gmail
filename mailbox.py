from message import Message
from utf import encode as encode_utf7, decode as decode_utf7


class Mailbox:
    def __init__(self, gmail, name="INBOX"):
        self.name = name
        self.gmail = gmail
        self.date_format = "%d-%b-%Y"
        self.messages = {}

    @property
    def external_name(self):
        if "external_name" not in vars(self):
            vars(self)["external_name"] = encode_utf7(self.name)
        return vars(self)["external_name"]

    @external_name.setter
    def external_name(self, value):
        if "external_name" in vars(self):
            del vars(self)["external_name"]
        self.name = decode_utf7(value)

    def mail(self, prefetch=False, **kwargs):
        search = ['ALL']

        kwargs.get('read') and search.append('SEEN')
        kwargs.get('unread') and search.append('UNSEEN')
        kwargs.get('header') and search.extend(['HEADER', kwargs.get('header')[0], kwargs.get('header')[1]])
        kwargs.get('sender') and search.extend(['FROM', kwargs.get('sender')])
        kwargs.get('fr') and search.extend(['FROM', kwargs.get('fr')])
        kwargs.get('to') and search.extend(['TO', kwargs.get('to')])
        kwargs.get('cc') and search.extend(['CC', kwargs.get('cc')])
        kwargs.get('subject') and search.extend(['SUBJECT', kwargs.get('subject')])
        kwargs.get('body') and search.extend(['BODY', kwargs.get('body')])
        kwargs.get('label') and search.extend(['X-GM-LABELS', kwargs.get('label')])
        kwargs.get('attachment') and search.extend(['HAS', 'attachment'])
        kwargs.get('query') and search.extend([kwargs.get('query')])

        emails = []
        # print search
        response, data = self.gmail.imap.uid('SEARCH', *search)
        if response == 'OK':
            uids = filter(None, data[0].split(' '))  # filter out empty strings

            for uid in uids:
                if not self.messages.get(uid):
                    self.messages[uid] = Message(self, uid)
                emails.append(self.messages[uid])

            if prefetch and emails:
                messages_dict = {}
                for email in emails:
                    messages_dict[email.uid] = email
                self.messages.update(self.gmail.fetch_multiple_messages(messages_dict))

        return emails
