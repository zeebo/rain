from rain.tracker.forms import UploadTorrentForm
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from rain.tracker.utils import *

@login_required
def upload_torrent(request):
  if request.method == 'POST':
    form = UploadTorrentForm(request.POST, request.FILES)
    if form.is_valid():
      new_torrent = form.save(commit=False)
      new_torrent.uploaded_by = request.user
      new_torrent.save()
      return HttpResponse('Got the file')
  else:
    form = UploadTorrentForm()
  return render_to_response('tracker/upload_torrent.html', {'form': form}, context_instance=RequestContext(request))

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

