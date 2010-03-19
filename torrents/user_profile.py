from models import Torrent

def add_profile(profile_object):
  queryset = Torrent.objects.filter(uploaded_by=profile_object.user)
  if queryset.exists():
    
    torrentinfo_dict = {'title': 'Uploaded torrents', 'headers': ('Info hash', 'Description', 'Completed'), 'rows': []}
    
    for info in queryset:
      torrentinfo_dict['rows'].append( (info.info_hash, info.description, info.downloaded) )
      
    profile_object.add_table(torrentinfo_dict)

