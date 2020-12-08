"""Forward committee emails to current committee members.

This script handles incoming emails to CG Housing committee-specific email
accounts and forwards them to the emails of the members of the relevant
committee. In this way, someone can send an email to board@cghousing.org or
maintenance@cghousing.org and the email will be stored on that webmail account
and also forwarded to the current members of the board or the maintenance
committee respectively.

In order for this to work, the WebFaction account must be set up with email
addresses that correspond to the names of committees, e.g., an email address
for "maintenance@cghousing.org" must exist in order for emails to that address
to be forwarded to members of the "Maintenance" committee.


"""

import imp
import logging
import os
import psycopg2
import pprint
import sys

from email.parser import Parser
from email.mime.multipart import MIMEMultipart
import smtplib


# Get and configure logger.
LOGGER = logging.getLogger(__file__)
hdlr = logging.FileHandler(
    '/home/cghousing/email-forwarding/emailforwarding.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
LOGGER.addHandler(hdlr)
LOGGER.setLevel(logging.INFO)


CG_BOARD_USERNAME = os.getenv('CG_BOARD_USERNAME', 'no cg board username')
CG_HOUSING_BOARD_PASSWORD = os.getenv(
    'CG_HOUSING_BOARD_PASSWORD', 'no cg board password')


# Get the Django settings for the CG Housing application.
# Here we import the cg_housing Django settings module so we can get the
# Postgresql database configuration details.
CG_DJANGO_SETTINGS_DIR = '/home/cghousing/webapps/cghousing_django/cghousing/cghousing/cghousing/'
CG_DJANGO_SETTINGS = 'settings'
fp, pathname, description = imp.find_module(CG_DJANGO_SETTINGS, [CG_DJANGO_SETTINGS_DIR])
try:
    cg_django_settings = imp.load_module(
        CG_DJANGO_SETTINGS, fp, pathname, description)
finally:
    if fp:
        fp.close()
DB_CONF = cg_django_settings.DATABASES['default']


# Committee email addresses to name mapping
EMAIL_2_COMMITTEE_NAME = {
    'board': 'Board',
    'finance': 'Finance',
    'maintenance': 'Maintenance',
    'common_room': 'Common room',
    'members': 'Co-op',
    'grounds': 'Grounds',
    'kids': 'Kids',
    'membership': 'Membership',
    'participation': 'Participation',
    'pets': 'Pets',
    'social': 'Social',
    'welcoming': 'Welcoming'
}


def get_committee_emails(committee):
    """Get the emails of the committee named ``committee`` from the CG Housing
    PostgreSQL database and return them as a list.
    """
    conn = psycopg2.connect(
        host='127.0.0.1',
        database=DB_CONF['NAME'],
        user=DB_CONF['USER'],
        password=DB_CONF['PASSWORD'])
    cursor = conn.cursor()
    sql = """SELECT p.email
        FROM coop_person p
        INNER JOIN coop_committee_members ccm
            ON ccm.person_id=p.id
        INNER JOIN coop_committee c
            ON c.id=ccm.committee_id
        WHERE c.name='{}';""".format(committee.capitalize())
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        committee_emails = list(set([x[0] for x in result if x[0]]))
        return committee_emails
    except:
        LOGGER.exception('error when trying to get emails')
        raise


def forward_to_committee(recipient, parsed_email, committee_emails):
    """Forward the email in ``parsed_email`` to the committee members whose
    emails are in the list ``committee_emails``.
    """
    msg = MIMEMultipart()
    msg.set_payload(parsed_email)

    # Redirect the email to the members of the committee
    msg['To'] = ', '.join(committee_emails)

    # The email's From header must be the original recipient (e.g.,
    # maintenance@cghousing.org), otherwise we get an error if we try to send
    # an email from @cghousing.org using, say, a Gmail address.
    msg['From'] = recipient

    # ... but the reply-to can be the original sender.
    msg['Reply-to'] = parsed_email['from']

    msg['Subject'] = parsed_email['subject']
    s = smtplib.SMTP()
    s.connect('smtp.webfaction.com')
    s.login(CG_BOARD_USERNAME, CG_HOUSING_BOARD_PASSWORD)

    s.sendmail(parsed_email['to'], committee_emails, msg.as_string())
    s.quit()


def forward(recipient, raw_email):
    """Parse ``raw_email`` (string), map the recipient email address to a
    CG committee, and forward the email to the members of that committee.
    """
    parsed_email = Parser().parsestr(raw_email)
    try:
        committee = EMAIL_2_COMMITTEE_NAME[recipient.split('@')[0]]
    except KeyError:
        LOGGER.exception('Unable to find committee name for email %s', recipient)
        raise
    LOGGER.info('Received an email from "%s" to "%s" with subject "%s"',
                parsed_email['from'], recipient, parsed_email['subject'])
    committee_emails = get_committee_emails(committee)
    LOGGER.info('Forwarding email to "%s"', ', '.join(committee_emails))
    forward_to_committee(recipient, parsed_email, committee_emails)
