from django.db import models
from django.contrib.auth.models import User

class UserIP(models.Model):
  user = models.ForeignKey(User, blank=True, null=True)
  ip = models.IPAddressField(unique=True)
  
  def __unicode__(self):
    return "%s [%s]" % (self.user.username, self.ip)