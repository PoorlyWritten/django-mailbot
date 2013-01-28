import logging
logger = logging.getLogger(__name__)
import poplib
from models import RawEmail
from django.conf import settings
from celery.task.schedules import crontab
from celery.task import periodic_task
from django.db import transaction

try:
    BOT_CONFIG = settings.EMAIL_BOT_CONF
except AttributeError:
    BOT_CONFIG = {}


USER = BOT_CONFIG.get('POP_USER', None)
PASS = BOT_CONFIG.get('POP_PASS', None)
POPSERVER = BOT_CONFIG.get('POP_SERVER', 'pop.gmail.com')


@periodic_task(run_every=crontab(minute="*"))
def fetch_pop_messages():
    # Build a pop3 connection
    Mailbox = poplib.POP3_SSL(POPSERVER, '995')
    Mailbox.user(USER)
    Mailbox.pass_(PASS)
    # get message count
    messageCount = len(Mailbox.list()[1])
    print "retrieving %d messages" % messageCount
    for i in range(messageCount):
        logger.debug("calling transaction on creating message number %d" % i)
        _tx_create_raw_message('\n'.join(Mailbox.retr(i+1)[1]))
    Mailbox.quit()

@transaction.commit_manually
def _tx_create_raw_message(content):
    raw_mail = RawEmail(content=content)
    try:
        raw_mail.save(force_insert=True)
        transaction.commit()
    except:
        transaction.rollback()

