from django.conf.urls.defaults import *
from django.http import HttpResponse
from models import Torrent

info_dict = {
  'queryset': Torrent.objects.all(),
}

urlpatterns = patterns('',
  (r'^$', 'rain.torrents.views.torrent_list', info_dict),
  (r'^upload/$', 'rain.torrents.views.upload_torrent'),
  (r'^(?P<object_id>\d+)/$', 'rain.torrents.views.torrent_detail', info_dict),
  (r'^(?P<torrent_id>\d+)/download$', lambda x, torrent_id: HttpResponse('niy')),
)
