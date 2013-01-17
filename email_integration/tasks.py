import logging
logger = logging.getLogger(__name__)
import poplib
from models import RawEmail, ParsedEmail
from django.conf import settings
from celery.task.schedules import crontab
from celery.task import periodic_task
from celery import task
from django.db import IntegrityError
from django.db import transaction
import datetime

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
        logger.debug("inside _tx_create_raw_message")
        transaction.commit()
    except:
        transaction.rollback()



@periodic_task(run_every=crontab(minute="*/5"))
def parse_all_mail():
    unparsed_mail = RawEmail.objects.filter(parsed=False)
    logger.debug("Processing %d unparsed raw emails" % len(unparsed_mail))
    for each in unparsed_mail:
        logger.debug("Parsing Raw Email :  %s" % each.pk)
        parse_one_mail(each.pk)


@task()
def parse_one_mail(raw_message_id):
    raw_message=RawEmail.objects.get(pk=raw_message_id)
    try:
        ParsedEmail.objects.create_parsed_email(raw_message = raw_message)
    except IntegrityError,e:
        logger.debug("couldn't create a parsed email because: %s" % e)
        raw_message.date_parsed = datetime.datetime.utcnow()
        raw_message.parsed = True
        raw_message.save()


@task()
def parse_email_from_mail(parsed_email_id):
    ParsedEmail.objects.get(pk=parsed_email_id)._parse_email_addresses()
