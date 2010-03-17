# Create your views here.
from rain.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic.list_detail import object_list, object_detail

@login_required
def user_list(*args, **kwargs):

  return object_list(template_name="user_profiles/user_list.html", *args, **kwargs)

@login_required
def user_profile(*args, **kwargs):
  return object_detail(template_name="user_profiles/user_detail.html", slug_field="username", *args, **kwargs)