from rain.tracker.utils import *

#from rain.profiler import profile
#@profile('announce.prof')
def announce(request):
  #Parse the request and return any errors
  values, response = parse_request(request)
  if response is not None:
    return response
  
  #Before doing anything, authenticate based on IP
  user_ip, response = get_user_from_ip(values['ip'])
  if response is not None:
    return response
  
  #Find the torrent the request is for and return any errors
  torrent, response = get_matching_torrent(info_hash=values['info_hash'])
  if response is not None:
    return response
  
  #Find the peer that matches the request, or none if it is new
  peer, response = find_matching_peer(torrent=torrent, user_ip=user_ip, port=values['port'], key=values['key'])
  if response is not None:
    return response
    
  #Create an event handler and hand off the event to it.
  handler = EventHandler()
  peer, response = handler(values=values, user_ip=user_ip, torrent=torrent, peer=peer)
  if response is not None:
    return response
  
  #Update the ratio
  response = update_ratio(peer, torrent, values.get('amount_downloaded', None), values.get('amount_uploaded', None))
  if response is not None:
    return response
  
  #Find more peers on the same torrent that arent the current peer
  return generate_announce_response(values=values, torrent=torrent, peer=peer)  

def scrape(request):
  #Get all the hashes from the request
  hashes, response = get_cleaned_hashes(request)
  if response is not None:
    return response
  
  #Generate a scrape response from the hashes. Easy peasy!
  return generate_scrape_response(hashes)

