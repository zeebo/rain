# Create your views here.
from django.http import HttpResponse

def announce(request):
  import logging
  logging.error(request.GET.lists())
  return HttpResponse('owned')