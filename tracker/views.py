from utils import *
#from rain.profiler import profile
#@profile('announce.prof')
def announce(request):
  #Parse the request and return any errors
  values, response = parse_request(request)
  if response is not None:
    return tracker_error(response)
  
  #authenticate the user. implement hooks
  user, response = authenticate_user(request)
  if response is not None:
    return tracker_error(response)
  
  #authenticate the info_hash. implement hooks
  response = authenticate_torrent(values['info_hash'])
  if response is not None:
    return tracker_error(response)
  
  #Find the peer that matches the request, or none if it is new
  peer, response = find_matching_peer(info_hash=values['info_hash'], user=user, port=values['port'], key=values['key'])
  if response is not None:
    return tracker_error(response)
    
  #Create an event handler and hand off the event to it.
  peer, response = handle_events(values=values, user=user, peer=peer)
  if response is not None:
    return tracker_error(response)
  
  #If we dont have a peer at this point, we've stopped the torrent
  if peer is None:
    return tracker_response('')
  
  #Find more peers on the same torrent that arent the current peer
  return generate_announce_response(values=values, peer=peer)  

def scrape(request):
  #Get all the hashes from the request
  hashes, response = get_cleaned_hashes(request)
  if response is not None:
    return tracker_error(response)
  
  for a_hash in hashes:
    response = authenticate_torrent(a_hash)
    if response is not None:
      return tracker_error(response)
  
  #Generate a scrape response from the hashes. Easy peasy!
  return generate_scrape_response(hashes)

