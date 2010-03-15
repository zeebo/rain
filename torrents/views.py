from rain.tracker.forms import UploadTorrentForm
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

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