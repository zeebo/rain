from rain.tracker.models import Torrent, Peer
from tracker.forms import UploadTorrentForm, PeerForm
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
    form = super(ReadOnlyModelAdmin, self).get_form(request, obj, **kwargs)
    
    if obj is not None:
      for field_name in form.base_fields:
        # field with 'choices' attribute
        if hasattr(obj, 'get_%s_display' % field_name):
          original_value = getattr(obj, field_name, '')
          display_value = getattr(obj, 'get_%s_display' % field_name )()
        # ForeignKey or ManyToManyField
        elif hasattr(obj, '%s_id' % field_name):
          original_value = getattr(obj, "%s_id" % field_name, '')
          display_value = getattr(obj, field_name, '')
        # other field type
        else:
          original_value = getattr(obj, field_name, '')
          display_value = getattr(obj, field_name, '')
      
        form.base_fields[field_name].widget = ReadOnlyWidget(original_value, display_value)
        form.base_fields[field_name].required = False
      
    return form


class TorrentAdmin(ReadOnlyModelAdmin):
  list_display = ('info_hash', 'uploaded_by', 'num_seeds', 'num_peers', 'downloaded')

class PeerAdmin(ReadOnlyModelAdmin):
  form = PeerForm
  list_display = ('torrent', 'peer_id', 'ip_port', 'key', 'state', 'last_announce', 'active')

admin.site.register(Torrent, TorrentAdmin)
admin.site.register(Peer, PeerAdmin)