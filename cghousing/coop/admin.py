from django.contrib import admin
from coop.models import Person, Unit, UnitInspection, Committee, Move,\
    BlockRepresentative, Forum, Thread, Post
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


CREATE_MODIFY_INFO = (
    'Creation & modification information', {
        'fields': [
            'creator',
            'datetime_created',
            'modifier',
            'datetime_modified'],
        'classes': [
            'collapse'
        ]
    }
)

CREATE_MODIFY_INFO_ = (
    'Creation & modification information', {
        'fields': [
            'get_creator',
            'datetime_created',
            'get_modifier',
            'datetime_modified'],
        'classes': [
            'collapse'
        ]
    }
)

READONLY_FIELDS = (
    'creator',
    'modifier',
    'datetime_modified',
    'datetime_created'
)

READONLY_FIELDS_ = (
    'get_creator',
    'datetime_created',
    'get_modifier',
    'datetime_modified'
)


class PersonGetter:
    """Class that defines the `get_creator` and `get_modifier` methods that are
    used by both the ModelAdmin and Inline subclasses defined here. This class
    should be the second superclass of all ModelAdmins and Inlines that need
    these methods.

    """

    def get_person(self, obj, role):
        """Return a `Person` instance from `getattr(obj, 'role')`, which should
        be a `User` instance. `role` should be one of 'creator' or 'modifier'.

        """

        user = getattr(obj, role)
        if hasattr(user, 'person'):
            return user.person
        else:
            if user.first_name and user.last_name:
                return '%s %s' % (user.first_name, user.last_name)
            else:
                return user

    def get_creator(self, obj):
        return self.get_person(obj, 'creator')

    get_creator.short_description = u'Creator'

    def get_modifier(self, obj):
        return self.get_person(obj, 'modifier')

    get_modifier.short_description = u'Modifier'


class PersonInline(admin.StackedInline, PersonGetter):
    """This is so that Co-op Person objects will be displayed with Django
    auth User objects.

    See https://docs.djangoproject.com/en/1.7/topics/auth/customizing/#extending-the-existing-user-model

    """

    model = Person
    fk_name = "user"
    can_delete = False
    verbose_name_plural = 'Co-op Member Profile'
    readonly_fields = READONLY_FIELDS

    fieldsets = [
        (None, {
            'fields': [
                'first_name',
                'last_name',
                'email',
                'unit',
                'member',
                'committee_excused',
                'notes']}),
        ('Phone numbers(s)', {
            'fields': ['phone_numbers'],
            'classes': ['collapse']}),
        ('Children', {
            'fields': ['children'],
            'classes': ['collapse']}),
        CREATE_MODIFY_INFO
    ]


class UserAdmin(UserAdmin):
    inlines = (PersonInline,)



class MyModelAdmin(admin.ModelAdmin, PersonGetter):
    """Subclass this for coop model admins. It sets the modifier and creator
    appropriately, using the logged-in user.

    """

    def save_model(self, request, obj, form, change):
        """Set the creator and modifier based on the logged-in user.

        """

        obj.modifier = request.user
        if not change:
            obj.creator = request.user
        obj.save()

    def save_formset(self, request, form, formset, change):
        """This causes the creator/modifier to be appropriately saved in Django
        Admin Inlines. See
        https://docs.djangoproject.com/en/1.7/ref/contrib/admin/#django.contrib.admin.ModelAdmin.save_formset

        """

        instances = formset.save(commit=False)
        for instance in instances:
            instance.modifier = request.user
            if not instance.id:
                instance.creator = request.user
            instance.save()
        formset.save_m2m()


class InspectionsInline(admin.StackedInline, PersonGetter):
    model = UnitInspection
    extra = 0


class OccupantsInline(admin.TabularInline):
    model = Person
    extra = 0
    verbose_name = 'Occupant'
    verbose_name_plural = 'Occupants'


class UnitAdmin(MyModelAdmin):

    list_display = (
        'block_number',
        'unit_number',
        'get_occupants',
        'bedrooms',
        'bathrooms',
        'notes'
    )

    ordering = ('block_number', 'unit_number')

    fieldsets = [
        (None, {
            'fields': [
                'block_number',
                'unit_number',
                'notes',
                'bedrooms',
                'bathrooms']}),
        CREATE_MODIFY_INFO
    ]

    readonly_fields = READONLY_FIELDS

    list_filter = ['block_number']

    search_fields = ['occupants__first_name', 'occupants__last_name']

    # inlines = [InspectionsInline, OccupantsInline]

    def has_add_permission(self, request):
        return False

    def get_occupants(self, obj):
        """Return a string of comma-delimited names of the occupants of
        this unit.

        """

        occupants = obj.occupants.all()
        adults = [str(o) for o in occupants]
        children = set()
        for occupant in occupants:
            for child in occupant.children.all():
                children.add(str(child))
        all_occupants = adults + list(children)
        # return u', '.join(all_occupants)
        if len(all_occupants) == 0:
            return u''
        elif len(all_occupants) == 1:
            return all_occupants[0]
        else:
            return '%s and %s' % (', '.join(all_occupants[:-1]), all_occupants[-1])

    get_occupants.short_description = "Occupants"


class CommitteesInline(admin.TabularInline):
    model = Committee.members.through
    verbose_name = 'Commitee'
    verbose_name_plural = 'Commitees'
    extra = 0


class MovesInline(admin.TabularInline):
    model = Move.movers.through
    verbose_name = 'Move'
    verbose_name_plural = 'Moves'
    extra = 0


