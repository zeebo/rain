from django.conf.urls.defaults import *
from django.contrib import admin
from django.http import HttpResponse
from rain.settings import MEDIA_ROOT
admin.autodiscover()

torrent_patterns = patterns('',
  (r'^$', 'list'),
  (r'^(?P<torrent_id>\d+)/$', 'view'),
  (r'^(?P<torrent_id>\d+)/download$', 'dl_somehow'),
)

urlpatterns = patterns('',
  (r'^admin/', include(admin.site.urls)),
  (r'^tracker/', include('rain.tracker.urls')),
  (r'^accounts/login/$', 'django.contrib.auth.views.login'),
  (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
  (r'^accounts/register/$', 'invite_registration.views.registration_view'),
  (r'^torrents/', include(torrent_patterns)),
  (r'^users/(?P<username>.*)$', lambda x: HttpResponse()), 
  #(r'^tracker/media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}), #probably security vuln but ok for now.
)
