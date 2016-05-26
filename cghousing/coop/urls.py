from django.conf.urls import patterns, url
from coop import views


urlpatterns = patterns('',

    url(r'^$', views.index_view, name='index'),
    url(r'^welcome$', views.index_view, name='welcome'),

    # Pages
    url(r'^pages/$', views.pages_view, name='pages'),
    url(r'^page/(?P<pk>\d+)/$', views.page_view, name='page'),
    url(r'^page/(?P<url_title>[-\w\d]+)/$', views.page_view_by_url_title,
        name='page_by_url_title'),
    url(r'^minutes/$', views.minutes_view, name='minutes'),

    # Forums
    url(r'^forums/$', views.forums_view, name='forums'),
    url(r'^forum/(?P<pk>\d+)/$', views.forum_view, name='forum'),
    url(r'^forum/(?P<url_name>[-\w\d]+)/$', views.forum_view_by_url_name,
        name='forum_by_url_name'),
    url(r'^forum/$', views.forum_new, name='forum_new'),
    url(r'^forum/save$', views.forum_save, name='forum_save'),

    # Threads
    url(r'^forum/(?P<url_name>[-\w\d]+)/thread/(?P<pk>\d+)/$',
        views.thread_view, name='thread'),
    url(r'^forum/(?P<url_name>[-\w\d]+)/thread/(?P<url_subject>[-\w\d]+)/$',
        views.thread_view_by_url_subject, name='thread_view_by_url_subject'),
    url(r'^forum/(?P<url_name>[-\w\d]+)/thread/$', views.thread_new_view,
        name='thread_new'),
    url(r'^forum/(?P<url_name>[-\w\d]+)/thread/save$', views.thread_save_view,
        name='thread_save'),

    # Posts
    url(r'^post/(?P<pk>\d+)/edit/$', views.post_edit_view, name='post_edit'),

    # Authentication
    url(r'^accounts/login/$', views.login_view, name='login'),
    url(r'^accounts/logout/$', views.logout_view, name='logout'),
    url(r'^accounts/authenticate/$', views.authenticate_view,
        name='authenticate')

)