class PersonAdmin(MyModelAdmin):

    readonly_fields = READONLY_FIELDS

    fieldsets = [
        (None, {
            'fields': [
                'first_name',
                'last_name',
                'email',
                'unit',
                'member',
                'committee_excused',
                'notes']}),
        ('Phone numbers(s)', {
            'fields': ['phone_numbers'],
            'classes': ['collapse']}),
        ('Children', {
            'fields': ['children'],
            'classes': ['collapse']}),
        CREATE_MODIFY_INFO
    ]

    list_display = ('last_name', 'first_name', 'address',
        'get_phone_numbers', 'email', 'member', 'get_committees')
    ordering = ('-member', 'last_name', 'first_name')
    filter_horizontal = ('children', 'phone_numbers')
    inlines = [CommitteesInline, MovesInline]

    list_filter = ['committees']

    search_fields = ['first_name', 'last_name', 'email', 'notes']

    def get_committees(self, obj):
        if obj.committee_excused:
            return u'Excused'
        chairships = map(str, obj.chairships.all())
        committees = map(str, obj.committees.order_by('name'))
        tmp = []
        for committee in committees:
            if committee in chairships:
                tmp.append(u'%s (chair)' % committee)
            else:
                tmp.append(committee)
        #return u', '.join([str(c) for c in obj.committees.order_by('name')])
        return u', '.join(tmp)

    get_committees.short_description = "Committees"

    def get_phone_numbers(self, obj):
        try:
            return u', '.join([unicode(x) for x in obj.phone_numbers.all()])
        except:
            return ''

    get_phone_numbers.short_description = "Phone(s)"


class CommitteeAdmin(MyModelAdmin):

    list_display = ('name', 'chair', 'get_members')
    ordering = ('name',)
    filter_horizontal = ('members',)

    fieldsets = [
        (None, {
            'fields': [
                'name',
                'chair',
                'members',
                'description']}),
        CREATE_MODIFY_INFO
    ]

    readonly_fields = READONLY_FIELDS

    def get_members(self, obj):
        try:
            return u', '.join([unicode(m) for m in obj.members.order_by('last_name')])
        except:
            return ''

    get_members.short_description = "Members"


class MoveAdmin(MyModelAdmin):

    list_display = ('move_type', 'get_movers', 'move_date', 'in_unit', 'out_unit', 'notes')

    filter_horizontal = ('movers',)

    def get_movers(self, obj):
        return u', '.join(map(str, obj.movers.all()))
    get_movers.short_description = 'Movers'


class BlockRepresentativeAdmin(MyModelAdmin):

    list_display = ('get_role', 'person')
    ordering = ('role', 'block_number')

    def get_role(self, obj):
        return u'%s for block %s' % (obj.role, obj.block_number)
    get_role.short_description = 'Role'


class PostInline(admin.StackedInline, PersonGetter):
    model = Post
    extra = 0

    fieldsets = [
        (None, {
            'fields': [
                'reply_to',
                'subject',
                'post']}),
        CREATE_MODIFY_INFO_
    ]

    readonly_fields = READONLY_FIELDS_

class ThreadInline(admin.StackedInline, PersonGetter):
    model = Thread
    extra = 0

    fieldsets = [
        (None, {
            'fields': [
                'subject',
                'post']}),
        CREATE_MODIFY_INFO
    ]

    readonly_fields = READONLY_FIELDS


class ForumAdmin(MyModelAdmin):

    list_display = (
        'name',
        'description',
        'get_thread_count',
        'get_post_count'
    )

    fieldsets = [
        (None, {
            'fields': [
                'name',
                'description']}),
        CREATE_MODIFY_INFO_]

    inlines = (ThreadInline,)

    readonly_fields = READONLY_FIELDS_

    def get_thread_count(self, obj):
        return len(obj.threads.all())

    get_thread_count.short_description = "Threads"

    def get_post_count(self, obj):
        post_count = 0
        for thread in obj.threads.all():
            post_count += thread.posts.count()
        return post_count

    get_post_count.short_description = "Posts"


class ThreadAdmin(MyModelAdmin):

    list_display = (
        'forum',
        'subject',
        'get_creator',
        'get_replies',
        'get_last_post'
    )

    fieldsets = [
        (None, {
            'fields': [
                'forum',
                'subject',
                'post']}),
        CREATE_MODIFY_INFO_
    ]

    readonly_fields = READONLY_FIELDS_

    inlines = (PostInline,)

    def get_replies(self, obj):
        return obj.posts.count()

    get_replies.short_description = u'Replies'

    def get_last_post(self, obj):
        last_post = obj.posts.order_by('datetime_created').last()
        if last_post:
            return last_post
        else:
            return u''

    get_last_post.short_description = u'Last post'


class PostAdmin(MyModelAdmin):

    list_display = (
        'thread',
        'subject',
        'get_post',
        'get_creator',
        'get_reply_to'
    )

    fieldsets = [
        (None, {
            'fields': [
                'thread',
                'reply_to',
                'subject',
                'post']}),
        CREATE_MODIFY_INFO_
    ]

    readonly_fields = READONLY_FIELDS_


    def get_reply_to(self, obj):
        if obj.reply_to:
            return obj.reply_to
        else:
            return u''

    get_reply_to.short_description = u'Reply to'

    def get_post(self, obj):
        return obj.get_truncated_post()

    get_post.short_description = u'Post'



admin.site.register(Person, PersonAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Committee, CommitteeAdmin)
# admin.site.register(Move, MoveAdmin)
# admin.site.register(BlockRepresentative, BlockRepresentativeAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Post, PostAdmin)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

