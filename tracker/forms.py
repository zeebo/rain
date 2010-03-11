from django import forms
from tracker.models import Torrent
from utils import bencode, bdecode
import hashlib
import os

class UploadTorrentForm(forms.ModelForm):
  torrent = forms.FileField(label="Torrent")
  
  class Meta:
    model = Torrent
    fields = ("torrent",)

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
    the_hash = hashlib.sha1(bencode(data['info'])).digest().encode('hex')
    if Torrent.objects.filter(info_hash=the_hash).count() != 0:
      raise forms.ValidationError('Torrent already exists [%s]' % the_hash)
    
    return torrent