from django.db import models
from django.utils import timezone
from django.utils.timezone import now, localtime
from django.contrib.auth.models import User

import datetime

"""Models for the Co-op App

- Person (Member is a subclass)
- Committees
- Units
- Pages

"""

class Base(models.Model):
    """Abstract base class for CG models. Implements the functionality
    for creator, modifier, datetime created, and datetime modified attributes.
    The datetime attributes are automatically populated on update and creation,
    respectively.

    See http://stackoverflow.com/questions/1737017/django-auto-now-and-auto-now-add?rq=1

    """

    creator = models.ForeignKey(
        User,
        null=True,
        related_name='+'
    )

    datetime_created = models.DateTimeField(
        null=True,
        editable=False,
        default=now
    )

    modifier = models.ForeignKey(
        User,
        null=True,
        related_name='+'
    )

    datetime_modified = models.DateTimeField(
        null=True,
        editable=False,
        default=now
    )

    def save(self, *args, **kwargs):
        """On save, update timestamps.

        """

        if not self.id:
            self.datetime_created = now()
        self.datetime_modified = now()
        return super(Base, self).save(*args, **kwargs)

    class Meta:
        abstract = True

    def get_user_str(self, user):
        if hasattr(user, 'person'):
            return user.person
        elif user:
            if user.first_name and user.last_name:
                return '%s %s' % (user.first_name, user.last_name)
            else:
                return user
        else:
            return u''


