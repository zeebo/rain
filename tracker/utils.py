import string
from rain.tracker.models import Torrent, Peer, current_peers, UserIP, RatioInfo, UserRatio
from django.template import RequestContext
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rain.tracker import ipaddr
from rain.settings import MAGIC_VALUES
from django.http import HttpResponse
import datetime
import hashlib
import unittest
import random

def bencode(data):
  if isinstance(data, int):
    return "i%de" % data
  if isinstance(data, str):
    return "%d:%s" % (len(data), data)
  if isinstance(data, list):
    return "l%se" % ''.join(bencode(x) for x in data)
  if isinstance(data, dict):
    return "d%se" % ''.join('%s%s' % (bencode(x), bencode(data[x])) for x in sorted(data.keys()))
  
  raise TypeError

def bdecode(data):
  '''Main function to decode bencoded data'''
  def _dechunk(chunks):
    try:
      item = chunks.pop()
    except IndexError:
      raise ValueError('Unexpected end of data')
    
    if (item == 'd'): 
      item = chunks.pop()
      h = {}
      while (item != 'e'):
        chunks.append(item)
        if not chunks[-1].isdigit():
          raise ValueError('Non numeric digit')
        key = _dechunk(chunks)
        h[key] = _dechunk(chunks)
        item = chunks.pop()
      return h
    elif (item == 'l'):
      item = chunks.pop()
      list = []
      while (item != 'e'):
        chunks.append(item)
        list.append(_dechunk(chunks))
        item = chunks.pop()
      return list
    elif (item == 'i'):
      item = chunks.pop()
      num = ''
      while (item != 'e'):
        num  += item
        item = chunks.pop()
      return int(num)
    elif item.isdigit():
      num = ''
      while item.isdigit():
        num += item
        item = chunks.pop()
      line = ''
      for i in range(1, int(num) + 1):
        line += chunks.pop()
      return line
  
  chunks = list(data)
  chunks.reverse()
  
  try:
    root = _dechunk(chunks)
  except IndexError:
    raise ValueError
  
  if len(chunks):
    raise ValueError('Extra data')
  return root


def get_user_from_ip(ip):
  try:
    return UserIP.objects.filter(ip=ip).get(), None
  except (UserIP.MultipleObjectsReturned, UserIP.DoesNotExist):
    return None, tracker_error_response('Problem authenticating against your ip address')

def update_ratio(peer, torrent, downloaded, uploaded):
  if downloaded is None or uploaded is None:
    return tracker_error_response('Must pass downloaded/uploaded info')
  
  if peer is None:
    return tracker_error_response('Somehow managed to not get a peer')
  
  ratio_object, created = RatioInfo.objects.get_or_create(user=peer.user_ip.user, torrent=torrent)
  
  delta_download = downloaded - ratio_object.downloaded
  delta_uploaded = uploaded - ratio_object.uploaded
  
  if delta_uploaded < 0 or delta_download < 0:
    return tracker_error_response('Downloaded/uploaded info went backwards. uh oh.')
  
  ratio_object.downloaded = downloaded
  ratio_object.uploaded = uploaded
  
  user_ratio_object, created = UserRatio.objects.get_or_create(user=peer.user_ip.user)
  
  user_ratio_object.downloaded += delta_download
  user_ratio_object.uploaded += delta_uploaded
  
  ratio_object.save()
  user_ratio_object.save()
  
  return None

def tracker_error_response(value):
  return HttpResponse(bencode({'failure reason': "Error: %s" % value}), mimetype='text/plain')

def tracker_response(value):
  return HttpResponse(bencode(value), mimetype='text/plain')

def get_cleaned_hashes(request):
  request.encoding = 'iso-8859-1'
  hash_list = []
  for dirty_hash in request.GET.getlist('info_hash'):
    clean_hash, response = clean_info_hash(dirty_hash)
    if response is not None:
      return None, response
    
    hash_list.append(clean_hash)
  
  if hash_list == []:
    return None, tracker_error_response('No info_hashes specified')
  
  return hash_list, None

def clean_info_hash(dirty_hash):
  try:
    return dirty_hash.encode('iso-8859-1').encode('hex'), None
  except AttributeError:
    return None, tracker_error_response('Invalid info_hash')

def parse_request(request):
  values = {}
  request.encoding = 'iso-8859-1'
    
  #Get the interesting values from the request
  values['info_hash'], response = clean_info_hash(request.GET.get('info_hash', None))
  if response is not None:
    return None, response
  
  values['peer_id'] = request.GET.get('peer_id', None)
  values['ip'] = request.META.get('REMOTE_ADDR') #ignore any sent ip address
  values['key'] = request.GET.get('key', None)
  values['event'] = request.GET.get('event', 'update')
  
  #These are integer values and require special handling
  try:
    values['port'] = int(request.GET.get('port', None))
    values['amount_left'] = int(request.GET.get('left', None))
    values['amount_downloaded'] = int(request.GET.get('downloaded', None))
    values['amount_uploaded'] = int(request.GET.get('uploaded', None))
    
    #Default values for parameters that arent required
    values['numwant'] = int(request.GET.get('numwant', MAGIC_VALUES['numwant_default']))
    values['compact'] = int(request.GET.get('compact', MAGIC_VALUES['compact_default']))
  except ValueError:
    return None, tracker_error_response('error parsing integer field')
  except TypeError:
    return None, tracker_error_response('missing value for required field')
  
  return values, check_request_sanity(values)

