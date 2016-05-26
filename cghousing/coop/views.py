import string
import json
import pprint
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.http import Http404
from django.views.generic import ListView, DetailView, TemplateView, View
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import Form, ModelForm, CharField, Textarea, ModelChoiceField, ValidationError
from django.forms.widgets import HiddenInput
from django.db.models import Q
from coop.models import Forum, Thread, Post, ApplicationSettings, Page

# TODO:
#
# - 403 Unauthorized response: needs something visual (just a blank screen
#   right now)

################################################################################
# Global Template Context Stuff
################################################################################

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
        'coop_dynamic_pages': (
            ('minutes', 'Minutes'),
            ('forums', 'Forums'),
            ('pages', 'Pages'),
        )
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
        new_forum.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
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
        context.update({'thread': thread, 'post_form': form})
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
    url = url.replace(' ','-').lower()
    return url

