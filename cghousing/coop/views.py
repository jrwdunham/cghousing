import string
import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
#from django.core.exceptions import RelatedObjectDoesNotExist
from django.template import RequestContext, loader
from django.http import Http404
from django.views.generic import ListView, DetailView, TemplateView, View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.forms import Form, ModelForm, CharField, Textarea, ModelChoiceField

from coop.models import Forum, Thread, Post, ApplicationSettings, Page

################################################################################
# Global Template Context Stuff
################################################################################

# Return a context dict that all templates need.
# Includes the active application settings model.
def get_global_context():
    app_settings = get_application_settings()
    try:
        public_page_ids = json.loads(app_settings.public_pages)
    except:
        public_page_ids = []
    pages = Page.objects.only('title', 'url_title').filter(id__in=public_page_ids)
    pages = dict((p.id, p) for p in pages)

    context = {
        'app_settings': app_settings,
        'coop_dynamic_pages': (
            ('forums', 'Forums'),
        )
    }
    for id_ in public_page_ids:
        page = pages.get(id_)
        if page:
            context.setdefault('coop_static_pages', []).append((page.url_title, page.title))
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

# View a forum
@login_required
def forums_view(request):
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
        'current_page': 'forums'}
    context.update(get_global_context())
    return render(request, 'coop/forum_list.html', context)

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



# View a thread, given its url-subject in the URL.
def thread_view_by_url_subject(request, url_name, url_subject):
    try:
        thread = Thread.objects.filter(url_subject=url_subject).first()
        if not thread:
            raise Http404("Thread does not exist")
        return return_thread(request, thread)
    except Thread.DoesNotExist:
        raise Http404("Thread does not exist")


# GET /thread/pk displays thread;
# POST /thread/pk handles submission of form for adding a post to a thread.
def thread_detail(request, pk):
    try:
        thread = Thread.objects.get(pk=pk)
        return return_thread(request, thread)
    except:
        raise Http404("Thread does not exist")


def return_thread(request, thread):
    context = {'thread': thread, 'errors': {}}
    context.update(get_global_context())
    if request.method == 'POST':
        new_post = None
        try:
            params = {
                'reply_to': Post.objects.get(pk=request.POST['reply_to']),
                'thread': Thread.objects.get(pk=request.POST['thread']),
                'subject': request.POST['subject'],
                'post': request.POST['post']
            }
            for key, val in params.items():
                if not val:
                    context['errors'].setdefault(key, []).append(
                        'This field is required.')
            if context['errors']:
                context['attempted_post'] = params
            else:
                new_post = Post(**params)
                new_post.save()
        except Exception as e:
            print e
        finally:
            return render(request, 'coop/thread_detail.html', context)
    else:
        thread.views += 1
        thread.save()
        return render(request, 'coop/thread_detail.html', context)


# View a forum after creation
class ForumResultsView(GlobalContextMixin, DetailView):
    model = Forum
    template_name = 'coop/results.html'


# Display page for creating a new forum.
@login_required
def forum_new(request):
    return render(request, 'coop/forum_new.html')


def post_save(request):
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

def get_post_save_next(request, new_post):
    next_ = request.POST.get('next')
    if next_:
        if new_post:
            return '%s#%s' % (next_, new_post.id)
        else:
            return next_
    else:
        return reverse('coop:forums')

def forum_save(request):
    try:
        new_forum = Forum(
            name=request.POST['name'],
            description=request.POST['description'],
        )
        new_forum.save()
    except:
        # Redisplay the forum creation form.
        # TODO: put input data back in.
        return render(request, 'coop/forum_new.html', {
            'error_message': "There was an erorr: could not create forum."
        })
    else:
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('coop:forum_results', args=(new_forum.id,)))


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
            return HttpResponse('you suck')
    else:
        return HttpResponse('you REALLY suck')


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
