from django.db import models
from django.contrib.auth.models import User
#from rain.tracker.models import current_peers

class Torrent(models.Model):
  torrent = models.FileField(upload_to='torrents')
  uploaded_by = models.ForeignKey(User, default=User.objects.all()[0].pk)
  info_hash = models.CharField(max_length=40, editable=False, unique=True, default='info_hash not specified')
  downloaded = models.IntegerField(default=0)
  
  def __unicode__(self):
    return self.info_hash
  
  def num_seeds(self):
    return 0
    #return current_peers().filter(torrent=self).filter(state=MAGIC_VALUES['seed']).count()
  
  def num_peers(self):
    return 0
    #return current_peers().filter(torrent=self).filter(state=MAGIC_VALUES['peer']).count()
  
  def torrent_data(self):
    self.torrent.seek(0)
    return_data = self.torrent.read()
    self.torrent.seek(0)
    
    return return_data
  
  def set_info_hash(self):
    data = bdecode(self.torrent_data())
    self.info_hash = hashlib.sha1(bencode(data['info'])).digest().encode('hex')
    
  def increment_downloaded(self):
    self.downloaded += 1
    self.save()
  
  def save(self, *args, **kwargs):
    if self.info_hash == 'info_hash not specified':
      self.set_info_hash()
    
    super(Torrent, self).save(*args, **kwargs)