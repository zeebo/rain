from rain.torrents.forms import UploadTorrentForm
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.list_detail import object_list, object_detail
from rain.decorators import login_required

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
      #change this to use message framework
      return HttpResponse('Got the file')
  else:
    form = UploadTorrentForm()
  return render_to_response('torrents/upload_torrent.html', {'form': form}, context_instance=RequestContext(request))