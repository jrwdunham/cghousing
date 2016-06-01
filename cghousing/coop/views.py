import os
import string
import magic
import json
import errno
import pprint
import subprocess
import re
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.http import Http404
from django.utils.timezone import now
from django.views.generic import ListView, DetailView, TemplateView, View
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import Form, ModelForm, CharField, Textarea, ModelChoiceField, ValidationError
from django.forms.widgets import HiddenInput
from django.db.models import Q
from coop.models import (
    Forum, Thread, Post, ApplicationSettings, Page, File, Person, UPLOADS_DIR,
    BlockRepresentative, Committee, PhoneNumber, Unit, Committee)

# TODO:
#
# - PostForm should not display reply_to when new post is first post in thread.
# - reply_to should not be optional in non-initial post.

################################################################################
# Global Template Context Stuff
################################################################################

# These are the pages that will be listed in the "Members only" section of the
# left sidebar.
# TODO: this information should be specified in the application settings model.
DYNAMIC_PAGES = (
    ('minutes', 'Minutes'),
    ('members', 'Members'),
    ('committees', 'Committees'),
    ('rules', 'Rules'),
    ('units', 'Units'),
    ('forums', 'Forums'),
    ('pages', 'Pages'),
    ('files', 'Files'),
)

LATEX_DIR = 'latex'

def get_global_context():
    """Return a context dict that all templates need. Includes the active
    application settings model, which specifies which pages are public.

    """

    app_settings = get_application_settings()
    try:
        public_page_ids = json.loads(app_settings.public_pages)
    except:
        public_page_ids = []
    pages = Page.objects.only('title', 'url_title')\
        .filter(id__in=public_page_ids)
    pages = dict((p.id, p) for p in pages)
    context = {
        'app_settings': app_settings,
        'coop_dynamic_pages': DYNAMIC_PAGES
    }
    for id_ in public_page_ids:
        page = pages.get(id_)
        if page:
            context.setdefault('coop_static_pages', [])\
                .append((page.url_title, page.title))
    return context


def get_application_settings():
    return ApplicationSettings.objects.last()


class LoginRequiredMixin(object):

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class GlobalContextMixin(View):
    """TODO: use this so that we don't have to un-DRY-ly call 
    `get_global_context()` all the time

    """

    def get_context_data(self, **kwargs):
        context = super(GlobalContextMixin, self).get_context_data(**kwargs)
        context.update(get_global_context())
        return context


################################################################################
# Co-op Static Page Views
################################################################################

def index_view(request):
    """Render the Co-op Home Page

    """

    return render(request, 'coop/index.html', get_global_context())


################################################################################
# Co-op Dynamic Page Views
################################################################################

# Forum-related Views, etc.
################################################################################

@login_required
def forums_view(request):
    """Display the collection of all forums at /forums.

    """

    forums = Forum.objects.order_by('name')
    forums = [get_forum_posts(forum) for forum in forums]
    forums = [get_forum_most_recent_post(forum) for forum in forums]
    forums = sorted(forums, key=lambda k: len(k.posts), reverse=True)
    forum_list, committee_forum_list = split_committee_forums(forums)
    context = {
        'forum_list': {
            'general_forums': forum_list,
            'committee_forums': committee_forum_list
            },
        'current_page': 'forums',
        'request': request
        }
    context.update(get_global_context())
    return render(request, 'coop/forum_list.html', context)


@login_required
def forum_view(request, pk):
    """Display a forum, given its primary key `pk`, e.g., /forum/37/.

    """

    forum = Forum.objects.get(pk=pk)
    return display_forum(request, forum)


@login_required
def forum_view_by_url_name(request, url_name):
    """Display a forum, given its `url_name`, e.g., /forum/classifieds/.

    """

    try:
        forum = Forum.objects.filter(url_name=url_name).first()
        if not forum:
            raise Http404("Forum does not exist")
        return display_forum(request, forum)
    except Forum.DoesNotExist:
        raise Http404("Forum does not exist")


def display_forum(request, forum):
    """Display the forum `forum`.

    """

    context = {'forum': forum}
    context.update(get_global_context())
    return render(request, 'coop/forum_detail.html', context)


@login_required
def forum_new(request):
    """Display page for creating a new forum, if you're a superuser.

    """

    if not request.user.is_superuser:
        return HttpResponseForbidden('Only administrators can create new forums.')
    form = ForumForm()
    context = {'form': form}
    context.update(get_global_context())
    return render(request, 'coop/forum_new.html', context)


@login_required
@require_POST
def forum_save(request):
    """Create a new forum, if you're a superuser.

    """

    if not request.user.is_superuser:
        return HttpResponseForbidden('Only administrators can create new forums.')
    form = ForumForm(request.POST)
    if form.is_valid():
        new_forum = Forum(**form.cleaned_data)
        new_forum.creator = new_forum.modifier = request.user
        new_forum.save()
        return HttpResponseRedirect(reverse('coop:forum',
            kwargs={'pk': new_forum.id}))
    else:
        context = {'form': form}
        context.update(get_global_context())
        return render(request, 'coop/forum_new.html', context)


# Thread-related Views, etc.
################################################################################

@login_required
def thread_view(request, url_name, pk):
    """View a thread, given the `url_name` of its forum and its `pk`,
    e.g., forum/classifieds/thread/2/.

    """

    try:
        thread = Thread.objects.get(pk=pk)
        return display_thread(request, thread)
    except:
        raise Http404("There is no thread with id %s in forum %s" % (
            pk, url_name))


@login_required
def thread_view_by_url_subject(request, url_name, url_subject):
    """View a thread, given the `url_name` of its forum and its `url_subject`,
    e.g., forum/classifieds/thread/couch-to-give-away/.

    """

    try:
        thread = Thread.objects.filter(url_subject=url_subject).first()
        if not thread:
            raise Http404("There is no thread %s in forum %s" % (
                url_subject, url_name))
        return display_thread(request, thread)
    except Thread.DoesNotExist:
        raise Http404("There is no thread %s in forum %s" % (
            url_subject, url_name))


@login_required
def thread_new_view(request, url_name):
    """Display the form for creating a new thread. Reachable at
    GET forum/<url_name>/thread/

    """

    forum = Forum.objects.filter(url_name=url_name).first()
    form = ThreadForm(forum)
    context = {'form': form, 'forum': forum}
    context.update(get_global_context())
    return render(request, 'coop/thread_new.html', context)


