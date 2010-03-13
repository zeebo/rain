from django.conf.urls.defaults import *
from django.contrib import admin
from rain.tracker.views import announce, scrape, upload_torrent
from rain.settings import MEDIA_ROOT
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^announce$', announce),
    (r'^scrape$', scrape),
    (r'^upload$', upload_torrent),
    (r'^accounts/login/$', 'django.contrib.auth.views.login')
    #(r'^tracker/media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}), #probably security vuln but ok for now.
)
