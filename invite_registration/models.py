from django.db import models
from django.contrib.auth.models import User
import random, hashlib

# Create your models here.


def random_hash_code():
  return hashlib.sha1(random.getrandbits(40)).hexdigest()

class Invite(models.Model):
  hash_code = models.CharField(max_lenght=40, unique=True, default=random_hash_code, editable=False)
  owner = models.ForeignKey(User)
  child = models.ForeignKey(User, null=True, blank=True)
  
  active = models.BooleanField(defualt=True)
  
  def used(self):
    return self.child is None
