"""Simple Python script that hashes (i.e., transforms/hides) personal
information in the fixtures_real.json file that is used as a Django fixture.
This is useful so that we can put a fake fixtures object on a web-available
version control system without releasing personal information.

Specifically, this script hashes the ``first_name``, ``last_name``, ``email``, and
``unit`` attributes of the ``coop.person`` models and the ``number`` attribute of
the ``coop.phonenumber`` models.

Usage::

    >>> python hash_fixtures.py

.. note::

    This script assumes that there is a fixtures file called ``fixtures_real.json``
    in this directory. It writes the hashed ``fixtures.json`` file to the directory
    in which it is called.

"""

import json
import pprint
from random import sample, choice, shuffle


NAMES_FEMALE = []
with open('names_female_first.txt', 'r') as f:
    for line in f:
        NAMES_FEMALE.append(line.split()[0].lower().capitalize())

NAMES_MALE = []
with open('names_male_first.txt', 'r') as f:
    for line in f:
        NAMES_MALE.append(line.split()[0].lower().capitalize())

NAMES_LAST = []
with open('names_last.txt', 'r') as f:
    for line in f:
        NAMES_LAST.append(line.split()[0].lower().capitalize())

fixtures = json.load(open('fixtures_real.json', 'rb'))

NAMES = NAMES_FEMALE + NAMES_MALE + NAMES_LAST
FIRST_NAMES = NAMES_FEMALE + NAMES_MALE
EMAIL_DOMAINS = ('gmail.com', 'yahoo.com', 'aol.com', 'hotmail.com', 'live.com')

DIGITS = range(0, 10)
PHONE_NUMBER_HASH = {}
def hash_phone_number(phone_number):
    try:
        return PHONE_NUMBER_HASH[phone_number]
    except KeyError:
        new_number = '%s-%s-%s' % (''.join(map(str, sample(DIGITS, 3))),
            ''.join(map(str, sample(DIGITS, 3))), ''.join(map(str, sample(DIGITS, 4))))
        PHONE_NUMBER_HASH[phone_number] = new_number
        return new_number

EMAIL_HASH = {}
def hash_email(email):
    try:
        return EMAIL_HASH[email]
    except KeyError:
        new_email = u'%s@%s' % (choice(NAMES).lower(), choice(EMAIL_DOMAINS))
        EMAIL_HASH[email] = new_email
        return new_email

FIRST_NAME_HASH = {}
def hash_first_name(first_name):
    try:
        return FIRST_NAME_HASH[first_name]
    except KeyError:
        new_first_name = choice(FIRST_NAMES)
        FIRST_NAME_HASH[first_name] = new_first_name
        return new_first_name

LAST_NAME_HASH = {}
def hash_last_name(last_name):
    try:
        return LAST_NAME_HASH[last_name]
    except KeyError:
        new_last_name = choice(NAMES_LAST)
        LAST_NAME_HASH[last_name] = new_last_name
        return new_last_name

UNIT_NUMBERS = range(1, 47)
SHUFFLED_UNIT_NUMBERS = range(1, 47)
shuffle(SHUFFLED_UNIT_NUMBERS)
UNIT_NUMBER_HASH = dict(zip(UNIT_NUMBERS, SHUFFLED_UNIT_NUMBERS))
def hash_unit_number(unit_number):
    return UNIT_NUMBER_HASH[unit_number]

for fixture in fixtures:
    if fixture["model"] == "coop.person":
        fixture["fields"]["first_name"] = hash_first_name(fixture["fields"]["first_name"])
        fixture["fields"]["last_name"] = hash_last_name(fixture["fields"]["last_name"])
        if "email" in fixture["fields"]:
            fixture["fields"]["email"] = hash_email(fixture["fields"]["email"])
        if "unit" in fixture["fields"]:
            fixture["fields"]["unit"] = hash_unit_number(fixture["fields"]["unit"])
    if fixture["model"] == "coop.phonenumber":
        fixture["fields"]["number"] = hash_phone_number(fixture["fields"]["number"])

with open('fixtures.json', 'w') as f:
    f.write(json.dumps(fixtures, indent=2))

