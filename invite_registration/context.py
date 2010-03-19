def add_new_invites(request):
  if request.user.is_authenticated():
    return {'new_invites': request.user.owner_id.filter(active=True).count()}
  return {}