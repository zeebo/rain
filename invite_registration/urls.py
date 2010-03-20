from django.conf.urls.defaults import *
from django.http import HttpResponse
from django.conf import settings

urlpatterns = patterns('',
  (r'^register$', 'invite_registration.views.registration_view'),
  (r'^%s$' % settings.LOGIN_REDIRECT_URL, lambda x: HttpResponse('lol')),
)