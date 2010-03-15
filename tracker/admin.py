from rain.tracker.models import Peer, UserIP, RatioInfo, UserRatio
from rain.tracker.forms import PeerForm
from rain.admin import ReadOnlyModelAdmin

class PeerAdmin(ReadOnlyModelAdmin):
  form = PeerForm
  list_display = ('torrent', 'peer_id', 'username', 'ip_port', 'key', 'state', 'last_announce', 'active')

class UserIPAdmin(admin.ModelAdmin):
  list_display = ('user', 'ip')

class RatioInfoAdmin(ReadOnlyModelAdmin):
  list_display = ('user', 'torrent', 'download_size', 'upload_size', 'ratio')

class UserRatioAdmin(admin.ModelAdmin):
  list_display = ('user', 'download_size', 'upload_size', 'ratio')

admin.site.register(UserIP, UserIPAdmin)
admin.site.register(RatioInfo, RatioInfoAdmin)
admin.site.register(UserRatio, UserRatioAdmin)
admin.site.register(Peer, PeerAdmin)