@login_required
@require_POST
def thread_save_view(request, url_name):
    """Create a new thread. POST request to forum/<url_name>/thread/save/.

    """

    forum = Forum.objects.filter(url_name=url_name).first()
    form = ThreadForm(forum, request.POST)
    if form.is_valid():
        new_thread = Thread(**form.cleaned_data)
        new_thread.creator = new_thread.modifier = request.user
        new_thread.save()
        return HttpResponseRedirect(reverse('coop:thread',
            kwargs={'url_name': forum.url_name, 'pk': new_thread.id}))
    else:
        context = {'form': form, 'forum': forum}
        context.update(get_global_context())
        return render(request, 'coop/thread_new.html', context)


def display_thread(request, thread):
    """Display `thread`. If HTTP method is POST, we are processing a request to
    add a post to a thread or we are updating an existing post on an existing
    thread.

    """

    context = {'thread': thread, 'errors': {}}
    context.update(get_global_context())
    if request.method == 'POST':
        return save_thread(request, thread, context)
    else:
        thread.views += 1
        thread.save()
        form = PostForm(thread=thread)
        form.fields['reply_to'].queryset = Post.objects.filter(thread=thread)
        context['post_form'] = form
        context['markdown_help_text'] = markdown_help_text
        return render(request, 'coop/thread_detail.html', context)


def save_thread(request, thread, context):
    """Save an existing thread, either by adding a post to it or by modifying
    one of its existing posts.

    """

    post_id = request.POST.get('id')
    if post_id:
        post = Post.objects.get(pk=post_id)
        form = PostForm(instance=post, data=request.POST, thread=thread)
    else:
        form = PostForm(request.POST, thread=thread)
    if form.is_valid():
        post = form.save(commit=False)
        post.thread = thread
        if post_id:
            post.modifier = request.user
        else:
            post.creator = post.modifier = request.user
        post.save()
        return HttpResponseRedirect(reverse('coop:thread',
            kwargs={'url_name': post.thread.forum.url_name,
                    'pk': post.thread.id}))
    else:
        form.fields['reply_to'].queryset = Post.objects.filter(thread=thread)
        context = get_global_context()
        if post_id:
            context.update({'thread': thread, 'form': form, 'post': post})
            return render(request, 'coop/post_edit.html', context)
        context.update({'thread': thread, 'post_form': form,
            'markdown_help_text': markdown_help_text})
        return render(request, 'coop/thread_detail.html', context)


# Post-related Views, etc.
################################################################################

@login_required
def post_edit_view(request, pk):
    """Display the form for editing an existing forum post.

    """

    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        raise Http404("There is no post with id %s" % pk)
    else:
        if post.creator != request.user:
            return HttpResponseForbidden('You are not authorized to edit this post')
        form = PostForm(instance=post, thread=post.thread)
        # TODO: can't the following line go in the `PostForm` constructor override?
        form.fields['reply_to'].queryset = Post.objects\
            .filter(thread=post.thread).filter(~Q(id=post.id))
        context = {'post': post, 'form': form}
        context.update(get_global_context())
        return render(request, 'coop/post_edit.html', context)


# File-related Views, etc.
################################################################################

@login_required
def files_view(request):
    """Display the collection of all files at /files.

    """

    files = File.objects.order_by('name')
    for file in files:
        file.path = os.path.split(str(file.upload))[1]
    context = {'files': files, 'request': request}
    context.update(get_global_context())
    return render(request, 'coop/file_list.html', context)


@login_required
def file_view(request, pk):
    """Display a file, given its primary key `pk`, e.g., /file/37/.

    """

    file = File.objects.get(pk=pk)
    context = {
        'file': file,
        'icon': FILE_FA_ICONS.get(file.type, 'file-o'),
        'path': os.path.split(str(file.upload))[1]
    }
    context.update(get_global_context())
    return render(request, 'coop/file_detail.html', context)


@login_required
def file_by_path_view(request, path):
    """Display a file, given its path, i.e., its name with spaces replaced by
    underscores.

    """

    full_path = os.path.join(UPLOADS_DIR, path)
    file = File.objects.filter(upload=full_path).first()
    context = {
        'file': file,
        'icon': FILE_FA_ICONS.get(file.type, 'file-o'),
        'path': path
    }
    context.update(get_global_context())
    return render(request, 'coop/file_detail.html', context)


def file_data_view(request, path):
    """Return the file data, i.e., serve the file. The `path` argument must be
    the value of file.upload minus the 'uploads' directory prefix. This is the
    name of the file with whitespace replaced by underscores.

    TODO: is this inefficient? Does it load the entire file into memory and/or
    should these files be served via Apache/Nginx instead of Django/Python?

    Note: add the following line in order to force a download/save-as of the
    file::

        >>> response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % (file.name)

    """

    try:
        path = os.path.join(UPLOADS_DIR, path)
        file = File.objects.filter(upload=path).first()
        if (not file.public) and (not request.user.is_authenticated()):
            return HttpResponseForbidden('Only co-op members can access that file')
        if os.path.isfile(path) and file:
            file_data = open(path, 'rb')
            response = HttpResponse(content=file_data)
            response['Content-Type']= file.type
            response['Content-Disposition'] = 'filename="%s.pdf"' % file.name
            return response
        else:
            raise Http404("There is no file at %s" % path)
    except File.DoesNotExist:
        raise Http404("There is no file at %s" % path)


@login_required
def file_new_view(request):
    """Display the form for uploading a new file at /file.

    """

    form = FileForm()
    context = {'form': form}
    context.update(get_global_context())
    return render(request, 'coop/file_new.html', context)


@login_required
def file_edit_view(request, pk):
    """Display the form for editing an existing file.

    """

    try:
        file = File.objects.get(pk=pk)
    except File.DoesNotExist:
        raise Http404("There is no file with id %s" % pk)
    else:
        if (not request.user.is_superuser) and file.creator != request.user:
            return HttpResponseForbidden('You are not authorized to edit this'
                ' file')
        form = FileEditForm(instance=file)
        icon = FILE_FA_ICONS.get(file.type, 'file-o')
        file.path = os.path.split(str(file.upload))[1]
        context = {'form': form, 'file': file, 'icon': icon}
        context.update(get_global_context())
        return render(request, 'coop/file_edit.html', context)


