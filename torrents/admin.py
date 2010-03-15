from rain.torrents.forms import UploadTorrentAdminForm
from rain.admin import ReadOnlyModelAdmin

class TorrentAdmin(ReadOnlyModelAdmin):
  form = UploadTorrentAdminForm
  list_display = ('info_hash', 'uploaded_by', 'num_seeds', 'num_peers', 'downloaded')
  editable_fields = ('uploaded_by', 'downloaded')

admin.site.register(Torrent, TorrentAdmin)