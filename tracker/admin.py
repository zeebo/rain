from rain.tracker.models import Torrent, Peer
from tracker.forms import UploadTorrentForm
from django.contrib import admin
from django import forms

class ReadOnlyWidget(forms.Widget):
  def __init__(self, original_value, display_value):
    self.original_value = original_value
    self.display_value = display_value
    
    super(ReadOnlyWidget, self).__init__()
  
  def render(self, name, value, attrs=None):
    if self.display_value is not None:
      return unicode(self.display_value)
    return unicode(self.original_value)
  
  def value_from_datadict(self, data, files, name):
    return self.original_value

class ReadOnlyModelAdmin(admin.ModelAdmin):
  def get_form(self, request, obj=None, **kwargs):
    form = super(ReadOnlyModelAdmin, self).get_form(request, obj)
    #return form
    #Force read only in edit mode
    if obj is not None:
      for field_name in form.base_fields:
        if hasattr(obj, 'get_%s_display' % field_name):
          display_value = getattr(obj, 'get_%s_display' % field_name)()
        else:
          display_value = None
      
        form.base_fields[field_name].widget = ReadOnlyWidget(getattr(obj, field_name, ''), display_value)
        form.base_fields[field_name].required = False
    
    return form

class TorrentAdmin(ReadOnlyModelAdmin):
  #form = UploadTorrentForm
  list_display = ('info_hash', 'uploaded_by', 'num_seeds', 'num_peers', 'downloaded')

class PeerAdmin(ReadOnlyModelAdmin):
  list_display = ('torrent', 'peer_id', 'ip_port', 'key', 'state', 'last_announce', 'active')

admin.site.register(Torrent, TorrentAdmin)
admin.site.register(Peer, PeerAdmin)