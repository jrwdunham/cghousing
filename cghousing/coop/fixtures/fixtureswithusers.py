"""Read the ./fixtures.json file and create a new file (fixtureswithusers.json)
containing Django auth.user fixtures for each *member*-type Person in that
file. Write this to disk as a new fixtures file for: ./fixtureswithusers.json.

"""

import string
import json
import pprint
import copy
import os

this_path = os.path.dirname(os.path.realpath(__file__))
fixtures_path = os.path.join(this_path, 'fixtures.json')
new_fixtures_path = os.path.join(this_path, 'fixtureswithusers.json')

# pk, username, first_name, last_name, and email are taken from coop.person
# password is just the default Django 1.7 PBKDF2 password for 'a'.
# username is first_name followed by last_name, all lowercase
USER_TEMPLATE = {
    "pk": None,
    "model": "auth.user",
    "fields": {
        "username": "",
        "password": "pbkdf2_sha256$15000$VT40UZicMRUb$4wekBQWWOg4xae2pcDiwyXWGuKOGkJodg/GuMOxTsT0=",
        "first_name": "",
        "last_name": "",
        "email": "",
        "is_staff": True,
        "is_active": True
    }
}

FORUM_TEMPLATE = {
    "pk": None,
    "model": "coop.forum", 
    "fields": {
        "name": "",
        "description": ""
    }
}

# If we user 1 for a user index, Django's superuser (created via `manage.py
# syncdb` will be overwritten.
def memberid2userid(memberid):
    return 10 + memberid

def generate_user(member):
    user = copy.deepcopy(USER_TEMPLATE)
    user['pk'] = memberid2userid(member['pk'])
    user['fields']['first_name'] = member['fields']['first_name']
    user['fields']['last_name'] = member['fields']['last_name']
    user['fields']['email'] = member['fields']['email']
    user['fields']['username'] = '%s%s' % (
        user['fields']['first_name'].lower(),
        user['fields']['last_name'].lower())
    return user

def generate_superuser():
    superuser = copy.deepcopy(USER_TEMPLATE)
    superuser['pk'] = 1001
    superuser['fields']['first_name'] = u'Alexander'
    superuser['fields']['last_name'] = u'Adams'
    superuser['fields']['email'] = u'alexander@adams.com'
    superuser['fields']['username'] = u'a'
    superuser['fields']['is_superuser'] = True
    return superuser

def committee2forum(committee):
    forum = copy.deepcopy(FORUM_TEMPLATE)
    forum['pk'] = committee['pk']
    forum['fields']['name'] = committee['fields']['name']
    forum['fields']['description'] = u'Forum for the %s committee' % (
        committee['fields']['name'].lower())
    forum['fields']['url_name'] = name2url(forum['fields']['name'])
    return forum

# Converts a name (a string) to something that can be part of a URL
# WARN: non-dry copy from coop/views.py
def name2url(name):
    valid_chars = "- %s%s" % (string.ascii_letters, string.digits)
    url = ''.join(c for c in name if c in valid_chars)
    url = url.replace(' ','-').lower()
    return url

member_ids = []
users = []
committees = []
forums = []
new_fixtures = []
coop_committee_fixture = None

# Loop through the fixtures, creating new ones and storing information.
fixtures = json.load(open(fixtures_path, 'rb'))
for fixture in fixtures:

    # Create auth.user fixtures and store the pks of the members.
    if fixture['model'] == 'coop.person' and fixture['fields']['member']:
        fixture['fields']['user'] = memberid2userid(fixture['pk'])
        users.append(generate_user(fixture))
        member_ids.append(fixture['pk'])

    if fixture['model'] == 'coop.forum':
        fixture['fields']['url_name'] = name2url(fixture['fields']['name'])

    # Get the Coop Committee fixture.
    if fixture['model'] == 'coop.committee':
        if fixture.get('fields', {}).get('name') == u'Co-op':
            coop_committee_fixture = fixture
        else:
            new_fixtures.append(fixture)
            forums.append(committee2forum(fixture))
    else:
        new_fixtures.append(fixture)


# All co-op members are members of the "Co-op Committee"
coop_committee_fixture['fields']['members'] = member_ids

new_fixtures = forums + \
    [generate_superuser(), coop_committee_fixture] + \
    users + \
    new_fixtures

json.dump(new_fixtures, open(new_fixtures_path, 'wb'), indent=2)

