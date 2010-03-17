from django.conf.urls.defaults import *
from django.contrib.auth.models import User

info_dict = {
  'queryset': User.objects.all(),
}

urlpatterns = patterns('',
  (r'^$', 'rain.user_profiles.views.user_list', info_dict),
  (r'^(?P<slug>.*)/$', 'rain.user_profiles.views.user_profile', info_dict),
) 