from django.contrib import admin
from coop.models import Person, Unit, Committee, Move, BlockRepresentative


class UnitAdmin(admin.ModelAdmin):

    list_display = ('block_number', 'unit_number', 'get_occupants')
    ordering = ('block_number', 'unit_number')
    fieldsets = [
        (None, {'fields': ['block_number', 'unit_number', 'notes']}),
        ('Date information', {'fields': ['datetime_modified', 'datetime_created'],
            'classes': ['collapse']})
    ]
    readonly_fields = ('datetime_modified', 'datetime_created')


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
        return u', '.join(all_occupants)

    get_occupants.short_description = "Occupants"

class MembershipInline(admin.TabularInline):
    model = Committee.members.through
    verbose_name = 'Commitee'
    verbose_name_plural = 'Commitees'

class MovesInline(admin.TabularInline):
    model = Move.movers.through
    verbose_name = 'Move'
    verbose_name_plural = 'Moves'

class PersonAdmin(admin.ModelAdmin):

    readonly_fields = ('datetime_modified', 'datetime_created')
    fieldsets = [
        (None, {'fields': ['first_name', 'last_name',
            'email', 'unit', 'member', 'committee_excused', 'notes']}),
        ('Phone numbers(s)', {'fields': ['phone_numbers'], 'classes':
            ['collapse']}),
        ('Children', {'fields': ['children'], 'classes': ['collapse']}),
        ('Date information', {'fields': ['datetime_modified', 'datetime_created'],
            'classes': ['collapse']})
    ]
    list_display = ('last_name', 'first_name', 'address',
        'get_phone_numbers', 'email', 'member', 'get_committees')
    ordering = ('-member', 'last_name', 'first_name')
    filter_horizontal = ('children', 'phone_numbers')
    inlines = [MembershipInline, MovesInline]

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

class CommitteeAdmin(admin.ModelAdmin):

    list_display = ('name', 'chair', 'get_members')
    ordering = ('name',)
    filter_horizontal = ('members',)

    def get_members(self, obj):
        try:
            return u', '.join([unicode(m) for m in obj.members.order_by('last_name')])
        except:
            return ''

    get_members.short_description = "Members"

class MoveAdmin(admin.ModelAdmin):

    list_display = ('move_type', 'get_movers', 'move_date', 'in_unit', 'out_unit', 'notes')

    filter_horizontal = ('movers',)

    def get_movers(self, obj):
        return u', '.join(map(str, obj.movers.all()))
    get_movers.short_description = 'Movers'

class BlockRepresentativeAdmin(admin.ModelAdmin):

    list_display = ('get_role', 'person')
    ordering = ('role', 'block_number')

    def get_role(self, obj):
        return u'%s for block %s' % (obj.role, obj.block_number)
    get_role.short_description = 'Role'


admin.site.register(Person, PersonAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Committee, CommitteeAdmin)
admin.site.register(Move, MoveAdmin)
admin.site.register(BlockRepresentative, BlockRepresentativeAdmin)

