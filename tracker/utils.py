from rain.tracker.models import Peer, current_peers
from django.contrib.auth.models import User
from rain import ipaddr
from django.http import HttpResponse
from django.conf import settings
from django.utils.importlib import import_module

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

def handle_events(values, user, peer):
  handler_function = 'handle_%s' % values['event']
  for app in settings.INSTALLED_APPS:
    try:
      peer, response = getattr(import_module("%s.tracker" % app), handler_function)(values, user, peer)
      if response is not None:
        return peer, response
    except (AttributeError, ImportError):
      continue
  
  return peer, response

def authenticate_torrent(info_hash):
  for app in settings.INSTALLED_APPS:
    try:
      response = getattr(import_module("%s.tracker" % app), 'authorize_torrent')(info_hash)
      if response is not None:
        return response
    except (AttributeError, ImportError):
      continue
  
  return None

def authenticate_user(request):
  queryset = User.objects.all()
  #Code idea borrowed from the django admin autodiscover
  for app in settings.INSTALLED_APPS:
    try:
      queryset = getattr(import_module("%s.tracker" % app), 'authorize_user')(request, queryset)
    except (AttributeError, ImportError):
      continue
  
  #Return the user
  try:
    return queryset.get(), None
  except User.MultipleObjectsReturned:
    return None, 'Too many users matched your credentials'
  except User.DoesNotExist:
    return None, 'No users matched your credentials'

def tracker_error(value):
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
    return None, 'No info_hashes specified'
  
  return hash_list, None

def clean_info_hash(dirty_hash):
  try:
    return dirty_hash.encode('iso-8859-1').encode('hex'), None
  except AttributeError:
    return None, 'Invalid info_hash'

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
    values['numwant'] = int(request.GET.get('numwant', settings.MAGIC_VALUES['numwant_default']))
    values['compact'] = int(request.GET.get('compact', settings.MAGIC_VALUES['compact_default']))
  except ValueError:
    return None, 'error parsing integer field'
  except TypeError:
    return None, 'missing value for required field'
  
  return values, check_request_sanity(values)

def check_request_sanity(values):
  if not 0 < values['port'] < 65536:
    return 'invalid port'
  if not values['amount_left'] >= 0:
    return 'invalid amount remaining'
  if not values['amount_downloaded'] >= 0:
    return 'invalid downloaded amount'
  if not values['amount_uploaded'] >= 0:
    return 'invalid uploaded amount'
  if values['compact'] not in (0, 1):
    return 'compact must be 0 or 1'
  if not values['numwant'] >= 0:
    return 'invalid number of peers requested'
  if values['event'] not in ('started', 'completed', 'stopped', 'update'):
    return 'invalid event'
  if values['peer_id'] is None:
    return 'peer id required'
  
  #all the data is good!
  return None

def peerset_to_ip(queryset, compact=1):
  if compact:
    return ''.join("%s%s%s" % (ipaddr.IPAddress(peer.user_ip.ip).packed, chr(peer.port//256), chr(peer.port%256)) for peer in queryset)
  else:
    return [{'peer id': peer.peer_id, 'ip': peer.user_ip.ip, 'port': peer.port} for peer in queryset]

def find_matching_peer(info_hash, user, port, key):
  peer_query = Peer.objects.filter(info_hash=info_hash).filter(user=user).filter(port=port)
  if key is not None:
    peer_query = peer_query.filter(key=key)
  try:
    return peer_query.get(), None
  except Peer.MultipleObjectsReturned:
    return None, 'Multiple peers match that hash/user/port/key combination'
  except Peer.DoesNotExist:
    return None, None

def num_seeds(info_hash):
  return current_peers().filter(info_hash=info_hash).filter(state=settings.MAGIC_VALUES['seed']).count()

def num_peers(info_hash):
  return current_peers().filter(info_hash=info_hash).filter(state=settings.MAGIC_VALUES['peer']).count()

def generate_announce_response(values, peer):
  peer_list = current_peers().filter(info_hash=values['info_hash']).exclude(pk=peer.pk).order_by('-state')
    
  if peer.state == settings.MAGIC_VALUES['seed']:
    interval = settings.MAGIC_VALUES['seed_interval']
  else:
    interval = settings.MAGIC_VALUES['peer_interval']
  
  return tracker_response({
    'interval': interval,
    'complete': num_seeds(values['info_hash']),
    'incomplete': num_peers(values['info_hash']),
    'peers': peerset_to_ip(peer_list[:values['numwant']], values['compact']),
  })

def generate_scrape_response(hashes):
  response_dict = {'files' : {}}
  
  for a_hash in hashes:
    response_dict['files'][a_hash] = {
      'complete' : num_seeds(a_hash),
      'downloaded' : 0,
      'incomplete' : num_peers(a_hash)
    }
  
  return tracker_response(response_dict)

