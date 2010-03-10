# Create your views here.
from django.http import HttpResponse
from django.utils.encoding import smart_str
from rain.tracker.models import Torrent, Peer
from rain import utils
import ipaddr

def tracker_error_response(value):
  return HttpResponse(utils.bencode({'failure reason':value}), mimetype='text/plain')

def tracker_response(value):
  return HttpResponse(utils.bencode(value), mimetype='text/plain')

def peerset_to_ip(queryset, compact=1):
  if compact:
    return ''.join("%s%s%s" % (ipaddr.IPAddress(peer.ip).packed, chr(peer.port//256), chr(peer.port%256)) for peer in queryset)
  else:
    return [{'peer id': peer.peer_id, 'ip': peer.ip, 'port': peer.port} for peer in queryset]

def announce(request):
  request.encoding = 'iso-8859-1'
  info_hash = request.GET.get('info_hash', '').encode('iso-8859-1').encode('hex')
  try:
    torrent = Torrent.objects.filter(info_hash=info_hash).get()
  except (Torrent.MultipleObjectsReturned, Torrent.DoesNotExist):
    return tracker_error_response('Problem with info_hash')
  
  #Parse data out
  peer_id = request.GET.get('peer_id', 'no-peer-id')
  ip = request.META.get('REMOTE_ADDR')
  key = request.GET.get('key', '')
  port = request.GET.get('port', 0)
  event = request.GET.get('event', 'update')
  amount_left = request.GET.get('left', 0)
  compact = request.GET.get('compact', 0)
  numwant = int(request.GET.get('numwant', '30'))
  
  #Attempt to find the peer who is doing the announce based on key, ip and torrent
  peer_query = Peer.objects.filter(torrent=torrent).filter(ip=ip)
  if key != '':
    peer_query = peer_query.filter(key=key)
  try:
    peer = peer_query.get()
  except (Peer.MultipleObjectsReturned, Peer.DoesNotExist):
    peer = None
  
  #Make a new peer object based on the announce
  if event == 'started':
    if peer is not None:
      return tracker_error_response('Already on that torrent. uh oh.')
    
    new_peer = Peer(torrent=torrent, peer_id=peer_id, port=port, ip=ip, key=key)
    if amount_left == 0:
      new_peer.state = 'S' #Seed
    else:
      new_peer.state = 'P' #Peer
    new_peer.save()
    
    peer = new_peer
  
  if event == 'stopped':
    if peer is None:
      return tracker_error_response('Cant find which peer you are. restart the torrent bro')
    
    peer.delete()
    return HttpResponse('', mimetype='text/plain')
  
  #Find more peers on the same torrent that arent the current peer
  peer_list = Peer.objects.filter(torrent=torrent).exclude(pk=peer.pk).order_by('-state')
  num_peers = Peer.objects.filter(torrent=torrent).filter(state='P').count()
  num_seeds = Peer.objects.filter(torrent=torrent).filter(state='S').count()
  
  response = {
    'interval': 30,
    'complete': num_seeds,
    'incomplete': num_peers,
    'peers': peerset_to_ip(peer_list[:numwant], compact),
  }
  
  return tracker_response(response)

