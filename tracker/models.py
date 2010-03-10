from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from rain.utils import bencode, bdecode
from rain.settings import SECRET_KEY, MAGIC_VALUES
import os, hashlib, datetime

class Torrent(models.Model):
  torrent = models.FileField(upload_to='torrents')
  uploaded_by = models.ForeignKey(User)
  info_hash = models.CharField(max_length=40, editable=False, unique=True)
  downloaded = models.IntegerField(default=0)
  
  def num_seeds(self):
    return current_peers().filter(torrent=self).filter(state=MAGIC_VALUES['seed']).count()
  
  def num_peers(self):
    return current_peers().filter(torrent=self).filter(state=MAGIC_VALUES['peer']).count()
  
  def increment_downloaded(self):
    self.downloaded += 1
    self.save()
  
  def clean(self):
    from django.core.exceptions import ValidationError
    
    # Check that the torrent is actually a torrent file and set the info_hash
    _, ext = os.path.splitext(self.torrent.name)
    if ext != '.torrent':
      raise ValidationError('File must end with .torrent')
    try:
      data = bdecode(self.torrent.read())
    except ValueError:
      raise ValidationError('Problem parsing torrent file')
    if 'info' not in data:
      raise ValidationError('Info dict not in torrent file')
    
    #Verify uniqueness
    the_hash = hashlib.sha1(bencode(data['info'])).digest().encode('hex')
    torrents_with_hash = Torrent.objects.filter(info_hash=the_hash)
    if len(torrents_with_hash) != 0 and torrents_with_hash[0].pk != self.pk:
      raise ValidationError('Torrent already exists [%s]' % the_hash)
    
    self.torrent.name = "%s.torrent" % hashlib.sha1(the_hash + SECRET_KEY).digest().encode('hex')
    self.info_hash = the_hash

class TorrentAdmin(admin.ModelAdmin):
  list_display = ('info_hash', 'uploaded_by', 'num_seeds', 'num_peers', 'downloaded')

class Peer(models.Model):
  STATE_CHOICES = (
    (MAGIC_VALUES['peer'], 'Peer'),
    (MAGIC_VALUES['seed'], 'Seed'),
  )
  torrent = models.ForeignKey(Torrent)
  peer_id = models.CharField(max_length=20)
  port = models.IntegerField()
  ip = models.IPAddressField()
  key = models.CharField(max_length=100) #spec does not specify data type on key
  state = models.CharField(max_length=1, choices=STATE_CHOICES)
  supportcrypto = models.BooleanField(default=True) #currently unused
  
  last_announce = models.DateTimeField(auto_now=True)
  
  def ip_port(self):
    return "%s:%s" % (self.ip, self.port)
  
  def active(self):
    delta = datetime.timedelta(seconds=MAGIC_VALUES['time_until_inactive']) #30 minutes
    return self.last_announce >= datetime.datetime.now() - delta
  
  def inactive(self):
    return not self.active()
  

def current_peers():
  delta = datetime.timedelta(seconds=MAGIC_VALUES['time_until_inactive']) #30 minutes
  return Peer.objects.filter(last_announce__range=(datetime.datetime.now() - delta, datetime.datetime.now()))

class PeerAdmin(admin.ModelAdmin):
  list_display = ('torrent', 'peer_id', 'ip_port', 'key', 'state', 'last_announce', 'active')