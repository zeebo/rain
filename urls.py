from django.conf.urls.defaults import *
from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
  (r'^$', lambda x: HttpResponseRedirect('torrents/')),
  (r'^admin/', include(admin.site.urls)),
  (r'^tracker/', include('rain.tracker.urls')),
  (r'^users/', include('rain.user_profiles.urls')),
  (r'^accounts/login/$', 'django.contrib.auth.views.login'),
  (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
  (r'^accounts/register/$', 'invite_registration.views.registration_view'),
  (r'^torrents/', include('rain.torrents.urls')),
  (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}), #probably security vuln but ok for now.
)
