from django.db import models

# Create your models here.
class Torrent(models.Model):
  torrent = models.FileField(upload_to='torrents')