from django.conf.urls import patterns, include, url
from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    url(r'^coop/', include('coop.urls', namespace='coop')),
    url(r'^admin/', include(admin.site.urls)),
)
