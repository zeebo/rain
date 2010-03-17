from rain.tracker.models import Peer
from django.conf import settings

def handle_started(values, user, peer):
  if peer is not None:
    return None, 'You are already on this torrent'
  
  new_peer = Peer(info_hash=values['info_hash'], peer_id=values['peer_id'], port=values['port'], user=user, key=values['key'])
  if values['amount_left'] == 0:
    new_peer.state = settings.MAGIC_VALUES['seed']
  else:
    new_peer.state = settings.MAGIC_VALUES['peer']
  
  new_peer.save()
  
  return new_peer, None

def handle_completed(values, user, peer):
  if peer is None:
    return None, 'Cant find which peer you are'
  
  peer.state = settings.MAGIC_VALUES['seed']
  peer.save()
  
  return peer, None

def handle_stopped(values, user, peer):
  if peer is None:
    return None, 'Cant find which peer you are'
  
  peer.delete()
  
  return None, None

def handle_update(values, user, peer):
  if peer is None:
    return None, 'Cant find which peer you are'
  
  if values['amount_left'] == 0:
    peer.state = settings.MAGIC_VALUES['seed']
    peer.save()
  
  return peer, None