class Unit(Base):
    """A model for each of the units/homes in the co-op.

    """

    def __unicode__(self):
        return u'Unit #%d, %d' % (self.unit_number, self.block_number)

    BLOCKS = (1701, 1703, 1715, 1739, 1747) # possible block numbers
    UNITS = range(101, 114) # possible unit numbers
    BEDROOMS = range(1, 5) # possible number of bedrooms in a unit
    BATHROOMS = range(1, 3) # possible number of bathrooms in a unit

    block_number = models.IntegerField(
        max_length=4,
        choices=tuple([(b, b) for b in BLOCKS]))

    unit_number = models.IntegerField(
        max_length=3,
        choices=tuple([(u, u) for u in UNITS]))

    notes = models.TextField(
        blank=True,
        help_text=u'Notes about the unit.'
    )

    bedrooms = models.IntegerField(
        default=3,
        max_length=1,
        choices = tuple([(x, x) for x in BEDROOMS]))

    bathrooms = models.IntegerField(
        default=1,
        max_length=1,
        choices = tuple([(x, x) for x in BATHROOMS]))

    # Relational attributes defined on other models:
    # occupants: reverse one-to-many relation defined on Person model
    # move_ins: reverse one-to-many relation defined on Move model
    # move_outs: reverse one-to-many relation defined on Move model

    # Attributes to add:
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

    TODO: connect this class to the Django auth User class

    https://docs.djangoproject.com/en/1.7/topics/auth/customizing/#extending-the-existing-user-model

    """

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)

    # The Django auth_user corresponding to this person (if applicable)
    # The `User` instance can access it's corresponding `Person` instance via
    # its `get_profile()` method.
    # See https://docs.djangoproject.com/en/1.7/topics/auth/customizing/#extending-the-existing-user-model
    user = models.OneToOneField(
        User,
        null=True,
    )

    first_name = models.CharField(
        max_length=200
    )

    last_name = models.CharField(
        max_length=200
    )

    email = models.CharField(
        max_length=200,
        blank=True
    )

    phone_numbers = models.ManyToManyField(
        PhoneNumber,
        related_name='owners',
        blank=True
    )

    unit = models.ForeignKey(
        Unit,
        null=True,
        related_name='occupants'
    )

    committee_excused = models.BooleanField(
        default=False,
        help_text=(u'If set to true, then this person is excused from the '
            'requirement that all members belong to at least one committee.')
    )

    member = models.BooleanField(
        default=False,
        help_text='Is this person a member of the co-op?'
    ) # Member of Co-op or not

    notes = models.TextField(
        blank=True
    )

    children = models.ManyToManyField(
        "Person",
        related_name='parents',
        blank=True
    )

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


class UnitInspection(Base):
    """A model for a unit inspection.

    """

    def __unicode__(self):
        return u'Inspection of %s on %s' % (
            self.unit, self.date.strftime('%b %d, %Y'))

    unit = models.ForeignKey(
        Unit,
        related_name='inspections')

    date = models.DateField() # date the inspection took place, if it has.

    request_date = models.DateField(
        null=True) # date the inspection was requested.

    requester = models.ForeignKey(
        Person,
        null=True,
        related_name='requested_inspections')

    content = models.TextField(
        blank=True)


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


class Page(Base):
    """A model for generic pages on the web site.

    """

    # Title of page; add unique constraint
    title = models.CharField(
        unique=True,
        max_length=200
    )

    # Content of the page in Markdown (or filtered HTML)
    content = models.TextField(
        blank=True
    )

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


class Forum(Base):
    """Model for the various discussion forums for the coop.

    Each forum may contain zero or more threads.

    TODO:

    1. admin view:
      - name
      - description
      - (moderator(s) ?)
      - thread count
      - post count
      - last post (thread title, poster, timestamp)

    """

    def __unicode__(self):
        return self.name

    # Name of the forum
    name = models.CharField(
        unique=True,
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    # Relational attributes defined on other models:
    # threads


class Thread(Base):
    """Model for the discussion threads contained in the forums.

    """

    def __unicode__(self):
        return self.subject

    # Subject of the thread
    subject = models.CharField(
        max_length=200
    )

    forum = models.ForeignKey(
        Forum,
        related_name='threads',
        null=True,
        default=None
    )

    # The content of the post
    #post = models.TextField()

    # TODO: other attributes:
    # - subcategory # TODO: is this useful here?
    # - markup language # markdown, reStructuredText
    # - keywords

    # TODO: admin interface:
    # - view count (first I need to count views in the app logic)
    # - reply count
    # - last post (thread title, poster, timestamp)

    # Relational attributes defined on other models:
    # posts


class Post(Base):
    """Model for the posts in a forum thread.

    Every post needs a `reply_to` (i.e., a parent post), except for the first
    one created.

    """

    def __unicode__(self):
        """Returns something like: "I'll be there! (by Alexander Adams on Jan 27
        2015 at 03:04:03 PM)"

        """

        post = self.get_truncated_post()
        post_time = localtime(self.datetime_created).strftime("%b %d %Y at %r")
        poster = self.get_user_str(self.creator)
        return u'%s (by %s on %s)' % (post, poster, post_time)

    def get_truncated_post(self):
        max_len = 30
        if len(self.post) > max_len:
            return u'%s ...' % self.post[:30]
        else:
            return self.post

    # Subject of the post
    # Should default to subject of thread, but user can modify it.
    subject = models.CharField(
        max_length=200
    )

    # The content of the post
    post = models.TextField()

    # The thread that this post belongs to.
    thread = models.ForeignKey(
        Thread,
        related_name='posts',
        blank=True,
        null=True,
        default=None
    )

    # The post that this post is responding to.
    # Only the initial post should be able to lack a reply_to value.
    reply_to = models.ForeignKey(
        'self',
        null=True,
        blank=True, # In the GUI, the default should be the last post.
        related_name='replies'
    )

    # TODO: other attributes:
    # - markup language # markdown, reStructuredText


class Committee(Base):
    """A model for each committee.

    """

    def __unicode__(self):
        return self.name

    # Commmittee name, e.g., 'Finance', 'Grounds', etc.
    name = models.CharField(
        max_length=200
    )

    # A chair is many-to-one: each committee has exactly one, but an
    # overworked member can be chair of many (I think...)
    # Note: some committees are currently lacking a chair and some appear
    # to have two. Is the last phenomenon an error?
    chair = models.ForeignKey(
        Person,
        blank=True,
        null=True,
        related_name='chairships'
    )

    # Members are many-to-many: committees can have multiple members and
    # people can be on multiple committees.
    members = models.ManyToManyField(
        Person,
        related_name='committees',
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    # Relational attributes defined on other models:
    # meeting_minutes


class MeetingMinutes(Base):
    """Model for holding meeting minutes.

    """

    def __unicode__(self):
        return 'Meeting of %s on %s' % (
            self.committee.name, self.meeting_date.strftime('%b %d, %Y'))

    # Commmittee name, e.g., 'Finance', 'Grounds', etc.
    committee = models.ForeignKey(
        Committee,
        related_name='meeting_minutes'
    )

    # date when the meeting occurred.
    meeting_date = models.DateField()

    # meeting minutes in text form
    minutes = models.TextField(
        blank=True
    )

    # TODO: file object(s) for minutes in file (.pdf, .doc, .txt) form

    class Meta:
        verbose_name_plural = "Meeting minutes"
