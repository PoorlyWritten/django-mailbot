import poplib
from models import RawEmail, ParsedEmail
from django.conf import settings

BOT_CONFIG = settings.get('EMAIL_BOT_CONF', {})


USER = BOT_CONFIG.get('POP_USER', None)
PASS = BOT_CONFIG.get('POP_PASS', None)
POPSERVER = BOT_CONFIG.get('POP_SERVER', 'pop.gmail.com')


def fetch_pop_messages():
    # Build a pop3 connection
    Mailbox = poplib.POP3_SSL(POPSERVER, '995')
    Mailbox.user(USER)
    Mailbox.pass_(PASS)
    # get message count
    messageCount = len(Mailbox.list()[1])
    print "retrieving %d messages" % messageCount
    for i in range(messageCount):
        raw_mail = RawEmail.objects.create(content='\n'.join(Mailbox.retr(i+1)[1]))
        parse_mail(raw_mail.id)
    Mailbox.quit()

def parse_mail(raw_message_id):
    ParsedEmail.objects.create_parsed_email(raw_message=RawEmail.objects.get(raw_message_id))
