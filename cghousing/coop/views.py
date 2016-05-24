import string
import json
import pprint

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
#from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext, loader
from django.http import Http404
from django.views.generic import ListView, DetailView, TemplateView, View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import Form, ModelForm, CharField, Textarea, ModelChoiceField, ValidationError

from coop.models import Forum, Thread, Post, ApplicationSettings, Page

################################################################################
# Global Template Context Stuff
################################################################################

def get_global_context():
    """Return a context dict that all templates need. Includes the active
    application settings model.

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

    def get_context_data(self, **kwargs):
        context = super(GlobalContextMixin, self).get_context_data(**kwargs)
        context.update(get_global_context())
        return context



################################################################################
# Co-op Static Page Views
################################################################################


# Co-op Home Page
def index_view(request):
    context = get_global_context()
    return render(request, 'coop/index.html', context)



################################################################################
# Co-op Dynamic Page Views
################################################################################

@login_required
def forums_view(request):
    """Display the list of forums at /forums

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
def pages_view(request):
    pages = Page.objects.order_by('title')
    context = {
        'pages': pages,
        'current_page': 'pages',
        'request': request
        }
    context.update(get_global_context())
    return render(request, 'coop/page_list.html', context)


# Input: list of forum models; output: 2-tuple of forum models.
def split_committee_forums(forums):
    general_forums = []
    committee_forums = []
    for forum in forums:
        try:
            tmp = forum.committee
            committee_forums.append(forum)
        except:
            general_forums.append(forum)
    return (general_forums, committee_forums)

# Get all the posts in a forum.
def get_forum_posts(forum):
    forum.posts = [post for thread in forum.threads.all()
        for post in thread.posts.all()]
    return forum

def get_forum_most_recent_post(forum):
    posts = sorted(forum.posts, key=lambda p: p.datetime_created, reverse=True)
    try:
        forum.most_recent_post = posts[0]
    except IndexError:
        forum.most_recent_post = None
    return forum

def name2url(name):
    valid_chars = "- %s%s" % (string.ascii_letters, string.digits)
    url = ''.join(c for c in name if c in valid_chars)
    url = url.replace(' ','-').lower()
    return url


################################################################################
# Forum view logic.
################################################################################

# View a forum.
def return_forum(request, forum):
    context = {'forum': forum}
    context.update(get_global_context())
    return render(request, 'coop/forum_detail.html', context)

# View a forum, given its primary key.
def forum_view(request, pk):
    forum = Forum.objects.get(pk=pk)
    return return_forum(request, forum)

# View a forum, given its url-name in the URL.
def forum_view_by_url_name(request, url_name):
    try:
        forum = Forum.objects.filter(url_name=url_name).first()
        if not forum:
            raise Http404("Forum does not exist")
        return return_forum(request, forum)
    except Forum.DoesNotExist:
        raise Http404("Forum does not exist")


################################################################################
# Page view logic.
################################################################################

# View a page.
def return_page(request, page):
    context = {'page': page, 'current_page': page.url_title}
    context.update(get_global_context())
    return render(request, 'coop/page_detail.html', context)

# View a page, given its utl-title in the URL.
def page_view_by_url_title(request, url_title):
    try:
        page = Page.objects.filter(url_title=url_title).first()
        if not page:
            raise Http404("Page does not exist")
        return return_page(request, page)
    except Page.DoesNotExist:
        raise Http404("Page does not exist")

# View a page, given its primary key.
def page_view(request, pk):
    page = Page.objects.get(pk=pk)
    return return_page(request, page)


@login_required
def minutes_view(request):
    """Display the minutes page, if there is one.

    url(r'^minutes/$', views.minutes_vew, name='minutes'),

    """

    minutes_page = Page.objects.filter(title='Minutes').first()
    if minutes_page:
        return return_page(request, minutes_page)
    else:
        raise Http404("There is no minutes page")




def thread_view_by_url_subject(request, url_name, url_subject):
    """View a thread, given its url-subject in the URL.

    """

    try:
        thread = Thread.objects.filter(url_subject=url_subject).first()
        if not thread:
            raise Http404("Thread does not exist")
        return return_thread(request, thread)
    except Thread.DoesNotExist:
        raise Http404("Thread does not exist")


# GET /thread/pk displays thread;
# POST /thread/pk handles submission of form for adding a post to a thread.
def thread_detail(request, url_name, pk):
    """View a thread, given its primary key `pk`. Note: `url_name` belongs to
    the forum that the thread belongs to.

    """

    try:
        thread = Thread.objects.get(pk=pk)
        return return_thread(request, thread)
    except:
        raise Http404("Thread does not exist")


@login_required
def thread_new(request, url_name):
    """Display page for creating a new thread.

    """

    forum = Forum.objects.filter(url_name=url_name).first()
    form = ThreadForm(forum)
    context = {'form': form, 'forum': forum}
    context.update(get_global_context())
    return render(request, 'coop/thread_new.html', context)


