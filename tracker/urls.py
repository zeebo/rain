from django.conf.urls.defaults import *

urlpatterns = patterns('rain.tracker.views',
  (r'announce$', 'announce'),
  (r'scrape$', 'scrape'),
)