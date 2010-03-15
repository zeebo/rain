from django.conf.urls.defaults import *
from django.http import HttpResponse

urlpatterns = patterns('',
  (r'^$', lambda x: HttpResponse('niy')),
  (r'^upload/$', 'rain.torrents.views.upload_torrent'),
  (r'^(?P<torrent_id>\d+)/$', lambda x, torrent_id: HttpResponse('niy')),
  (r'^(?P<torrent_id>\d+)/download$', lambda x, torrent_id: HttpResponse('niy')),
)