@login_required
@require_POST
def file_save_view(request):
    """Handle a POST request to create a new file, i.e., upload it, or edit an
    existing one.

    """

    file_id = request.POST.get('id')
    if file_id:
        file = File.objects.get(pk=file_id)
        form = FileEditForm(instance=file, data=request.POST)
    else:
        form = FileForm(request.POST, request.FILES)
    if form.is_valid():
        if file_id:
            updated_file = form.save(commit=False)
            updated_file.modifier = request.user
            updated_file.save()
            return HttpResponseRedirect(reverse('coop:file',
                kwargs={'pk': updated_file.id}))
        else:
            new_file = File(**form.cleaned_data)
            new_file.creator = new_file.modifier = request.user
            new_file.save()
            return HttpResponseRedirect(reverse('coop:file',
                kwargs={'pk': new_file.id}))
    else:
        if file_id:
            icon = FILE_FA_ICONS.get(file.type, 'file-o')
            file.path = os.path.split(str(file.upload))[1]
            context = {'form': form, 'file': file, 'icon': icon}
            context.update(get_global_context())
            return render(request, 'coop/file_edit.html', context)
        context = {'form': form}
        context.update(get_global_context())
        return render(request, 'coop/file_new.html', context)


# Member-related Views, etc.
################################################################################

@login_required
def members_view(request):
    """Display the members page. This displays information about the current
    members of the co-op.

    """

    members = [fix_member(m) for m in
        Person.objects.order_by('last_name').filter(member=True)]
    context = {'members': members, 'request': request, 'current_page': 'members'}
    context.update(get_global_context())
    return render(request, 'coop/members.html', context)


@login_required
def members_pdf_view(request):
    """Create and serve a PDF file that shows the members of the co-op.

    """

    members = Person.objects.filter(member=True).all()
    path = generate_membership_list_pdf(members)
    print 'path to pdf file: %s' % path
    if path:
        file_data = open(path, 'rb')
        response = HttpResponse(content=file_data)
        response['Content-Type']= 'application/pdf'
        response['Content-Disposition'] = 'filename="%s.pdf"' % file.name
        return response
    else:
        return HttpResponseRedirect(reverse('coop:members'))


@login_required
def member_by_full_name_view(request, full_name):
    """Display the page for the member, based on their full name, where
    `full_name` is their last name, followed by an underscore, followed by
    their first name, e.g., "Doe_Jane" or "Doe-Smith_Mary-Jane".

    """

    try:
        last_name, first_name = full_name.split('_')
    except ValueError:
        raise Http404("There is no member matching %s" % full_name)
    member = Person.objects\
        .filter(member=True)\
        .filter(first_name=first_name)\
        .filter(last_name=last_name)\
        .first()
    if not member:
        raise Http404("There is no member matching %s" % full_name)
    context = {'member': fix_member(member)}
    context.update(get_global_context())
    return render(request, 'coop/person_detail.html', context)


@login_required
def member_edit_view(request, pk):
    """Display a form for editing a member. Only superusers should be able to
    edit members. A member can edit his/her own member model. However, they
    should not be able to modify certain attributes.

    """

    try:
        member = Person.objects.filter(member=True).get(pk=pk)
    except Person.DoesNotExist:
        raise Http404("There is no member with id %s" % pk)
    else:
        if ((not request.user.is_superuser) and member.user.id != request.user.id):
            return HttpResponseForbidden('You are not authorized to edit this'
                ' member')
        form = PersonForm(instance=member)
        context = {'form': form, 'member': member, 'markdown_help_text':
                markdown_help_text}
        context.update(get_global_context())
        return render(request, 'coop/member_edit.html', context)


@login_required
@require_POST
def member_save_view(request):
    """Handle a POST request to update an existing member.

    """

    member_id = int(request.POST.get('id'))
    try:
        member = Person.objects.filter(member=True).get(pk=member_id)
    except Person.DoesNotExist:
        raise Http404("There is no member with id %s" % member_id)
    form = PersonForm(instance=member, data=request.POST)
    if form.is_valid():
        updated_member = form.save(commit=False)
        updated_member.modifier = request.user
        updated_member.save()
        form.save_m2m()
        return HttpResponseRedirect(reverse('coop:member_by_full_name',
            kwargs={'full_name': '%s_%s' % (updated_member.last_name,
                updated_member.first_name)}))
    else:
        context = {'form': form, 'member': member, 'markdown_help_text':
                markdown_help_text}
        context.update(get_global_context())
        return render(request, 'coop/member_edit.html', context)


def fix_member(member):
    """Add attributes to the member (`Person` instance) so that it is more
    easily displayable in a template.

    TODO: this functionality should probably be in the `Person` model.

    TODO: link each committee name to the page for that committee.

    """

    committees = []
    for c in member.committees.all():
        if c.name != 'Co-op':
            if c.chair and c.chair.id == member.id:
                committees.append('%s (chair)' % c.name)
            else:
                committees.append(c.name)
    member.formatted_committees = ', '.join(committees)

    member.formatted_children = ', '.join(
        c.first_name for c in member.children.all())

    phone_nos = []
    for p in member.phone_numbers.all():
        if p.phone_type:
            phone_nos.append('%s (%s)' % (p.number, p.phone_type))
        else:
            phone_nos.append(p.number)
    member.phone_numbers_string = ', '.join(phone_nos)
    return member


def get_person_phone_numbers_string(person):
    phone_nos = []
    for p in person.phone_numbers.all():
        if p.phone_type:
            phone_nos.append('%s (%s)' % (p.number, p.phone_type))
        else:
            phone_nos.append(p.number)
    return ', '.join(phone_nos)


# Committee-related Views, etc.
################################################################################

@login_required
def committees_view(request):
    """Display the collection of all committees at /committees/.

    """

    committees = Committee.objects.order_by('name')
    for c in committees:
        c.formatted_members = get_formatted_members(c)
    context = {
        'committees': committees,
        'current_page': 'committees',
        'request': request
        }
    context.update(get_global_context())
    return render(request, 'coop/committee_list.html', context)


def get_formatted_members(committee):
    """Return a comma-delimited string of HTML links for each non-chair member
    in `committee`.

    """

    chair_id = None
    if committee.chair:
        chair_id = committee.chair.id
    members = []
    for member in committee.members.all():
        if member.id != chair_id:
            members.append(get_formatted_member(member))
    return ', '.join(members)


