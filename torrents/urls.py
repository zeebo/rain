from django.conf.urls.defaults import *
from django.http return HttpResponse

urlpatterns = patterns('',
  (r'^$', lambda x: HttpResponse('niy')),
  (r'^(?P<torrent_id>\d+)/$', lambda x: HttpResponse('niy')),
  (r'^(?P<torrent_id>\d+)/download$', lambda x: HttpResponse('niy')),
)
