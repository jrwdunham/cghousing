import os
import django
import random
import string
import email
import smtplib
import pprint
import getpass
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cghousing.settings")
django.setup()
from coop.models import Person

def get_people():
    return Person.objects.all()


def generate_password():
    t = ['l', 'u', 'p', 'd', 'l', 'u', 'p', 'd', 'l', 'l']
    random.shuffle(t)
    pwd = []
    for c in t:
        if c == 'l':
            pwd.append(random.choice(string.lowercase))
        elif c == 'u':
            pwd.append(random.choice(string.uppercase))
        elif c == 'p':
            pwd.append(random.choice(string.punctuation))
        else:
            pwd.append(random.choice(string.digits))
    return ''.join(pwd)


def get_email_msg(person):
    return '''
Hi {first_name},

You are receiving this email because you are a member of the Common Ground
Housing Co-op and because the co-op's web site at https://www.cghousing.org has
been updated and your password has changed.

Your username and password for the web site are now as follows:

    - username: {username}
    - password: {password}

When you log in for the first time, you should change your password. Here's how:

    1. Click on your name in the top right of the page.
    2. Click "Change password"
    3. Enter your current password and then your new one twice and click the
       "Change Password" button.

The new Common Ground web site now contains useful information and features
that are accessible only to members who are logged in. Please contact me if you
have concerns about these features or if you have suggestions for changes or
improvements. In brief, these members-only features are:

    1. Minutes of members' meetings.
    2. Members of the co-op: contact info & Membership List.
    3. Committees active in the co-op.
    4. Rules of the co-op (red book).
    5. Units in the co-op.
    6. Forums: for discussions about co-op-related matters.
    7. Pages: web pages we create.
    8. Files: e.g., images, minutes, etc.

See the Help page (https://www.cghousing.org/help/) of the web site to find out
more.

- Joel


'''.format(
    first_name=person['first_name'],
    username=person['username'],
    password=person['password']
        ).strip()


def send_email(params):
    """Send an email via gmail, using info in `params`.

    """

    fromaddr = params['fromaddr']
    toaddrs = params['toaddrs']
    mymsg = params['mymsg']
    username = params['username']
    password = params['password']
    subject = params['subject']

    # The actual mail send
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username, password)
    msg = email.MIMEMultipart.MIMEMultipart()
    msg['Subject'] = subject
    msg['To'] = toaddrs
    msg['From'] = fromaddr
    msg.attach(email.MIMEText.MIMEText(mymsg))
    server.sendmail(fromaddr, toaddrs, msg.as_string())
    server.quit()


if __name__ == '__main__':
    """
    For each person:
    1. filter out the superusers and people without .user attributes
    2. give each person.user a new randomly generated password, while saving
       state
    3. If person has email, send invitation email with new password.

    """

    people = []

    for p in get_people():
        if p.user and p.user.is_active and not p.user.is_superuser:
            user_email = getattr(p, 'email', None)
            if not user_email:
                user_email = getattr(p.user, 'email', None)
            person = {
                    'id': p.user.id,
                    'first_name': p.user.first_name,
                    'last_name': p.user.last_name,
                    'email': user_email,
                    'username': p.user.username,
                    'password': generate_password()
                    }
            p.user.set_password(person['password'])
            p.user.save()
            people.append(person)

    gmail_username = raw_input('Enter your gmail username: ')
    gmail_password = getpass.getpass('Enter your gmail password: ')

    for i, p in enumerate(people):
        if p.get('email'):
            params = {
                'fromaddr': '%s@gmail.com' % gmail_username,
                'toaddrs': p['email'],
                'mymsg': get_email_msg(p),
                'username': gmail_username,
                'password': gmail_password,
                'subject': 'Changes to Common Ground web site'
            }
            send_email(params)

