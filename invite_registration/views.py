from django.shortcuts import get_object_or_404
from django.http raise Http404
from models import Invite
from forms import RegistrationForm

def registration_view(request):
  hash_code = request.GET.get('code', None)
  invite = get_object_or_404(hash_code=hash_code)
  
  if not invite.active:
    raise Http404
  
  if request.method == 'POST':
    form = RegistrationForm(request.POST)
    if form.is_valid():
      return HttpResponse('Valid user!')
  else:
    form = RegistrationForm()
  return render_to_response('invite_registration/register.html', {'form': form, 'code': hash_code})