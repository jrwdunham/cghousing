from django.conf.urls import patterns, url
from coop import views


urlpatterns = patterns('',
    # ex: /coop/
    url(r'^$', views.index, name='index'),

    # ex: /coop/forums/
    url(r'^forums/$', views.ForumsView.as_view(), name='forums'),

    # ex: /coop/forum/5/
    url(r'^forum/(?P<pk>\d+)/$', views.ForumView.as_view(), name='forum'),

    # ex: /coop/forum/5/results
    url(r'^forum/(?P<pk>\d+)/results/$', views.ForumResultsView.as_view(), name='forum_results'),

    # ex: /coop/forum/
    url(r'^forum/$', views.forum_new, name='forum_new'),

    # ex: /coop/forum/
    url(r'^forum/save$', views.forum_save, name='forum_save'),

)
