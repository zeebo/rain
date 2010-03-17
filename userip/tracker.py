from rain.userip.models import UserIP

def authorize_user(request, queryset):
  try:
    userip = UserIP.objects.filter(ip=request.META['REMOTE_ADDR']).get()
    return queryset.filter(pk=userip.user.pk)
  except (UserIP.MultipleObjectsReturned, UserIP.DoesNotExist):
    return queryset.none()
