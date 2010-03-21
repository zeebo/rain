from django.conf.urls.defaults import *
from django.http import HttpResponse
from models import Torrent

info_dict = {
  'queryset': Torrent.objects.all(),
}

urlpatterns = patterns('torrents.views',
  (r'^$', 'torrent_list', info_dict),
  (r'^upload/$', 'upload_torrent'),
  (r'^(?P<object_id>\d+)/$', 'torrent_detail', info_dict),
  url(r'^(?P<object_id>\d+)/download$', 'download_torrent', name='download_torrent'),
)
