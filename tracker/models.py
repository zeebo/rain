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
  
  def __unicode__(self):
    return self.info_hash
  
  def num_seeds(self):
    return current_peers().filter(torrent=self).filter(state=MAGIC_VALUES['seed']).count()
  
  def num_peers(self):
    return current_peers().filter(torrent=self).filter(state=MAGIC_VALUES['peer']).count()
  
  def increment_downloaded(self):
    self.downloaded += 1
    self.save()
  
  def save(self, *args, **kwargs):
    data = bdecode(self.torrent.read())
    self.info_hash = hashlib.sha1(bencode(data['info'])).digest().encode('hex')
    
    super(Torrent, self).save(*args, **kwargs)

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
    delta = datetime.timedelta(seconds=MAGIC_VALUES['time_until_inactive'])
    return self.last_announce >= datetime.datetime.now() - delta
  
  def inactive(self):
    return not self.active()
  

def current_peers():
  delta = datetime.timedelta(seconds=MAGIC_VALUES['time_until_inactive'])
  return Peer.objects.filter(last_announce__range=(datetime.datetime.now() - delta, datetime.datetime.now()))