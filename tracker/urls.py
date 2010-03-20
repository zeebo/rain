from django.conf.urls.defaults import *

urlpatterns = patterns('tracker.views',
  (r'announce$', 'announce'),
  (r'scrape$', 'scrape'),
)