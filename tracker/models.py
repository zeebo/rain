from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import hashlib
import datetime

class Peer(models.Model):
  STATE_CHOICES = (
    (settings.MAGIC_VALUES['peer'], 'Peer'),
    (settings.MAGIC_VALUES['seed'], 'Seed'),
  )
  info_hash = models.CharField(max_length=40)
  peer_id = models.CharField(max_length=20)
  port = models.IntegerField()
  key = models.CharField(max_length=100, blank=True, null=True) #spec does not specify data type on key
  state = models.CharField(max_length=1, choices=STATE_CHOICES)
  
  user = models.ForeignKey(User) #Required false while figuring out how to implement
  
  #unused fields
  support_crypto = models.BooleanField(default=True)
  require_crypto = models.BooleanField(default=False) 
  
  last_announce = models.DateTimeField(auto_now=True)
  
  def username(self):
    return self.user.username
  
  def active(self):
    delta = datetime.timedelta(seconds=settings.MAGIC_VALUES['time_until_inactive'])
    return self.last_announce >= datetime.datetime.now() - delta
  
  def inactive(self):
    return not self.active()

def current_peers():
  delta = datetime.timedelta(seconds=settings.MAGIC_VALUES['time_until_inactive'])
  return Peer.objects.filter(last_announce__range=(datetime.datetime.now() - delta, datetime.datetime.now()))
