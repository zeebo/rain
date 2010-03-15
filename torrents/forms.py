from django.contrib.auth.models import User
from rain.torrents.models import Torrent
from rain.torrents.utils import bencode, bdecode
from rain.settings import SECRET_KEY
from django import forms
import hashlib
import os

class UploadTorrentBaseForm(forms.ModelForm):  
  def clean_torrent(self):
    torrent = self.cleaned_data["torrent"]
    
    # Check that the torrent is actually a torrent file and set the info_hash
    _, ext = os.path.splitext(torrent.name)
    if ext != '.torrent':
      raise forms.ValidationError('File must end with .torrent')
    
    try:
      data = bdecode(torrent.read())
    except ValueError:
      raise forms.ValidationError('Problem parsing torrent file')
    if 'info' not in data:
      raise forms.ValidationError('Info dict not in torrent file')
    
    #Verify uniqueness
    the_hash = hashlib.sha1(bencode(data['info'])).hexdigest()
    if Torrent.objects.filter(info_hash=the_hash).count() != 0:
      raise forms.ValidationError('Torrent already exists [%s]' % the_hash)
    
    #encode the name
    torrent.name = '%s.torrent' % hashlib.sha1(the_hash + SECRET_KEY).hexdigest()
    
    return torrent

class UploadTorrentForm(UploadTorrentBaseForm):
  class Meta:
    model = Torrent
    fields = ("torrent",)

class UploadTorrentAdminForm(UploadTorrentBaseForm):
  class Meta:
    model = Torrent