from rain.tracker.models import Torrent, TorrentAdmin, Peer, PeerAdmin
from django.contrib import admin
 
admin.site.register(Torrent, TorrentAdmin)
admin.site.register(Peer, PeerAdmin)