from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.template import RequestContext
from django.http import HttpResponseRedirect
from models import Invite
from forms import RegistrationForm
import datetime

def registration_view(request):
  hash_code = request.GET.get('code', None)
  try:
    invite = Invite.objects.filter(active=True).get(hash_code=hash_code)
  except Invite.DoesNotExist:
    return render_to_response('invite_registration/invalid.html')
  
  if request.method == 'POST':
    form = RegistrationForm(request.POST)
    if form.is_valid():
      new_user = User.objects.create_user(form.data['username'], '', form.data['password'])
      invite.child = new_user
      invite.active = False
      invite.join_date = datetime.datetime.now()
      
      invite.save()
      new_user.save()
      
      return HttpResponseRedirect(new_user.get_absolute_url())
      
  else:
    form = RegistrationForm()
  return render_to_response('invite_registration/register.html', {'form': form, 'code': hash_code}, context_instance=RequestContext(request))