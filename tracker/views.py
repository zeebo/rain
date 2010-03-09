# Create your views here.
from django.http import HttpResponse
from rain import utils
def announce(request):
  return HttpResponse(utils.bencode({'failure-reason':'owned'}), mimetype='text/plain')

