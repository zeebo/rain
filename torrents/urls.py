from django.conf.urls.defaults import *
from django.http import HttpResponse
from models import Torrent

info_dict = {
  'queryset': Torrent.objects.all(),
}

urlpatterns = patterns('',
  (r'^$', 'torrents.views.torrent_list', info_dict),
  (r'^upload/$', 'torrents.views.upload_torrent'),
  (r'^(?P<object_id>\d+)/$', 'torrents.views.torrent_detail', info_dict),
  url(r'^(?P<object_id>\d+)/download$', lambda x, object_id: HttpResponse('niy'), name='download_torrent'),
)