def get_formatted_member(member):
    """Return member as a link to that member's page.

    """

    url = reverse('coop:member_by_full_name',
        kwargs={'full_name': '%s_%s' % (member.last_name,
            member.first_name)})
    return '<a href="%s">%s %s</a>' % (url, member.first_name,
            member.last_name)


@login_required
@require_POST
def committee_save_view(request):
    """Handle a POST request to update an existing committee.

    """

    committee_id = int(request.POST.get('id'))
    try:
        committee = Committee.objects.get(pk=committee_id)
    except Committee.DoesNotExist:
        raise Http404("There is no committee with id %s" % committee_id)
    if ((not request.user.is_superuser) and
        request.user.id not in [m.user.id for m in
        committee.members.all()]):
        return HttpResponseForbidden('You are not authorized to edit this'
                ' committee')
    form = CommitteeForm(instance=committee, data=request.POST)
    if form.is_valid():
        updated_committee = form.save(commit=False)
        updated_committee.modifier = request.user
        updated_committee.save()
        form.save_m2m()
        return HttpResponseRedirect(reverse('coop:committee_by_url_name',
            kwargs={'url_name': committee.url_name}))
    else:
        context = {'form': form, 'committee': committee, 'markdown_help_text':
                markdown_help_text}
        context.update(get_global_context())
        return render(request, 'coop/committee_edit.html', context)


@login_required
def committee_by_url_name_view(request, url_name):
    """Display a committee, given its `url_name`, e.g., /committee/finance/.

    """

    try:
        committee = Committee.objects.filter(url_name=url_name).first()
        if not committee:
            raise Http404("Committee %s does not exist" % url_name)
        committee.formatted_members = get_formatted_members(committee)
        committee.member_ids = [m.user.id for m in committee.members.all()]
        context = {'committee': committee}
        context.update(get_global_context())
        return render(request, 'coop/committee_detail.html', context)
    except Committee.DoesNotExist:
        raise Http404("Committee %s does not exist" % url_name)


@login_required
def committee_edit_view(request, pk):
    """Display a form for editing a committee. Only superusers and members of
    the given committee can edit it.

    """

    try:
        committee = Committee.objects.get(pk=pk)
    except Committee.DoesNotExist:
        raise Http404("There is no committee with id %s" % pk)
    else:
        if ((not request.user.is_superuser) and
            request.user.id not in [m.user.id for m in
            committee.members.all()]):
            return HttpResponseForbidden('You are not authorized to edit this'
                ' committee')
        form = CommitteeForm(instance=committee)
        members = Person.objects.filter(member=True).order_by('last_name',
            'first_name')
        form.fields['members'].queryset = members
        form.fields['chair'].queryset = members
        context = {'form': form, 'committee': committee, 'markdown_help_text':
                markdown_help_text}
        context.update(get_global_context())
        return render(request, 'coop/committee_edit.html', context)


# Unit-related Views, etc.
################################################################################

@login_required
def units_view(request):
    """Display the collection of all units at /units.

    """

    units = Unit.objects.order_by('block_number', 'unit_number')
    for unit in units:
        fo = []
        for o in unit.occupants.all():
            if o.member:
                url = reverse('coop:member_by_full_name',
                    kwargs={'full_name': '%s_%s' % (o.last_name, o.first_name)})
                fo.append('<a href="%s">%s %s</a>' % (url, o.first_name,
                    o.last_name))
            else:
                fo.append('%s %s' % (o.first_name, o.last_name))
        unit.formatted_occupants = ', '.join(fo)
    context = {
        'units': units,
        'current_page': 'units',
        'request': request
        }
    context.update(get_global_context())
    return render(request, 'coop/unit_list.html', context)


@login_required
def unit_by_block_unit_nos_view(request, block_unit_nos):
    """Display the page for the unit, based on its block number, followed by a
    hyphen, followed by its unit number.

    """

    try:
        block_number, unit_number = block_unit_nos.split('-')
    except ValueError:
        raise Http404("There is no unit matching %s" % block_unit_nos)
    unit = Unit.objects\
        .filter(block_number=block_number)\
        .filter(unit_number=unit_number)\
        .first()
    if not unit:
        raise Http404("There is no unit matching %s" % block_unit_nos)
    context = {'unit': unit}
    context.update(get_global_context())
    return render(request, 'coop/unit_detail.html', context)


# Page-related Views, etc.
################################################################################

@login_required
def pages_view(request):
    """Display the collection of all pages at /pages.

    """

    pages = Page.objects.order_by('title')
    context = {
        'pages': pages,
        'current_page': 'pages',
        'request': request
        }
    context.update(get_global_context())
    return render(request, 'coop/page_list.html', context)


@login_required
def page_new_view(request):
    """Display the form for creating a new page at /page.

    """

    form = PageForm()
    context = {'form': form,
        'markdown_help_text': markdown_help_text}
    context.update(get_global_context())
    return render(request, 'coop/page_new.html', context)


@login_required
def page_edit_view(request, pk):
    """Display the form for editing an existing page.

    """

    try:
        page = Page.objects.get(pk=pk)
    except Page.DoesNotExist:
        raise Http404("There is no page with id %s" % pk)
    else:
        if ((not request.user.is_superuser) and (not page.editable) and
            page.creator != request.user):
            return HttpResponseForbidden('You are not authorized to edit this'
                ' page')
        form = PageForm(instance=page)
        context = {'form': form, 'page': page,
            'markdown_help_text': markdown_help_text}
        context.update(get_global_context())
        return render(request, 'coop/page_edit.html', context)


@login_required
@require_POST
def page_save_view(request):
    """Handle a POST request to create a new page or update an existing one.

    """

    page_id = request.POST.get('id')
    if page_id:
        page = Page.objects.get(pk=page_id)
        form = PageForm(instance=page, data=request.POST)
    else:
        form = PageForm(request.POST)
    if form.is_valid():
        if page_id:
            updated_page = form.save(commit=False)
            updated_page.url_title = form.cleaned_data['url_title']
            updated_page.modifier = request.user
            updated_page.save()
            return HttpResponseRedirect(reverse('coop:page',
                kwargs={'pk': updated_page.id}))
        else:
            new_page = Page(**form.cleaned_data)
            new_page.creator = new_page.modifier = request.user
            new_page.save()
            return HttpResponseRedirect(reverse('coop:page',
                kwargs={'pk': new_page.id}))
    else:
        if page_id:
            context = {'form': form, 'page': page,
                'markdown_help_text': markdown_help_text}
            context.update(get_global_context())
            return render(request, 'coop/page_edit.html', context)
        context = {'form': form,
            'markdown_help_text': markdown_help_text}
        context.update(get_global_context())
        return render(request, 'coop/page_new.html', context)


