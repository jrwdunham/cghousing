from django.conf.urls import patterns, url
from coop import views


urlpatterns = patterns('',
    # e.g., /coop/
    url(r'^$', views.index_view, name='index'),
    url(r'^welcome$', views.index_view, name='welcome'),

    url(r'^page/(?P<url_title>[-\w\d]+)/$', views.page_view_by_url_title,
        name='page_by_url_title'),

    # forums
    url(r'^forums/$', views.forums_view, name='forums'),
    url(r'^forum/(?P<pk>\d+)/$', views.forum_view, name='forum'),
    url(r'^forum/(?P<url_name>[-\w\d]+)/$', views.forum_view_by_url_name,
        name='forum_by_url_name'),
    url(r'^forum/(?P<pk>\d+)/results/$', views.ForumResultsView.as_view(),
        name='forum_results'),
    url(r'^forum/$', views.forum_new, name='forum_new'),
    url(r'^forum/save$', views.forum_save, name='forum_save'),

    # threads
    url(r'^forum/(?P<url_name>[-\w\d]+)/thread/(?P<pk>\d+)/$',
        views.thread_detail, name='thread'),
    url(r'^forum/(?P<url_name>[-\w\d]+)/thread/(?P<url_subject>[-\w\d]+)/$',
        views.thread_view_by_url_subject, name='thread_view_by_url_subject'),
    url(r'^forum/(?P<url_name>[-\w\d]+)/thread/$', views.thread_new,
        name='thread_new'),
    url(r'^forum/(?P<url_name>[-\w\d]+)/thread/save$', views.thread_save,
        name='thread_save'),

    # posts
    url(r'^post/save$', views.post_save, name='post_save'), # e.g., /post/save

    # Authentication
    url(r'^accounts/login/$', views.show_login_form, name='login'),
    url(r'^accounts/logout/$', views.logout_view, name='logout'),
    url(r'^accounts/authenticate/$', views.handle_authenticate_request,
        name='authenticate')

)

