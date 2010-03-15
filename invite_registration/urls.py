from django.conf.urls.defaults import *
from django.http import HttpResponse

urlpatterns = patterns('',
  (r'^register$', 'invite_registration.views.registration_view'),
  (r'^users/newuser/$', lambda x: HttpResponse() ), #hack to pass even if they dont have 404.html
)