#!/usr/bin/python

from imaplib import IMAP4_SSL
import rfc822
import string
import os
import os.path
import re

class Msg:
    """A filename-like object for passing a string to rfc822.Message"""
    def __init__(self, text):
        self.lines = string.split(text, '\015\012')
        self.lines.reverse()
    def readline(self):
        try: return self.lines.pop() + '\n'
        except: return ''

def file_to_string(file_name):
    """Reads a file's content to a string."""
    f = open(file_name)
    s = f.read()
    f.close()
    return s

def string_to_file(s,file_name):
    """Writes a string to a file."""
    f = open(file_name,'w')
    f.write(s)
    f.close()

def get_next_file(dir):
    """Returns a filename with a *.mail form, such that there is no file with
    that name."""
    i = 1
    while i != 0:
        filename = os.path.join(dir,('%d.mail' % i))
        if os.path.exists(filename):
            i += 1
        else:
            i = 0
    return filename

def getheader_str(m, header):
    """Reads the header from the given message. If the message does not contain
    that header, the result will be a 'None' string."""
    return str(m.getheader(header))

def download_email(email_index):
    """Writes the email with the given index to file index.mail."""

    header = server.fetch(
            email_index,
            '(BODY[HEADER.FIELDS (SUBJECT FROM MESSAGE-ID IN-REPLY-TO)])')[1][0][1]
    m = rfc822.Message(Msg(header), 0)
    from_ =  getheader_str(m, 'from')
    subject = getheader_str(m, 'subject')
    message_id = getheader_str(m, 'message-id')
    in_reply_to = getheader_str(m, 'in-reply-to')
    text = server.fetch(email_index,'(BODY[TEXT])')[1][0][1]
    nl = "\n"
    output = \
        "From: " + from_ + nl + \
        "Subject: " + subject + nl + \
        "Message-ID: " + message_id + nl + \
        "In-Reply-To: " + in_reply_to + nl + \
        "------------------------------------------------------------------------" + nl + \
        str(text)
    output = re.sub(r'\r\n',r'\n',output)
    string_to_file(output, get_next_file(mail_dir))


# Login settings
def get_setting(name):
    return file_to_string(name).strip()

host = get_setting('host')
port = int(get_setting('port'))
username = get_setting('username')
password = get_setting('pw')
mail_dir = 'mail'

server = IMAP4_SSL(host, port)
server.login(username, password)
server.select("INBOX")[1]
emails = server.search(None, '(ALL)')[1][0]

if not os.path.exists(mail_dir):
    os.mkdir(mail_dir)

for email_index in emails.split(' '):
    email_index = int(email_index)
    if not os.path.exists(os.path.join(mail_dir, "%d.mail" % email_index)):
        print 'Downloading mail #%d' % email_index
        download_email(email_index)

server.close()

