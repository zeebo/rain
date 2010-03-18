from models import UserIP

class UpdateUserIPMiddleware(object):
  def process_request(self, request):
    if request.user is not None and request.user.is_authenticated():
      ip = request.META['REMOTE_ADDR']
      
      #Get the userip object with that ip and update it to the current user (steal that ip! screws with ratios! dont care!)
      obj, created = UserIP.objects.get_or_create(ip=ip)
      obj.user = request.user
      obj.save()
    
    return None