def page_view(request, pk):
    """Display a page, given its primary key `pk`, e.g., /page/2/.

    """

    page = Page.objects.get(pk=pk)
    return display_page(request, page)


def page_view_by_url_title(request, url_title):
    """Display a page, given its `url_title`, e.g., /page/my-favourite-page/.

    """

    try:
        page = Page.objects.filter(url_title=url_title).first()
        if not page:
            raise Http404("Page %s does not exist" % url_title)
        return display_page(request, page)
    except Page.DoesNotExist:
        raise Http404("Page %s does not exist" % url_title)


def display_page(request, page):
    """Display the page `page`. Non-public pages require authentication.

    """

    if (not page.public) and (not request.user.is_authenticated()):
        context = {'next': reverse('coop:page_by_url_title',
            kwargs={'url_title': page.url_title})}
        context.update(get_global_context())
        return render(request, 'coop/login.html', context)
    context = {'page': page, 'current_page': page.url_title}
    context.update(get_global_context())
    return render(request, 'coop/page_detail.html', context)


@login_required
def minutes_view(request):
    """Display the minutes page, if there is one. "The" minutes page is the one
    whose title is "Minutes". URL path is /minutes/.

    """

    minutes_page = Page.objects.filter(title='Minutes').first()
    if minutes_page:
        return display_page(request, minutes_page)
    else:
        raise Http404("There is no minutes page")


@login_required
def rules_view(request):
    """Display the rules page, if there is one. "The" rules page is the one
    whose title is "Rules". URL path is /rules/.

    """

    rules_page = Page.objects.filter(title='Rules').first()
    if rules_page:
        return display_page(request, rules_page)
    else:
        raise Http404("There is no rules page")


# Phone Number-related views, etc.
################################################################################


@login_required
def phone_number_save_ajax_view(request):
    """Create a new phone number and return a JSON response.

    """

    payload = json.loads(request.body)
    form = PhoneNumberForm(payload)
    if form.is_valid():
        new_phone_number = PhoneNumber(**form.cleaned_data)
        new_phone_number.creator = new_phone_number.modifier = request.user
        new_phone_number.save()
        response_data = {
                'id': new_phone_number.id,
                'number': new_phone_number.number,
                'phone_type': new_phone_number.phone_type
                }
        return HttpResponse(json.dumps(response_data),
            content_type="application/json")
    else:
        return HttpResponse(json.dumps(form.errors),
            content_type="application/json")


# Authentication Views
################################################################################

def login_view(request):
    """Show the login form.

    """

    next_ = request.GET.get('next', reverse('coop:index'))
    context = {'next': next_}
    context.update(get_global_context())
    return render(request, 'coop/login.html', context)


def authenticate_view(request):
    """Handle the request from submitting the login form.

    """

    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            redirect_to = request.POST.get('next', reverse('coop:index'))
            return HttpResponseRedirect(redirect_to)
        else:
            messages.add_message(request, messages.INFO, 'Authentication failed.')
            return HttpResponseRedirect('/accounts/login/')
    else:
        messages.add_message(request, messages.INFO, 'Authentication failed.')
        return HttpResponseRedirect('/accounts/login/')


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('coop:index'))


################################################################################
# Forms
################################################################################

class ForumForm(ModelForm):
    """Form for creating new forums.

    """

    class Meta:
        model = Forum
        fields = ['name', 'description']

    def clean(self):
        cleaned_data = super(ForumForm, self).clean()
        url_name = name2url(cleaned_data.get('name', ''))
        existing_forum = Forum.objects.filter(url_name=url_name).first()
        if existing_forum:
            raise ValidationError('The name %(name)s is too similar to an'
                ' existing name', params={'name': cleaned_data['name']},
                code='invalid')
        cleaned_data['url_name'] = url_name
        return cleaned_data


