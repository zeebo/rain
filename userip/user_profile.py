from models import UserIP

def add_profile(profile_object):
  queryset = UserIP.objects.filter(user=profile_object.user)
  if queryset.exists():
    
    useripinfo_dict = {'title': 'User IP Addresses', 'headers': ('IP', ), 'rows': []}
    
    for info in queryset:
      useripinfo_dict['rows'].append( (info.ip, ) )
      
    profile_object.add_table(useripinfo_dict)

