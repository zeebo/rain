from django.test import TestCase
from models import Peer

class MyTestCase(TestCase):
  urls = 'tracker.urls'
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

class AnnounceTest(MyTestCase):
  def test_bad_ip_authentication(self):
    self.make_bad_request(event='started', extra_params={'REMOTE_ADDR': '1.1.1.1'})
  
  def test_double_start(self):
    self.make_good_request(event='started')
    self.make_bad_request(event='started')
  
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
  urls = 'tracker.urls'
  fixtures = ['torrents.json', 'users.json']
  
  def test_scrape(self):
    response = self.client.get('/tracker/scrape?info_hash=%eb%22%8c%08%6e%67%da%7f%5e%43%5e%f6%e4%75%7d%29%31%07%00%8b')
    self.assertNotContains(response, 'Error: ', status_code=200)
    
    response = self.client.get('/tracker/scrape?info_hash=%eb%22%8c%08%6e%67%da%7f%5e%43%5e%f6%e4%75%7d%29%31%07%00%8b&info_hash=%eb%22%8c%08%6e%67%da%7f%5e%43%5e%f6%e4%75%7d%29%31%07%00%8b&info_hash=%eb%22%8c%08%6e%67%da%7f%5e%43%5e%f6%e4%75%7d%29%31%07%00%8b')
    self.assertNotContains(response, 'Error: ', status_code=200)
