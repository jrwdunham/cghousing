"""Read the ./fixtures.json file and create a new file (fixtureswithusers.json)
containing Django auth.user fixtures for each *member*-type Person in that
file. Write this to disk as a new fixtures file for: ./fixtureswithusers.json.

"""

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

fixtures = json.load(open(fixtures_path, 'rb'))

users = []
for fixture in fixtures:
    if fixture['model'] == 'coop.person' and fixture['fields']['member']:
        fixture['fields']['user'] = memberid2userid(fixture['pk'])
        users.append(generate_user(fixture))

new_fixtures = [generate_superuser()] + users + fixtures

json.dump(new_fixtures, open(new_fixtures_path, 'wb'), indent=2)