def check_request_sanity(values):
  if not 0 < values['port'] < 65536:
    return tracker_error_response('invalid port')  
  if not values['amount_left'] >= 0:
    return tracker_error_response('invalid amount remaining')  
  if not values['amount_downloaded'] >= 0:
    return tracker_error_response('invalid downloaded amount')  
  if not values['amount_uploaded'] >= 0:
    return tracker_error_response('invalid uploaded amount')  
  if values['compact'] not in (0, 1):
    return tracker_error_response('compact must be 0 or 1')  
  if not values['numwant'] >= 0:
    return tracker_error_response('invalid number of peers requested')  
  if values['event'] not in ('started', 'completed', 'stopped', 'update'):
    return tracker_error_response('invalid event')
  if values['peer_id'] is None:
    return tracker_error_response('peer id required')
  
  #all the data is good!
  return None

def peerset_to_ip(queryset, compact=1):
  if compact:
    return ''.join("%s%s%s" % (ipaddr.IPAddress(peer.user_ip.ip).packed, chr(peer.port//256), chr(peer.port%256)) for peer in queryset)
  else:
    return [{'peer id': peer.peer_id, 'ip': peer.user_ip.ip, 'port': peer.port} for peer in queryset]

def get_matching_torrent(info_hash):
  try:
    return Torrent.objects.filter(info_hash=info_hash).get(), None
  except (Torrent.MultipleObjectsReturned, Torrent.DoesNotExist):
    return None, tracker_error_response('Problem with info_hash')

def find_matching_peer(torrent, user_ip, port, key):
  peer_query = Peer.objects.filter(torrent=torrent).filter(user_ip=user_ip).filter(port=port)
  if key is not None:
    peer_query = peer_query.filter(key=key)
  try:
    return peer_query.get(), None
  except Peer.MultipleObjectsReturned:
    return None, tracker_error_response('Multiple peers match that torrent/ip/port/key combination')
  except Peer.DoesNotExist:
    return None, None

class EventHandler(object):
  def __call__(self, **kwargs):
    
    #Update the peer if it exists to update last_announce
    if kwargs['peer'] is not None:
      kwargs['peer'].save()
    
    return getattr(self, 'handle_%s' % kwargs['values']['event'])(**kwargs)
    
  def handle_started(self, values, user_ip, torrent, peer):
    if peer is not None:
      return None, tracker_error_response('You are already on this torrent')
    
    new_peer = Peer(torrent=torrent, peer_id=values['peer_id'], port=values['port'], user_ip=user_ip, key=values['key'])
    if values['amount_left'] == 0:
      new_peer.state = MAGIC_VALUES['seed']
    else:
      new_peer.state = MAGIC_VALUES['peer']
    
    new_peer.save()
    
    return new_peer, None
  
  def handle_completed(self, values, user_ip, torrent, peer):
    if peer is None:
      return None, tracker_error_response('Cant find which peer you are')
    
    peer.state = MAGIC_VALUES['seed']
    peer.torrent.increment_downloaded()
    peer.save()
    
    return peer, HttpResponse('', mimetype='text/plain')
  
  def handle_stopped(self, values, user_ip, torrent, peer):
    if peer is None:
      return None, tracker_error_response('Cant find which peer you are')
    
    peer.delete()
    
    return None, HttpResponse('', mimetype='text/plain')
  
  def handle_update(self, values, user_ip, torrent, peer):
    if peer is None:
      return None, tracker_error_response('Cant find which peer you are')
    
    if values['amount_left'] == 0:
      peer.state = MAGIC_VALUES['seed']
      peer.save()
    
    return peer, None

def generate_announce_response(values, torrent, peer):
  peer_list = current_peers().filter(torrent=torrent).exclude(pk=peer.pk).order_by('-state')
  num_peers = current_peers().filter(torrent=torrent).filter(state=MAGIC_VALUES['peer']).count()
  num_seeds = current_peers().filter(torrent=torrent).filter(state=MAGIC_VALUES['seed']).count()
  
  if peer.state == MAGIC_VALUES['seed']:
    interval = MAGIC_VALUES['seed_interval']
  else:
    interval = MAGIC_VALUES['peer_interval']
  
  return tracker_response({
    'interval': interval,
    'complete': num_seeds,
    'incomplete': num_peers,
    'peers': peerset_to_ip(peer_list[:values['numwant']], values['compact']),
  })

def generate_scrape_response(hashes):
  response_dict = {'files' : {}}
  
  for a_hash in hashes:
    torrent, response = get_matching_torrent(info_hash=a_hash)
    if response is not None:
      return response
    
    response_dict['files'][a_hash] = {
      'complete' : torrent.num_seeds(),
      'downloaded' : torrent.downloaded,
      'incomplete' : torrent.num_peers()
    }
  
  return tracker_response(response_dict)

