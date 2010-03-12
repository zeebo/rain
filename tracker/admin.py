from rain.tracker.models import Torrent, Peer
from tracker.forms import UploadTorrentForm, PeerForm
from django.contrib import admin
from django import forms

class TorrentAdmin(admin.ModelAdmin):
  form = UploadTorrentForm
  list_display = ('info_hash', 'uploaded_by', 'num_seeds', 'num_peers', 'downloaded')

class PeerAdmin(admin.ModelAdmin):
  form = PeerForm
  list_display = ('torrent', 'peer_id', 'ip_port', 'key', 'state', 'last_announce', 'active')

admin.site.register(Torrent, TorrentAdmin)
admin.site.register(Peer, PeerAdmin)