class ThreadForm(ModelForm):
    """Form for creating new threads.

    """

    def __init__(self, forum, *args, **kwargs):
        self.forum = forum
        return super(ThreadForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Thread
        fields = ['subject']

    def clean(self):
        cleaned_data = super(ThreadForm, self).clean()
        url_subject = name2url(cleaned_data.get('subject', ''))
        existing_thread = Thread.objects.filter(forum__id=self.forum.id)\
            .filter(url_subject=url_subject).first()
        if existing_thread:
            raise ValidationError('The subject %(subject)s is too similar to an'
            ' existing one', params={'subject': cleaned_data['subject']},
            code='invalid')
        cleaned_data['url_subject'] = url_subject
        cleaned_data['forum'] = self.forum
        return cleaned_data


class PostForm(ModelForm):
    """Form for creating new posts.

    """

    class Meta:
        model = Post
        fields = ['reply_to', 'subject', 'post']

    def __init__(self, *args, **kwargs):
        thread = kwargs['thread']
        del kwargs['thread']
        super(PostForm, self).__init__(*args, **kwargs)
        posts = thread.posts.all()
        if (not posts) or (self.instance == posts[0]):
            self.fields["reply_to"].widget = HiddenInput()

ALLOWED_FILE_TYPES = (
    'application/pdf',
    'image/gif',
    'image/png',
    'image/jpeg',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpointtd',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'audio/vorbis',
    'application/ogg',
    'audio/wav',
    'audio/x-wav',
    'audio/mpeg'
)

FILE_FA_ICONS = {
    'application/pdf': 'file-pdf-o',
    'image/gif': 'file-image-o',
    'image/png': 'file-image-o',
    'image/jpeg': 'file-image-o',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        'file-word-o',
    'application/msword': 'file-word-o',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        'file-excel-o',
    'application/ms-excel': 'file-excel-o',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation':
        'file-powerpoint-o',
    'application/ms-powerpointtd': 'file-powerpoint-o',
    'audio/vorbis': 'file-audio-o',
    'application/ogg': 'file-audio-o',
    'audio/wav': 'file-audio-o',
    'audio/x-wav': 'file-audio-o',
    'audio/mpeg': 'file-audio-o',
}

class FileForm(ModelForm):
    """Form for creating new files.

    """

    class Meta:
        model = File
        fields = ['upload', 'description', 'public']

    def clean(self):
        cleaned_data = super(FileForm, self).clean()
        upload = cleaned_data.get('upload', '')
        if not upload:
            raise ValidationError('Please choose a file for upload',
                code='invalid')
        try:
            type_ = magic.Magic(mime=True).from_file(
                upload.temporary_file_path())
        except AttributeError:
            type_ = magic.Magic(mime=True).from_buffer(upload.read())
        if type_ not in ALLOWED_FILE_TYPES:
            raise ValidationError('Files of type %(type)s cannot be uploaded',
                params={'type': type_}, code='invalid')
        if upload.size > 20000000:
            raise ValidationError('That file is too big. 20 MB is the limit',
                code='invalid')
        cleaned_data['type'] = type_
        cleaned_data['size'] = upload.size
        cleaned_data['name'] = upload.name
        return cleaned_data


class FileEditForm(ModelForm):
    """Form for editing existing files.

    """

    class Meta:
        model = File
        fields = ['description', 'public']


class PageForm(ModelForm):
    """Form for creating new pages.

    """

    class Meta:
        model = Page
        fields = ['title', 'content', 'public', 'editable']

    def clean(self):
        cleaned_data = super(PageForm, self).clean()
        title = cleaned_data.get('title', '')
        url_title = name2url(title)
        existing_page = Page.objects.filter(url_title=url_title).first()
        if (existing_page and
            getattr(self.instance, 'id', None) != existing_page.id):
            raise ValidationError('The title %(title)s is too similar to an'
            ' existing one', params={'title': cleaned_data['title']},
            code='invalid')
        cleaned_data['url_title'] = url_title
        return cleaned_data


class PersonForm(ModelForm):
    """Form for creating new people.

    """

    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'email', 'phone_numbers',
                'children', 'page_content']

        # The template uses this to trigger opening of an Ajax-based form in a
        # modal dialog.
        help_texts = {'phone_numbers': ('<a href="javascript:void(0)"'
            ' class="new-number"><i class="fa fa-plus"></i>&nbsp;New'
            ' Number</a>.')}


class PhoneNumberForm(ModelForm):
    """Form for creating new phone numbers.

    """

    class Meta:
        model = PhoneNumber
        fields = ['number', 'phone_type']


class CommitteeForm(ModelForm):
    """Form for editing committees.

    """

    class Meta:
        model = Committee
        fields = ['chair', 'members', 'description', 'page_content']


################################################################################
# Helpers
################################################################################


def split_committee_forums(forums):
    """Given a list of forum models in `forums`, return a tuple containing 2
    lists: one for general forums and one for committee-specific forums.

    """

    general_forums = []
    committee_forums = []
    for forum in forums:
        try:
            tmp = forum.committee
            committee_forums.append(forum)
        except:
            general_forums.append(forum)
    return (general_forums, committee_forums)


def get_forum_posts(forum):
    """Return all of the posts in the forum `forum`.

    """

    forum.posts = [post for thread in forum.threads.all()
        for post in thread.posts.all()]
    return forum


def get_forum_most_recent_post(forum):
    """Return the most recent post in `forum`.

    """

    posts = sorted(forum.posts, key=lambda p: p.datetime_created, reverse=True)
    try:
        forum.most_recent_post = posts[0]
    except IndexError:
        forum.most_recent_post = None
    return forum


def name2url(name):
    """Convert string `name` to a string that only contains ASCII letters,
    digits and the hyphen. The result is usable as a URL path.

    """

    valid_chars = "- %s%s" % (string.ascii_letters, string.digits)
    url = ''.join(c for c in name if c in valid_chars)
    url = url.replace(' ', '-').lower()
    return url


################################################################################
#  General Utilities
################################################################################


def make_directory_safely(path):
    """Create a directory and avoid race conditions.
    http://stackoverflow.com/questions/273192/python-best-way-to-create-directory-if-it-doesnt-exist-for-file-write.

    """

    try:
        os.makedirs(path)
    except OSError, exception:
        if exception.errno != errno.EEXIST:
            raise


################################################################################
#  Utilities for Generating the Membership List PDF
################################################################################


def generate_membership_list_pdf(members):
    """Use LaTeX to generate a PDF encoding the members, their roles, and their
    contact information.

    """

    make_directory_safely(LATEX_DIR)
    subdir = 'latex-%s' % now().strftime('%Y-%m-%d')
    subpath = os.path.join(LATEX_DIR, subdir)
    make_directory_safely(subpath)
    filename = 'membership-distribution-list-%s' % now().strftime('%Y-%m-%d')
    latex_fname = '%s.tex' % filename
    pdf_fname = '%s.pdf' % filename
    latex_fpath = os.path.join(subpath, latex_fname)
    pdf_fpath = os.path.join(subpath, pdf_fname)
    with open(latex_fpath, 'w') as f:
        f.write(get_latex_membership_doc(members))
    cwd = os.path.join(os.getcwd(), subpath)
    process = subprocess.Popen(['pdflatex', latex_fname], shell=False,
            stdout=subprocess.PIPE, cwd=cwd)
    output = process.communicate()[0]
    if os.path.isfile(pdf_fpath):
        return pdf_fpath
    else:
        return None


def get_latex_membership_doc(members):
    """Return a LaTeX (.tex) document representing a "Membership List". This is
    a series of tables, one for each block (i.e., address) in the co-op

    """

    blocks = get_blocks_dict_for_latex_membership_doc(members)
    block_reps = BlockRepresentative.objects.all()
    participation_chair = get_participation_chair()
    for block_no, block in blocks.items():
        latex_rows = []
        for unit_no, occupants in block['units'].items():
            latex_rows.append(get_latex_occupants_row(unit_no, occupants))
        block['member_rows'] = '\n'.join(latex_rows)
        block['maintenance_rep'] = get_maintenance_rep(block_no, block_reps)
        block['roof_monitor'] = get_roof_monitor(block_no, block_reps)
        block['participation_chair'] = participation_chair
    latex_membership_blocks = '\n\n'.join(get_latex_membership_block_table(
            block_no, blocks[block_no]) for block_no in sorted(blocks.keys()))

    return r'''
\documentclass{article}
\usepackage[a4paper,margin=0.5in,landscape]{geometry}
\usepackage{tabularx}
\usepackage{hhline}
\begin{document}

\setlength\tabcolsep{2.5pt}

%s

\end{document}
''' % latex_membership_blocks


