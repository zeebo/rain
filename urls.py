from django.conf.urls.defaults import *
from django.contrib import admin
from rain.tracker.views import announce, scrape, upload_torrent
from rain.settings import MEDIA_ROOT
admin.autodiscover()

tracker_views = patterns('rain.tracker.views',
  (r'announce$', 'announce'),
  (r'scrape$', 'scrape'),
  (r'upload_torrent$', 'upload_torrent'),
)

urlpatterns = patterns('',
  (r'^admin/', include(admin.site.urls)),
  (r'^tracker/', include(tracker_views)),
  (r'^accounts/login/$', 'django.contrib.auth.views.login'),
  (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
  (r'^accounts/register/$', 'invite_registration.registration_view'),
  #(r'^tracker/media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}), #probably security vuln but ok for now.
)