def thread_save(request, url_name):
    """Create a new thread.

    """

    if request.method == 'POST':
        forum = Forum.objects.filter(url_name=url_name).first()
        form = ThreadForm(forum, request.POST)
        if form.is_valid():
            new_thread = Thread(**form.cleaned_data)
            new_thread.save()
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            return HttpResponseRedirect(reverse('coop:thread',
                kwargs={'url_name': forum.url_name, 'pk': new_thread.id}))
        else:
            context = {'form': form, 'forum': forum}
            context.update(get_global_context())
            return render(request, 'coop/thread_new.html', context)


def return_thread(request, thread):
    context = {'thread': thread, 'errors': {}}
    context.update(get_global_context())
    if request.method == 'POST':
        post_id = request.POST.get('id')
        if post_id:
            post = Post.objects.get(pk=post_id)
        try:
            reply_to = request.POST.get('reply_to')
            if reply_to:
                reply_to = Post.objects.get(pk=reply_to)
            params = {
                'reply_to': reply_to,
                'thread': Thread.objects.get(pk=request.POST['thread']),
                'subject': request.POST['subject'],
                'post': request.POST['post']
            }
            for key, val in params.items():
                if key != 'reply_to' and not val:
                    context['errors'].setdefault(key, []).append(
                        'This field is required.')
            if context['errors']:
                context['attempted_post'] = params
            else:
                if post_id:
                    post.modifier = request.user
                    post.reply_to = params['reply_to']
                    post.subject = params['subject']
                    post.post = params['post']
                else:
                    post = Post(**params)
                    post.creator = post.modifier = request.user
                post.save()
                # Always return an HttpResponseRedirect after successfully dealing
                # with POST data. This prevents data from being posted twice if a
                # user hits the Back button.
                return HttpResponseRedirect(reverse('coop:thread',
                    kwargs={
                        'url_name': post.thread.forum.url_name,
                        'pk': post.thread.id}))
        except Exception as e:
            print 'got an exception'
            print e
        finally:
            if post_id and context.get('errors'):
                context['post'] = post
                return render(request, 'coop/post_edit.html', context)
            else:
                return render(request, 'coop/thread_detail.html', context)
    else:
        thread.views += 1
        thread.save()
        return render(request, 'coop/thread_detail.html', context)


# View a forum after creation
class ForumResultsView(GlobalContextMixin, DetailView):
    model = Forum
    template_name = 'coop/results.html'


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


@login_required
def forum_new(request):
    """Display page for creating a new forum.

    """

    form = ForumForm()
    context = {'form': form}
    context.update(get_global_context())
    return render(request, 'coop/forum_new.html', context)


def forum_save(request):
    """Create a new forum.

    """

    if request.method == 'POST':
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


def forum_save_DEPRECATED(request):
    """Create a new forum.

    """

    try:
        name = request.POST['name']
        url_name = name2url(name)
        new_forum = Forum(
            name=name,
            url_name=url_name,
            description=request.POST['description'],
        )
        new_forum.save()
    except:
        # Redisplay the forum creation form.
        # TODO: put input data back in.
        return render(request, 'coop/forum_new.html', {
            'error_message': "There was an error: could not create forum.",
            'forum': new_forum
        })
    else:
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('coop:forum_results', args=(new_forum.id,)))


def post_save(request):
    """TODO: is this function ever called? Check and destroy if not.

    """

    new_post = None
    try:
        reply_to = Post.objects.get(pk=request.POST['reply_to'])
        thread = Thread.objects.get(pk=request.POST['thread'])
        new_post = Post(
            subject=request.POST['subject'],
            post=request.POST['post'],
            reply_to=reply_to,
            thread=thread
        )
        new_post.save()
    except Exception as e:
        print e
    finally:
        next_ = get_post_save_next(request, new_post)
        return HttpResponseRedirect(next_)


def post_edit(request, pk):
    """Display the form for editing an existing forum post.

    """

    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        raise Http404("Post does not exist")
    else:
        context = {'post': post}
        context.update(get_global_context())
        return render(request, 'coop/post_edit.html', context)


def get_post_save_next(request, new_post):
    next_ = request.POST.get('next')
    if next_:
        if new_post:
            return '%s#%s' % (next_, new_post.id)
        else:
            return next_
    else:
        return reverse('coop:forums')


# Show the login form
def show_login_form(request):
    next_ = request.GET.get('next', reverse('coop:index'))
    context = {'next': next_}
    context.update(get_global_context())
    return render(request, 'coop/login.html', context)


# Handle the request from submitting the login form.
def handle_authenticate_request(request):
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

def about_us(request):
    return HttpResponse('about us')

def housing_fees(request):
    return HttpResponse('housing fees')

def about_area(request):
    return HttpResponse('about area')

def amenities(request):
    return HttpResponse('amenities')

def contact_us(request):
    return HttpResponse('contact us')