def get_blocks_dict_for_latex_membership_doc(members):
    """Return a dict representing the blocks in the co-op. Keys are block
    numbers, i.e., street addresses. Values are dicts representing each block.
    Each block has a `unit` key whose value is a dict that maps unit numbers to
    lists of persons, i.e., members.

    """

    blocks = {}
    app_settings = get_application_settings()
    coop_name = getattr(app_settings, 'coop_name', 'Co-op')
    date = now().strftime('%B %d, %Y')
    for member in members:
        member_block = member.unit.block_number
        block = blocks.get(member_block)
        if not block:
            block = {
                'coop_name': coop_name,
                'date': date,
                'maintenance_rep': '',
                'roof_monitor': '',
                'participation_chair': '',
                'units': {}
                }
        block['units'].setdefault(member.unit.unit_number, []).append(member)
        if not blocks.get(member_block):
            blocks[member_block] = block
    return blocks


def get_latex_occupants_row(unit_no, occupants):
    """Return a latex {tabular} row to represent the occupants of a given unit.
    This is a row with the following columns:

        1. Unit #
        2. Members
        3. Children
        4. Phone #
        5. E-mail Address
        6. Committee
        7. Chair

    """

    members = get_members_for_latex_row(occupants)
    children = get_children_for_latex_row(occupants)
    phone_nos = get_phone_nos_for_latex_row(occupants)
    emails = get_emails_for_latex_row(occupants)
    committees, chairships = get_cmtes_chrs_for_latex_row(occupants)
    return (r'%s & %s & %s & %s & %s & \scriptsize {\scshape %s} & \scriptsize'
            r' {\scshape %s} \\ \hline' % (
                unit_no,
                tex_escape(members),
                tex_escape(children),
                tex_escape(phone_nos),
                tex_escape(emails),
                tex_escape(committees),
                tex_escape(chairships))
        )


def get_members_for_latex_row(occupants):
    """Return a string representing the members in `occupants`, a list of persons in a unit.

    """

    if len(set(p.last_name for p in occupants)) == 1:
        return '%s, %s' % (occupants[0].last_name, ' & '.join(p.first_name
            for p in occupants))
    else:
        return ' & '.join('%s, %s' % (p.last_name, p.first_name) for p in
            occupants)


def get_children_for_latex_row(occupants):
    """Return a string representing the children in `occupants`, a list of
    persons in a given unit.

    """

    children = set()
    for person in occupants:
        for child in person.children.all():
            children.add(child)
    children = list(children)
    if len(children) == 0:
        return ''
    elif len(children) == 1:
        return children[0].first_name
    elif len(children) == 2:
        return ' & '.join(c.first_name for c in children)
    else:
        return '%s & %s' % (', '.join(c.first_name for c in children[:-1]),
                children[-1].first_name)


def get_phone_nos_for_latex_row(occupants):
    """Return a string representing the phone numbers of `occupants`, a list of
    persons in a given unit.

    """

    phone_nos_tmp = {}
    for person in occupants:
        for phone_no in person.phone_numbers.all():
            phone_nos_tmp.setdefault(phone_no.number, {})
            phone_nos_tmp[phone_no.number]['type'] = phone_no.phone_type
            phone_nos_tmp[phone_no.number].setdefault('owner',
                []).append(person.first_name)
    phone_nos = []
    for number, meta in phone_nos_tmp.items():
        if meta['type']:
            if len(meta['owner']) != len(occupants):
                phone_nos.append('%s~(%s, %s)' % (
                    number, meta['type'], ' & '.join(meta['owner'])))
            else:
                phone_nos.append('%s~(%s)' % (number, meta['type']))
        else:
            if len(meta['owner']) != len(occupants):
                phone_nos.append('%s~(%s)' % (
                    number, ' & '.join(meta['owner'])))
            else:
                phone_nos.append('%s' % (number,))
    return ', '.join(phone_nos)


def get_emails_for_latex_row(occupants):
    """Return a string representing the emails of `occupants`, a list of
    persons in a given unit.

    """

    emails = list(set(p.email for p in occupants))
    if len(emails) == 1:
        return emails[0]
    else:
        return ', '.join('%s (%s)' % (p.email, p.first_name) for p in occupants
                if p.email)


def get_cmtes_chrs_for_latex_row(occupants):
    """Return a 2-tuple of strings representing the committees and chairships
    of `occupants`, a list of persons in a given unit.

    """

    committees = []
    chairships = []
    if len(occupants) == 1:
        if occupants[0].committee_excused:
            committees.append('excused by board')
        for committee in occupants[0].committees.all():
            if committee.name != 'Co-op':
                committees.append('%s' % committee.name)
            if committee.chair and committee.chair.id == occupants[0].id:
                chairships.append('Yes-%s' % committee.name)
    else:
        for person in occupants:
            if person.committee_excused:
                committees.append('excused by board (%s)' % person.first_name)
            for committee in person.committees.all():
                if committee.name != 'Co-op':
                    committees.append('%s (%s)' % (committee.name,
                        person.first_name))
                if committee.chair and committee.chair.id == person.id:
                    chairships.append('Yes-%s-%s' % (committee.name,
                        person.first_name))
    return (' / '.join(committees).lower(), ', '.join(chairships).lower())


def get_maintenance_rep(block_no, block_reps):
    """Return the maintenance representative for block `block_no`, if
    exists. Return as '<First Name> <Last Name> - <Phone Number>'.

    """

    try:
        rep = [r for r in block_reps if r.block_number == block_no and
                r.role == 'maintenance'][0].person
    except IndexError:
        return 'POSITION AVAILABLE'
    else:
        if rep:
            return '%s %s - %s' % (rep.first_name, rep.last_name,
                get_person_phone_numbers_string(rep))
        else:
            return 'POSITION AVAILABLE'


