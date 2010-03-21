from forms import UploadTorrentForm
from models import Torrent
from utils import bencode, bdecode
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic.list_detail import object_list, object_detail
from rain.decorators import login_required
from django.contrib.sites.models import Site
from django.contrib import messages
from django.core.urlresolvers import reverse

@login_required
def download_torrent(request, object_id):
  torrent = get_object_or_404(Torrent, pk=object_id)
  
  #load the file into memory
  data = torrent.torrent.read()
  decoded_data = bdecode(data)
  
  #set the tracker, reverse announce url
  announce_url = 'http://%s%s' % (Site.objects.get_current().domain, reverse('tracker.views.announce'))
  decoded_data['announce'] = announce_url
  
  #generate a response with correct mimetype and file as the attachment
  response = HttpResponse(mimetype='application/x-bittorrent')
  response['Content-Disposition'] = 'attachment; filename=%s.torrent' % torrent.info_hash
  response.write(bencode(decoded_data))
  
  return response

@login_required
def torrent_list(*args, **kwargs):
  return object_list(*args, **kwargs)

@login_required
def torrent_detail(*args, **kwargs):
  return object_detail(*args, **kwargs)

@login_required
def upload_torrent(request):
  if request.method == 'POST':
    form = UploadTorrentForm(request.POST, request.FILES)
    if form.is_valid():
      new_torrent = form.save(commit=False)
      new_torrent.uploaded_by = request.user
      new_torrent.save()
      
      messages.success(request, 'Torrent has been uploaded.')
      
      return HttpResponseRedirect(reverse(torrent_list))
  else:
    form = UploadTorrentForm()
  return render_to_response('torrents/upload_torrent.html', {'form': form}, context_instance=RequestContext(request))