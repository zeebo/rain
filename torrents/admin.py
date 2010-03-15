from rain.torrents.forms import UploadTorrentAdminForm
from rain.admin import ReadOnlyModelAdmin
from rain.torrents.models import Torrent
from django.contrib import admin

class TorrentAdmin(ReadOnlyModelAdmin):
  form = UploadTorrentAdminForm
  list_display = ('info_hash', 'uploaded_by', 'downloaded', 'description')
  editable_fields = ('uploaded_by', 'downloaded', 'description')

admin.site.register(Torrent, TorrentAdmin)