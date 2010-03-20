from django.conf import settings
from django.contrib.sites.models import Site

def add_domain(request):
    try:
        current_domain = Site.objects.get_current().domain
        return {'domain': "http://%s" % current_domain}
    except Site.DoesNotExist:
        return {'domain': 'poop'}