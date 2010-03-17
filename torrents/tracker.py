from rain.tracker.models import Torrent

def authorize_torrent(info_hash):
  if Torrent.objects.filter(info_hash=info_hash).exists():
    return None
  return 'Invalid info_hash'

def handle_completed(values, user, peer):
  try:
    Torrent.objects.get(info_hash=values['info_hash']).increment_downloaded()
  except (Torrent.DoesNotExist, Torrent.MultipleObjectsReturned):
    return None, 'Info hash does not correspond to a known torrent'
  
  return peer, None
