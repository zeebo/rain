from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from rain.settings import SECRET_KEY, MAGIC_VALUES
from django.core.exceptions import ValidationError
from rain.torrents.models import Torrent
import os, hashlib, datetime, logging

class Peer(models.Model):
  STATE_CHOICES = (
    (MAGIC_VALUES['peer'], 'Peer'),
    (MAGIC_VALUES['seed'], 'Seed'),
  )
  torrent = models.ForeignKey(Torrent)
  peer_id = models.CharField(max_length=20)
  port = models.IntegerField()
  key = models.CharField(max_length=100, blank=True, null=True) #spec does not specify data type on key
  state = models.CharField(max_length=1, choices=STATE_CHOICES)
  
  user_ip = models.ForeignKey('UserIP') #Required false while figuring out how to implement
  
  #unused fields
  support_crypto = models.BooleanField(default=True)
  require_crypto = models.BooleanField(default=False) 
  
  last_announce = models.DateTimeField(auto_now=True)
  
  def ip_port(self):
    return "%s:%s" % (self.user_ip.ip, self.port)
  
  def username(self):
    return self.user_ip.user.username
  
  def active(self):
    delta = datetime.timedelta(seconds=MAGIC_VALUES['time_until_inactive'])
    return self.last_announce >= datetime.datetime.now() - delta
  
  def inactive(self):
    return not self.active()

def current_peers():
  delta = datetime.timedelta(seconds=MAGIC_VALUES['time_until_inactive'])
  return Peer.objects.filter(last_announce__range=(datetime.datetime.now() - delta, datetime.datetime.now()))


#Class to map ip addresses to user.
class UserIP(models.Model):
  user = models.ForeignKey(User, blank=True, null=True)
  ip = models.IPAddressField(unique=True)
  
  def __unicode__(self):
    return "%s [%s]" % (self.user.username, self.ip)

class RatioModel(models.Model):
  downloaded = models.IntegerField(default=0)
  uploaded = models.IntegerField(default=0)
  
  def pretty_filesize(self, bytes):
    suffix = ['tb', 'gb', 'mb', 'kb']
    a_suffix = 'b'
    bytes = float(bytes)
    while bytes >= 1024:
      try:
        a_suffix = suffix.pop()
        bytes /= 1024    
      except IndexError:
        return "%.2f tb" % (bytes)
    return "%.2f %s" % (bytes, a_suffix)
    
  def download_size(self):
    return self.pretty_filesize(self.downloaded)
  
  def upload_size(self):
    return self.pretty_filesize(self.uploaded)
  
  def ratio(self):
    if self.downloaded == 0:
      if self.uploaded == 0:
        return '0.00'
      return 'Inf'
    return "%.2f" % (float(self.uploaded) / self.downloaded)

#Map the amount the user downloaded/uploaded on a torrent
class RatioInfo(RatioModel):
  user = models.ForeignKey(User)
  torrent = models.ForeignKey(Torrent)

#Maps the total downloaded and uploaded to a user uniquely (updated automatically)
class UserRatio(RatioModel):
  user = models.OneToOneField(User)
