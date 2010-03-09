from rain.tracker.models import Torrent, TorrentAdmin
from django.contrib import admin
 
admin.site.register(Torrent, TorrentAdmin)