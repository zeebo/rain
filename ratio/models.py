from django.db import models
from django.contrib.auth.models import User

# Create your models here.
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
  info_hash = models.CharField(max_length=40)
  last_updated = models.DateTimeField(auto_now=True)

#Maps the total downloaded and uploaded to a user uniquely (updated automatically)
class UserRatio(RatioModel):
  user = models.OneToOneField(User)