from django.db import models
from django.contrib.auth.models import User

def random_hash_code():
  import random, hashlib
  return hashlib.sha1(str(random.getrandbits(40))).hexdigest()

class Invite(models.Model):
  hash_code = models.CharField(max_length=40, unique=True, default=random_hash_code, editable=False)
  owner = models.ForeignKey(User, related_name='owner_id')
  child = models.ForeignKey(User, null=True, blank=True, related_name='child_id')
  
  active = models.BooleanField(default=True)
  
  join_date = models.DateTimeField(blank=True, null=True)
  
  def used(self):
    return self.child is None
