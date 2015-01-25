from django.db import models
from django.utils import timezone
from django.utils.timezone import now

import datetime

"""Models for the Co-op App

- Person (Member is a subclass)
- Committees
- Units
- Pages

"""

class Base(models.Model):
    """Abstract base class for CG models. Implements the functionality
    for datetime modified and created attributes that are automatically
    populated on update and creation, respectively. See
    http://stackoverflow.com/questions/1737017/django-auto-now-and-auto-now-add?rq=1

    """

    datetime_modified = models.DateTimeField(null=True, editable=False)
    datetime_created = models.DateTimeField(null=True, editable=False)

    def save(self, *args, **kwargs):
        """ On save, update timestamps

        """

        print 'In save method'
        if not self.id:
            self.datetime_created = now()
        self.datetime_modified = now()
        return super(Base, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class Unit(Base):
    """A model for each of the units/homes in the co-op.

    """

    def __unicode__(self):
        return u'#%d %d' % (self.unit_number, self.block_number)

    BLOCKS = (1701, 1703, 1715, 1739, 1747)
    UNITS = tuple(range(101, 114))
    block_number = models.IntegerField(
        max_length=4,
        choices=tuple([(b, b) for b in BLOCKS]))
    unit_number = models.IntegerField(
        max_length=3,
        choices=tuple([(u, u) for u in UNITS]))
    notes = models.TextField()

    # Relational attributes defined on other models:
    # occupants: reverse one-to-many relation defined on Person model
    # move_ins: reverse one-to-many relation defined on Move model
    # move_outs: reverse one-to-many relation defined on Move model

    # Attributes to add:
    # rooms (i.e., size of the unit)
    # unit_inspections (one-to-many with an inspection object)


class PhoneNumber(Base):
    """Phone number class so that people can have multiple phones.

    """

    def __unicode__(self):
        if self.phone_type:
            return u'%s (%s)' % (self.number, self.phone_type)
        else:
            return u'%s' % self.number

    number = models.CharField(max_length=12)
    phone_type = models.CharField(
        max_length=10,
        choices=tuple([(pt, pt) for pt in [u'', u'cell', u'home']]))

class Person(Base):
    """Model for people who live in the co-op: members and their family members.

    """

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)

    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    phone_numbers = models.ManyToManyField(PhoneNumber, related_name='owners')

    unit = models.ForeignKey(Unit, null=True, related_name='occupants')

    committee_excused = models.BooleanField(default=False)
    member = models.BooleanField(default=False) # Member of Co-op or not

    notes = models.TextField()
    children = models.ManyToManyField("Person", related_name='parents')

    def committees(self):
        return self.committees.all()

    def address(self):
        try:
            return u'#%s, %s' % (self.unit.unit_number, self.unit.block_number)
        except AttributeError:
            try:
                return u'#%s, %s' % (self.parents.all()[0].unit.unit_number,
                    self.parents.all()[0].unit.block_number)
            except AttributeError:
                return u''
    address.short_description = 'Address'

    class Meta:
        verbose_name_plural = "People"

    # Relational attributes defined on other models:
    # committees (many-to-many, defined on Committee model)
    # chairships (many-to-one, defined on Committee model)

    # role (for authorization)
    # date_of_birth (too personal?)
    # username
    # password
    # membership_start_date
    # membership_end_date

    # TODO: Figure out how to encode block-level maintenance and roof monitor roles? (see membership list)


class BlockRepresentative(Base):
    """Model for block-specific roles that may be relevant to particular
    committees. For example, block-specific maintenance and roof monitor roles.

    """

    BLOCKS = (1701, 1703, 1715, 1739, 1747)
    block_number = models.IntegerField(
        max_length=4,
        choices=tuple([(b, b) for b in BLOCKS]))
    committee = models.ForeignKey('Committee', null=True,
            related_name='block_representatives')
    person = models.ForeignKey('Person', null=True,
            related_name='block_representative_roles')
    ROLES = ('roof monitor', 'maintenance')
    role = models.CharField(max_length=30, choices=tuple([(r, r) for r in
        ROLES]))


class Committee(Base):
    """A model for each committee.

    """

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=200) # E.g., 'Finance', 'Grounds', etc.

    # A chair is many-to-one: each committee has exactly one, but an
    # overworked member can be chair of many (I think...)
    # Note: some committees are currently lacking a chair and some appear
    # to have two. Is the last phenomenon an error?
    chair = models.ForeignKey(Person, null=True, related_name='chairships')

    # Members are many-to-many: committees can have multiple members and
    # people can be on multiple committees.
    members = models.ManyToManyField(Person, related_name='committees')

    description = models.TextField()

    # meeting minutes


class Page(Base):
    """A model for generic pages on the web site.

    """

    # Title of page; add unique constraint
    title = models.CharField(max_length=200)

    # Content of the page in Markdown (or filtered HTML)
    content = models.TextField()

    # path (to route directly to the page, e.g., cghousing.or/pages/<path>


class Move(Base):
    """Model for moves into, out of, and within the co-op.

    """

    def __unicode__(self):
        move_date = self.move_date.strftime('%b %d, %Y')
        movers = u', '.join(map(str, self.movers.all()))
        if self.move_type == 'move in':
            return u'Move in to %s by %s on %s' % (self.in_unit, movers,
                move_date)
        elif self.move_type == 'move out':
            return u'Move out of %s by %s on %s' % (self.out_unit, movers,
                move_date)
        else:
            return u'Move from %s to %s by %s on %s' % (self.out_unit,
                self.in_unit, movers, move_date)

    MOVE_TYPES = ('move in', 'move out', 'internal move')
    move_type = models.CharField(max_length=20,
        choices=tuple([(mt, mt) for mt in MOVE_TYPES]))
    in_unit = models.ForeignKey(Unit, null=True, related_name='move_ins') # Unit moved into
    out_unit = models.ForeignKey(Unit, null=True, related_name='move_outs') # Unit moved out of
    movers = models.ManyToManyField(Person) # Persons involved in the move
    move_date = models.DateField()
    notes = models.TextField()

