from models import RatioInfo, UserRatio

def update_ratio(peer, user, info_hash, downloaded, uploaded):
  if downloaded is None or uploaded is None:
    return 'Must pass downloaded/uploaded info'
  
  ratio_object, created = RatioInfo.objects.get_or_create(user=user, info_hash=info_hash)
  
  delta_download = downloaded - ratio_object.downloaded
  delta_uploaded = uploaded - ratio_object.uploaded
  
  if delta_uploaded < 0 or delta_download < 0:
    return 'Downloaded/uploaded info went backwards. uh oh.'
  
  ratio_object.downloaded = downloaded
  ratio_object.uploaded = uploaded
  
  user_ratio_object, created = UserRatio.objects.get_or_create(user=user)
  
  user_ratio_object.downloaded += delta_download
  user_ratio_object.uploaded += delta_uploaded
  
  ratio_object.save()
  user_ratio_object.save()
  
  return None

def handle_started(values, user, peer):
  return peer, update_ratio(peer=peer, user=user, info_hash=values['info_hash'], downloaded=values['amount_downloaded'], uploaded=values['amount_uploaded'])
def handle_completed(values, user, peer):
  return peer, update_ratio(peer=peer, user=user, info_hash=values['info_hash'], downloaded=values['amount_downloaded'], uploaded=values['amount_uploaded'])
def handle_stopped(values, user, peer):
  return peer, update_ratio(peer=peer, user=user, info_hash=values['info_hash'], downloaded=values['amount_downloaded'], uploaded=values['amount_uploaded'])
def handle_update(values, user, peer):
  return peer, update_ratio(peer=peer, user=user, info_hash=values['info_hash'], downloaded=values['amount_downloaded'], uploaded=values['amount_uploaded'])