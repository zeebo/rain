from django.conf.urls.defaults import *
from django.contrib import admin
from rain.announce.views import announce
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^announce/', announce),
)
