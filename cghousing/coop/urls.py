from django.conf.urls import patterns, url
from coop import views


urlpatterns = patterns('',

    url(r'^$', views.index_view, name='index'),
    url(r'^welcome$', views.index_view, name='welcome'),

    # Members
    url(r'^members/$', views.members_view, name='members'),
    url(r'^members-pdf/$', views.members_pdf_view, name='members_pdf'),
    url(r'^member/save/$', views.member_save_view, name='member_save'),
    url(r'^member/(?P<pk>\d+)/change-password/$',
        views.member_change_password_view, name='member_change_password'),
    url(r'^member/(?P<full_name>[-_\w\d]+)/$', views.member_by_full_name_view,
        name='member_by_full_name'),
    url(r'^member/(?P<pk>\d+)/edit/$', views.member_edit_view,
        name='member_edit'),

    # Phone Numbers
    url(r'^phonenumber/save/ajax$', views.phone_number_save_ajax_view,
        name='phone_number_save_ajax'),

    # Pages
    url(r'^pages/$', views.pages_view, name='pages'),
    url(r'^page/$', views.page_new_view, name='page_new'),
    url(r'^page/save/$', views.page_save_view, name='page_save'),
    url(r'^page/(?P<pk>\d+)/$', views.page_view, name='page'),
    url(r'^page/(?P<url_title>[-\w\d]+)/$', views.page_view_by_url_title,
        name='page_by_url_title'),
    url(r'^page/(?P<pk>\d+)/edit/$', views.page_edit_view, name='page_edit'),
    url(r'^minutes/$', views.minutes_view, name='minutes'),
    url(r'^rules/$', views.rules_view, name='rules'),

    # Units
    url(r'^units/$', views.units_view, name='units'),
    url(r'^unit/(?P<block_unit_nos>[-\d]+)/$',
        views.unit_by_block_unit_nos_view, name='unit_by_block_unit_nos'),

    # Committees
    url(r'^committees/$', views.committees_view, name='committees'),
    url(r'^committee/save/$', views.committee_save_view, name='committee_save'),
    url(r'^committee/(?P<url_name>[-\w\d]+)/$',
        views.committee_by_url_name_view, name='committee_by_url_name'),
    url(r'^committee/(?P<pk>\d+)/edit/$', views.committee_edit_view,
        name='committee_edit'),

    # Files
    url(r'^files/$', views.files_view, name='files'),
    url(r'^file/(?P<pk>\d+)/$', views.file_view, name='file'),
    url(r'^file/(?P<path>[^ /]+)/$', views.file_by_path_view, name='file_by_path'),
    url(r'^file/$', views.file_new_view, name='file_new'),
    url(r'^file/save$', views.file_save_view, name='file_save'),
    url(r'^file/data/(?P<path>[^ ]+)/$$', views.file_data_view,
        name='file_data'),
    url(r'^file/(?P<pk>\d+)/edit/$', views.file_edit_view, name='file_edit'),

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

