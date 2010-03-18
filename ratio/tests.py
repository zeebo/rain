from django.test import TestCase
from models import RatioInfo, UserRatio

class MyTestCase(TestCase):
  #urls = 'tracker.urls'
  fixtures = ['torrents.json', 'users.json']
  
  def make_request(self, info_hash='%eb%22%8c%08%6e%67%da%7f%5e%43%5e%f6%e4%75%7d%29%31%07%00%8b',
                         peer_id='test',
                         port='1234',
                         uploaded='0',
                         downloaded='0',
                         left='1',
                         numwant='200',
                         key='test',
                         compact='1',
                         event=None,
                         extra_params=None):
                         
    local_settings = locals()
    del local_settings['extra_params']
    del local_settings['self']
    for key, value in local_settings.items():
      if value is None:
        del local_settings[key]
    
    if extra_params is None:
      extra_params = {}
    
    return self.client.get('/tracker/announce?%s' % '&'.join(['%s=%s' % (k, local_settings[k]) for k in local_settings]), **extra_params)
  
  def check_invalid_argument(self, invalid_args):
    for name, value in invalid_args:
      self.make_bad_request(**{name: value})
  
  def make_good_request(self, *args, **kwargs):
    response = self.make_request(*args, **kwargs)
    self.assertNotContains(response, 'Error: ', status_code=200)
  
  def make_bad_request(self, *args, **kwargs):
    response = self.make_request(*args, **kwargs)
    self.assertContains(response, 'Error: ', status_code=200)

class RatioTest(MyTestCase):
  def test_bad_torrent_update(self):
    self.make_good_request(event='started', downloaded='100', uploaded='50')
    
    self.make_bad_request(downloaded='90', uploaded='50')
    
    #make sure data didnt change
    self.failUnlessEqual(RatioInfo.objects.all().count(), 1)
    obj = RatioInfo.objects.all().get()
    self.failUnlessEqual(obj.downloaded, 100)
    self.failUnlessEqual(obj.uploaded, 50)
    
    self.make_bad_request(downloaded='120', uploaded='40')
    
    self.failUnlessEqual(RatioInfo.objects.all().count(), 1)
    obj = RatioInfo.objects.all().get()
    self.failUnlessEqual(obj.downloaded, 100)
    self.failUnlessEqual(obj.uploaded, 50)
  
  def test_torrent_ratio_created(self):
    self.make_good_request(event='started', downloaded='100', uploaded='50')
    
    self.failUnlessEqual(RatioInfo.objects.all().count(), 1)
    obj = RatioInfo.objects.all().get()
    self.failUnlessEqual(obj.downloaded, 100)
    self.failUnlessEqual(obj.uploaded, 50)
    
    self.make_good_request(event='started', downloaded='120', uploaded='60', info_hash='%58%00%39%8c%82%f7%6c%14%ea%5f%37%d9%4c%8e%d1%37%9c%e5%0c%bd')
    
    self.failUnlessEqual(RatioInfo.objects.all().count(), 2)
    obj = RatioInfo.objects.exclude(pk=obj.pk).get()
    self.failUnlessEqual(obj.downloaded, 120)
    self.failUnlessEqual(obj.uploaded, 60)
    
  def test_torrent_ratio_updated(self):
    self.make_good_request(event='started', downloaded='100', uploaded='50')
    self.make_good_request(downloaded='120', uploaded='60')
    
    self.failUnlessEqual(RatioInfo.objects.all().count(), 1)
    obj = RatioInfo.objects.all().get()
    self.failUnlessEqual(obj.downloaded, 120)
    self.failUnlessEqual(obj.uploaded, 60)
    
    self.make_good_request(event='started', downloaded='150', uploaded='30', info_hash='%58%00%39%8c%82%f7%6c%14%ea%5f%37%d9%4c%8e%d1%37%9c%e5%0c%bd')
    self.make_good_request(downloaded='180', uploaded='30', info_hash='%58%00%39%8c%82%f7%6c%14%ea%5f%37%d9%4c%8e%d1%37%9c%e5%0c%bd')
    
    self.failUnlessEqual(RatioInfo.objects.all().count(), 2)
    #check to see original info didnt change
    self.failUnlessEqual(obj.downloaded, 120)
    self.failUnlessEqual(obj.uploaded, 60)
    
    obj = RatioInfo.objects.exclude(pk=obj.pk).get()
    self.failUnlessEqual(obj.downloaded, 180)
    self.failUnlessEqual(obj.uploaded, 30)
    
  def test_user_ratio_created(self):
    self.make_good_request(event='started', downloaded='100', uploaded='50')
    
    self.failUnlessEqual(UserRatio.objects.all().count(), 1)
    obj = UserRatio.objects.all().get()
    self.failUnlessEqual(obj.downloaded, 100)
    self.failUnlessEqual(obj.uploaded, 50)
  
  def test_user_ratio_updated(self):
    self.make_good_request(event='started', downloaded='100', uploaded='50')
    self.make_good_request(downloaded='120', uploaded='60')
    
    self.failUnlessEqual(UserRatio.objects.all().count(), 1)
    obj = UserRatio.objects.all().get()
    self.failUnlessEqual(obj.downloaded, 120)
    self.failUnlessEqual(obj.uploaded, 60)
  
  def test_user_ratio_is_total(self):
    self.make_good_request(event='started', downloaded='100', uploaded='50')
    self.make_good_request(event='started', downloaded='100', uploaded='50', info_hash='%58%00%39%8c%82%f7%6c%14%ea%5f%37%d9%4c%8e%d1%37%9c%e5%0c%bd')
    
    self.failUnlessEqual(UserRatio.objects.all().count(), 1)
    obj = UserRatio.objects.all().get()
    self.failUnlessEqual(obj.downloaded, 200)
    self.failUnlessEqual(obj.uploaded, 100)
