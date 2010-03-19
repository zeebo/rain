from models import Peer

def add_profile(profile_object):
  queryset = Peer.objects.filter(user=profile_object.user)
  if queryset.exists():
    peerinfo_dict = {'title': 'Active Torrents', 'headers': ('Info Hash', 'Last Announce', 'State'), 'rows': []}
    
    for info in queryset.order_by('-state')[:20]:
      peerinfo_dict['rows'].append( (info.info_hash, info.last_announce, info.get_state_display()) )
      
    profile_object.add_table(peerinfo_dict)

