#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import gmail

GMAIL_USERNAME = os.getenv("GMAIL_USERNAME")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
SENDER_FILTER = os.getenv("SENDER_FILTER", "")

g = gmail.Gmail()

if not g.login(GMAIL_USERNAME, GMAIL_PASSWORD):
    sys.exit()

msgs = g.inbox().mail(prefetch=True, sender=SENDER_FILTER, unread=True)

for msg in msgs:
    # TODO: https://github.com/yukihirai0505/auto-mail_send/issues/1
    message = "超SPEED!!!!\n\n\n\n" + msg.message["Date"] + msg.message["From"] + "\n> " + msg.body.replace("\n", "\n> ")
    msg.reply(message)
    msg.read()
