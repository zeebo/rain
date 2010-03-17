from django.contrib import admin
from rain.tracker.models import Peer
from rain.tracker.forms import PeerForm
from rain.admin import ReadOnlyModelAdmin

class PeerAdmin(ReadOnlyModelAdmin):
  form = PeerForm
  list_display = ('info_hash', 'peer_id', 'username', 'key', 'state', 'last_announce', 'active')

admin.site.register(Peer, PeerAdmin)