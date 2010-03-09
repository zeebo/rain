# Create your views here.
from django.http import HttpResponse
from django.utils.encoding import smart_str
from rain.tracker.models import Torrent
from rain import utils
def tracker_error_response(value):
  return HttpResponse(utils.bencode({'failure reason':value}), mimetype='text/plain')
  
def announce(request):
  request.encoding = 'iso-8859-1'
  info_hash = request.GET.get('info_hash', '').encode('iso-8859-1').encode('hex')
  try:
    torrent = Torrent.objects.filter(info_hash=info_hash).get()
  except Torrent.MultipleObjectsReturned, Torrent.DoesNotExist:
    return tracker_error_response('Problem with info_hash')
  return tracker_error_response('found torrent. peerlist NYI')

