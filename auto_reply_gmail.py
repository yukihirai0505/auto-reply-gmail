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
    reply_body = "超SPEED!!!!\n\n\n\n%s %s\n> %s" % (msg.date, msg.fr, msg.body.replace("\n", "\n> "))
    msg.reply(reply_body)
    msg.read()
