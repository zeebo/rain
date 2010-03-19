from models import Invite

def add_profile(profile_object):
  queryset = Invite.objects.filter(owner=profile_object.user).filter(active=False)
  if queryset.exists():
    inviteinfo_dict = {'title': 'Invited Users', 'headers': ('Username', 'Join Date'), 'rows': []}
    
    for info in queryset.order_by('-join_date'):
      inviteinfo_dict['rows'].append( (info.child.username, info.join_date) )
      
    profile_object.add_table(inviteinfo_dict)

