"""One-off functionality for generating and printing a CSV membership list.
"""

def format_committees(committees_list, person):
    if person.committee_excused:
        return 'EXCUSED BY BOARD'
    return ', '.join([c.name for c in committees_list if c.name != 'Co-op'])


def get_chairships(committees_list, person):
    return ', '.join(c.name for c in committees_list if c.chair == person)


def format_children(children):
    return ', '.join('{} {}'.format(c.first_name, c.last_name) for c in children)


def format_phone_no(phone_number):
    if phone_number.phone_type:
        return '{} ({})'.format(phone_number.number, phone_number.phone_type)
    return '{}'.format(phone_number.number)


def format_phone_nos(phone_numbers):
    return ', '.join(format_phone_no(pn) for pn in phone_numbers)


def clean(thing):
    thing = thing.replace('"', r'\"')
    if ',' in thing:
        return '"' + thing + '"'
    return thing


def inspect(thing):
    print('\n'.join(x for x in dir(thing) if not x.startswith('_')))


def print_members_csv():
    people = []
    for person in models.Person.objects.all():
        if not person.member:
            continue
        try:
            person_tuple = (
                str(person.unit.block_number),
                str(person.unit.unit_number),
                '{} {}'.format(person.first_name, person.last_name),
                format_children(person.children.all()),
                format_phone_nos(person.phone_numbers.all()),
                person.email,
                format_committees(person.committees.all(), person),
                get_chairships(person.committees.all(), person),
            )
            people.append(','.join(clean(val) for val in person_tuple))
        except AttributeError as err:
            print 'Error with {} {} member? {}'.format(
                person.first_name,
                person.last_name,
                person.member)
    print ','.join((
        'Block Number',
        'Unit Number',
        'Name',
        'Children',
        'Phone Number',
        'Email Address',
        'Committee(s)',
        'Chairship(s)',
    ))
    people.sort()
    print '\n'.join(people)


print_members_csv()