def get_roof_monitor(block_no, block_reps):
    """Return the roof monitor for block `block_no`, if
    exists. Return as '<First Name> <Last Name> - <Phone Number>'.

    """

    try:
        rep = [r for r in block_reps if r.block_number == block_no and
                r.role == 'roof monitor'][0].person
    except IndexError:
        return 'POSITION AVAILABLE'
    else:
        if rep:
            return '%s %s - %s' % (rep.first_name, rep.last_name,
                get_person_phone_numbers_string(rep))
        else:
            return 'POSITION AVAILABLE'


def get_participation_chair():
    """Return the chair of the participation committee, if exists. Return as
    '<First Name> <Last Name> <Address> or <Email>'.

    """

    participation_cmte = Committee.objects.filter(name='Participation').first()
    if participation_cmte:
        if participation_cmte.chair:
            return '%s %s #%s - %s or %s' % (
                participation_cmte.chair.first_name,
                participation_cmte.chair.last_name,
                participation_cmte.chair.unit.unit_number,
                participation_cmte.chair.unit.block_number,
                participation_cmte.chair.email)
        else:
            return 'There is no participation committee chair'
    else:
        return 'There is no participation committee chair'


def get_latex_membership_block_table(block_no, block):
    """Return a chunk of LaTeX representing all of the units/members in the
    block (i.e., address) represented by `block_no` and the dict `block`.

    """

    return (r'''
{\centering
  \large
  \textbf{
  %s Membership List \\
  Block: %s} \par
}

\normalsize

%%\vspace{0.5cm}

\begin{flushright}
\footnotesize
%s
\small
\end{flushright}

{\renewcommand{\arraystretch}{1.5}
\begin{tabularx}{\textwidth}{|c|X|l|X|X|X|c|}
    \hline
    %%\hhline{|=|=|=|=|=|=|=|}
    \textbf{UNIT \#} & \textbf{MEMBERS} & \textbf{CHILDREN} & \textbf{PHONE \#} & \textbf{E-MAIL ADDRESS} & \textbf{COMMITTEE} & \textbf{CHAIR} \\
    \hline
    %s
    %%\hhline{|=|=|=|=|=|=|=|}
\end{tabularx}
}

\vspace{0.5cm}

\footnotesize

\textbf{
{\renewcommand{\arraystretch}{1.15}
\begin{tabular}{ll}
    MAINTENANCE FOR BLOCK %s: & \underline{%s} \\
    ROOF MONITOR FOR BLOCK %s: & \underline{%s} \\
    & \\
    \multicolumn{2}{l}{\footnotesize***To make changes to this list or submit excuse notes (i.e., missing a meeting), please contact:***\small} \\
    PARTICIPATION COMMITTEE: & \underline{%s} \\
\end{tabular}
}}

\normalsize
\newpage
''' % (
        tex_escape(block['coop_name']),
        block_no,
        block['date'],
        block['member_rows'],
        block_no,
        tex_escape(block['maintenance_rep']),
        block_no,
        tex_escape(block['roof_monitor']),
        tex_escape(block['participation_chair'])
        )).strip()


# Map LaTeX special characters to their escaped counterparts.
latex_conv = {
    '&': r'\&',
    '%': r'\%',
    '$': r'\$',
    '#': r'\#',
    '_': r'\_',
    '{': r'\{',
    '}': r'\}',
    #'~': r'\textasciitilde{}',
    '^': r'\^{}',
    '\\': r'\textbackslash{}',
    '<': r'\textless',
    '>': r'\textgreater',
}


# Regex for replacing LaTeX special characters with their escaped counterparts.
latex_regex = re.compile('|'.join(re.escape(unicode(key)) for key in
    sorted(latex_conv.keys(), key = lambda item: - len(item))))


def tex_escape(text):
    """Return `text` with its LaTeX special characters escaped.

    """

    return latex_regex.sub(lambda match: latex_conv[match.group()], text)


markdown_help_text = '''
    <h1>How to Use
      <a href="https://daringfireball.net/projects/markdown/">Markdown</a></h1>

    <p>Markdown is a very simple language for adding links, images and
    formatting to your web pages.</p>

    <h2>Links</h2>
    <p>To create links to co-op-internal pages, like the <a
         href="/members/">Members Page</a>, or to external pages, like <a
         href="https://www.google.com/">Google</a>, use the following
       syntax.</p>
    <pre><code>[Members Page](/members/)</code>
<code>[Google](https://www.google.com/)</code></pre>

    <h2>Images</h2>
    <p>To embed images, do the following.</p>
    <pre><code>![](/path/to/img.jpg)</code></pre>
    <p>In the above, <code>/path/to/img.jpg</code> is
    the path to the image that you want to display in your page. Use the URL
    value of files that you upload to the co-op web site for the path.</p>
    <p>Your images can also have values for <code>alt text</code>, which is
    text that represents the image for users who can't see it, and
    <code>"Title"</code>, which is the help text that pops up
    when your mouse is over the image.</p>
    <pre><code>![alt text](/path/to/img.jpg "Title")</code></pre>

    <h2>Paragraphs</h2>
    <p>Any chunk of text separated from other chunks by a blank line, will be a
    paragraph.</p>
    <pre><code>I will be the first paragraph.

I will be the second paragraph. I have more words than the first.</code></pre>

    <h2>Headers</h2>
    <p>Section headers, from biggest to smallest, are as follows.</p>
    <pre><code># Biggest Header
## Second Biggest Header
### Third Biggest Header
#### Third Smallest Header
##### Second Smallest Header
###### Smallest Header</code></pre>

    <h2>Bold and Italics</h2>
    <p>Enclose portions of text in <code>*</code> or <code>**</code> to make
    them italicized or bolded, respectively.</p>
    <pre><code>*I will be italicized*
**I will be bolded**</code></pre>

    <h2>Unordered Lists</h2>
    <p>You can use <code>-</code>, <code>+</code> or <code>*</code> to create
    unordered lists.</p>
    <pre><code>- apples
- bananas
- celery</code></pre>

    <pre><code>* John
* Paul
* Ringo
* George</code></pre>

    <h2>Ordered Lists</h2>
    <p>You can use numerals to create ordered lists.</p>
    <pre><code>1. Wash dishes.
2. Rinse dishes.
3. Dry dishes.</code></pre>

    <h2>More ...</h2>
    <p>For more help with Markdown, see the <a
         href="https://daringfireball.net/projects/markdown/">Markdown web
         site</a>.</p>
'''.strip()
