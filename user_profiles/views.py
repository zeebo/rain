from rain.decorators import login_required
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils.importlib import import_module
from django.views.generic.list_detail import object_list, object_detail

class Table(object):
  def __init__(self, table_dict):
    self.title = table_dict.get('title', '')
    self.headers = table_dict.get('headers', [])
    self.rows = table_dict.get('rows', [])

class Profile(object):
  def __init__(self, user):
    self.user = user
    self.tables = []
  
  def add_table(self, table_dict):
    self.tables.append(Table(table_dict))

def get_context(user):
  profile_object = Profile(user)
  for app in settings.INSTALLED_APPS:
    try:
      getattr(import_module("%s.user_profile" % app), 'add_profile')(profile_object)
    except (AttributeError, ImportError):
      pass
  
  return profile_object

@login_required
def user_list(*args, **kwargs):
  return object_list(template_name="user_profiles/user_list.html", *args, **kwargs)

@login_required
def user_profile(request, *args, **kwargs):
  user = get_object_or_404(User, username=kwargs['slug'])
  extra_context = {'profile': get_context(user)}
  return object_detail(request=request,
                       extra_context=extra_context,
                       template_name="user_profiles/user_detail.html",
                       slug_field="username",
                       *args, **kwargs)