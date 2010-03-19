from models import RatioInfo, UserRatio

def add_profile(profile_object):
  queryset = RatioInfo.objects.filter(user=profile_object.user)
  if queryset.exists():
    ratioinfo_dict = {'title': 'Torrent Ratios', 'headers': ('Info hash', 'Downloaded', 'Uploaded', 'Ratio'), 'rows': []}
    
    for info in queryset.order_by('-last_updated')[:10]:
      ratioinfo_dict['rows'].append( (info.info_hash, info.download_size(), info.upload_size(), info.ratio()) )
      
    profile_object.add_table(ratioinfo_dict)
    
    user_ratio = UserRatio.objects.get(user=profile_object.user)
    
    profile_object.add_table({
      'title': 'Overall Ratio',
      'headers': ('Downloaded', 'Uploaded', 'Ratio'),
      'rows': [(user_ratio.download_size(), user_ratio.upload_size(), user_ratio.ratio())]
    })

