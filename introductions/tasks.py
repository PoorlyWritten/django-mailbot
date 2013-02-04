import logging
logger = logging.getLogger(__name__)
from .models import parse_one_mail, Introduction
from email_integration.models import RawEmail
from celery.task import periodic_task
from celery import task
from celery.task.schedules import crontab

@task
def parse_one_mail_task(raw_message_id):
    intro = parse_one_mail(raw_message_id)
    if intro:
        print 'Created intro: %s' % intro.pk
        logger.debug('Created intro: %s' % intro.pk)
    return intro

@periodic_task(run_every=crontab(minute="*"))
def assert_followups():
    unfinished_intros = Introduction.objects.all()
    for each in unfinished_intros:
        if len(each.followup_set.all()) < 2:
            each.create_followups()

@periodic_task(run_every=crontab(minute="*"))
def parse_all_mail():
    unparsed_mail = RawEmail.objects.filter(parsed=False)
    logger.debug("Processing %d unparsed raw emails" % len(unparsed_mail))
    print "Processing %d unparsed raw emails" % len(unparsed_mail)
    for each in unparsed_mail:
        logger.debug("Parsing Raw Email :  %s" % each.pk)
        parse_one_mail_task(each.pk)

