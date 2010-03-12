from django.test import TestCase
from rain.tracker.models import Peer, Torrent, RatioInfo, UserRatio

class MyTestCase(TestCase):
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
    
    return self.client.get('/announce?%s' % '&'.join(['%s=%s' % (k, local_settings[k]) for k in local_settings]), **extra_params)
  
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
  fixtures = ['a_torrent.json', 'a_user.json']
  
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


class AnnounceTest(MyTestCase):
  fixtures = ['a_torrent.json', 'a_user.json']
  
  def test_bad_ip_authentication(self):
    self.make_bad_request(event='started', extra_params={'REMOTE_ADDR': '1.1.1.1'})
    
  
  def test_double_start(self):
    self.make_good_request(event='started')
    self.make_bad_request(event='started')
  
  def test_download_incremented(self):
    self.make_good_request(event='started')
    self.make_good_request(event='completed', left='0')
    
    torrent = Peer.objects.all().get().torrent
    self.failUnlessEqual(torrent.downloaded, 1)
    
    other_torrent = Torrent.objects.exclude(pk=torrent.pk).get()
    self.failUnlessEqual(other_torrent.downloaded, 0)
    
  def test_peer_cycle(self):
    self.make_good_request(event='started')
    
    new_peer = Peer.objects.all().get()
    self.failUnlessEqual(new_peer.peer_id, 'test')
    self.failUnlessEqual(new_peer.state, 'P')
    
    self.make_good_request(left='0', numwant='0')
    
    new_peer = Peer.objects.all().get()
    self.failUnlessEqual(new_peer.state, 'S')
    
    self.make_good_request(event='stopped', left='0', numwant='0')
    self.assertRaises(Peer.DoesNotExist, Peer.objects.all().get)
  
  def test_add_as_seed(self):
    response = self.make_request(left='0', event='started')
    self.assertNotContains(response, 'Error: ', status_code=200)
    new_peer = Peer.objects.all().get()
    self.failUnlessEqual(new_peer.state, 'S')
  
  def test_invalid_hash(self):
    self.check_invalid_argument( (('info_hash', 'invalid_hash'), ('info_hash', None)) )
  
  def test_invalid_peer_id(self):
    self.check_invalid_argument( (('peer_id', 'over_twenty_characters_long'), ('peer_id', None)) )
  
  def test_invalid_port(self):
    self.check_invalid_argument( (('port', '123456'), ('port', 'abc'), ('port', '-5'), ('port', None)) )
  
  def test_invalid_uploaded(self):
    self.check_invalid_argument( (('uploaded', '-5'), ('uploaded', 'abc'), ('uploaded', None)) )
  
  def test_invalid_downloaded(self):
    self.check_invalid_argument( (('downloaded', '-5'), ('downloaded', 'abc'), ('downloaded', None)) )
  
  def test_invalid_left(self):
    self.check_invalid_argument( (('left', '-5'), ('left', 'abc'), ('left', None)) )
   
  def test_invalid_numwant(self):
    self.check_invalid_argument( (('numwant', '-5'), ('numwant', 'abc'), ('numwant', None)) )
  
  def test_invalid_compact(self):
    self.check_invalid_argument( (('compact', '2'), ('compact', 'abc'), ('compact', None)) )
  
  def test_invalid_event(self):
    self.check_invalid_argument( (('event', 'bad_event'), ('event', None) ) )


class ScrapeTest(TestCase):
  fixtures = ['a_torrent.json', 'a_user.json']
  
  def test_scrape(self):
    response = self.client.get('/scrape?info_hash=%eb%22%8c%08%6e%67%da%7f%5e%43%5e%f6%e4%75%7d%29%31%07%00%8b')
    self.assertNotContains(response, 'Error: ', status_code=200)
    
    response = self.client.get('/scrape?info_hash=%eb%22%8c%08%6e%67%da%7f%5e%43%5e%f6%e4%75%7d%29%31%07%00%8b&info_hash=%eb%22%8c%08%6e%67%da%7f%5e%43%5e%f6%e4%75%7d%29%31%07%00%8b&info_hash=%eb%22%8c%08%6e%67%da%7f%5e%43%5e%f6%e4%75%7d%29%31%07%00%8b')
    self.assertNotContains(response, 'Error: ', status_code=200)
  
  def test_invalid_hash(self):
    response = self.client.get('/scrape?info_hash=bad_hash')
    self.assertContains(response, 'Error: ', status_code=200)
    
    response = self.client.get('/scrape?info_hash=%eb%22%8c%08%6e%67%da%7f%5e%43%5e%f6%e4%75%7d%29%31%07%00%8b&info_hash=bad_hash')
    self.assertContains(response, 'Error: ', status_code=200)
    
  def test_blank_hash(self):
    response = self.client.get('/scrape')
    self.assertContains(response, 'Error: ', status_code=200)

    