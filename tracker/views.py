# Create your views here.
from django.http import HttpResponse
from django.utils.encoding import smart_str
from rain.tracker.models import Torrent, Peer
from rain import utils
from rain.settings import MAGIC_VALUES
import ipaddr
import datetime

def tracker_error_response(value):
  return HttpResponse(utils.bencode({'failure reason': "Error: %s" % value}), mimetype='text/plain')

def tracker_response(value):
  return HttpResponse(utils.bencode(value), mimetype='text/plain')

def parse_request(request):
  values = {}
  request.encoding = 'iso-8859-1'
  
  #Get the interesting values from the request
  try:
    values['info_hash'] = request.GET.get('info_hash', None).encode('iso-8859-1').encode('hex')
  except AttributeError:
    return None, tracker_error_response('No info_hash specified')
  
  values['peer_id'] = request.GET.get('peer_id', None)
  values['ip'] = request.META.get('REMOTE_ADDR')
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
  
  #all the data is good!
  return None

def peerset_to_ip(queryset, compact=1):
  if compact:
    return ''.join("%s%s%s" % (ipaddr.IPAddress(peer.ip).packed, chr(peer.port//256), chr(peer.port%256)) for peer in queryset)
  else:
    return [{'peer id': peer.peer_id, 'ip': peer.ip, 'port': peer.port} for peer in queryset]

def get_matching_torrent(info_hash):
  try:
    return Torrent.objects.filter(info_hash=info_hash).get(), None
  except (Torrent.MultipleObjectsReturned, Torrent.DoesNotExist):
    return None, tracker_error_response('Problem with info_hash')

def current_peers():
  delta = datetime.timedelta(seconds=30*60) #30 minutes
  return Peer.objects.filter(last_announce__range=(datetime.datetime.now() - delta, datetime.datetime.now()))

def find_matching_peer(torrent, ip, port, key):
  peer_query = current_peers().filter(torrent=torrent).filter(ip=ip).filter(port=port)
  if key is not None:
    peer_query = peer_query.filter(key=key)
  try:
    return peer_query.get(), None
  except Peer.MultipleObjectsReturned:
    return None, tracker_error_response('Multiple peers match that torrent/ip/port/key combination')
  except Peer.DoesNotExist:
    return None, None

class EventHandler(object):
  def __call__(self, values, torrent, peer):
    return getattr(self, 'handle_%s' % values['event'])(values, torrent, peer)
    
  def handle_started(self, values, torrent, peer):
    if peer is not None:
      return None, tracker_error_response('You are already on this torrent')
    
    new_peer = Peer(torrent=torrent, peer_id=values['peer_id'], port=values['port'], ip=values['ip'], key=values['key'])
    if values['amount_left'] == 0:
      new_peer.state = MAGIC_VALUES['seed'] #Seed
    else:
      new_peer.state = MAGIC_VALUES['peer'] #Peer
    
    new_peer.save()
    
    return new_peer, None
  
  def handle_completed(self, values, torrent, peer):
    if peer is None:
      return None, tracker_error_response('Cant find which peer you are')
    
    peer.state = MAGIC_VALUES['seed']
    peer.save()
    
    return peer, HttpResponse('', mimetype='text/plain')
  
  def handle_stopped(self, values, torrent, peer):
    if peer is None:
      return None, tracker_error_response('Cant find which peer you are')
    
    peer.delete()
    
    return None, HttpResponse('', mimetype='text/plain')
  
  def handle_update(self, values, torrent, peer):
    if peer is None:
      return None, tracker_error_response('Cant find which peer you are')
    
    if values['amount_left'] == 0:
      peer.state = MAGIC_VALUES['seed']
    
    #Make sure to save the peer regardless to update announce time
    peer.save()
    
    return peer, None

def generate_response(values, torrent, peer):
  peer_list = current_peers().filter(torrent=torrent).exclude(pk=peer.pk).order_by('-state')
  num_peers = current_peers().filter(torrent=torrent).filter(state=MAGIC_VALUES['peer']).count()
  num_seeds = current_peers().filter(torrent=torrent).filter(state=MAGIC_VALUES['seed']).count()
  
  if peer.state == MAGIC_VALUES['seed']:
    interval = MAGIC_VALUES['seed_interval']
  else:
    interval = MAGIC_VALUES['peer_interval']
  
  return {
    'interval': interval,
    'complete': num_seeds,
    'incomplete': num_peers,
    'peers': peerset_to_ip(peer_list[:values['numwant']], values['compact']),
  }

def announce(request):
  #Parse the request and return any errors
  values, response = parse_request(request)
  if response is not None:
    return response
  
  #Find the torrent the request is for and return any errors
  torrent, response = get_matching_torrent(info_hash=values['info_hash'])
  if response is not None:
    return response
  
  #Find the peer that matches the request, or none if it is new
  peer, response = find_matching_peer(torrent=torrent, ip=values['ip'], port=values['port'], key=values['key'])
  if response is not None:
    return response
  
  #Create an event handler and hand off the event to it.
  handler = EventHandler()
  peer, response = handler(values=values, torrent=torrent, peer=peer)
  if response is not None:
    return response
  
  #Find more peers on the same torrent that arent the current peer
  response = generate_response(values=values, torrent=torrent, peer=peer)  
  
  return tracker_response(response)

