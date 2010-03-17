from django.http import HttpResponseRedirect

def simple_decorator(decorator):
  def new_decorator(f):
    g = decorator(f)
    g.__name__ = f.__name__
    g.__doc__ = f.__doc__
    g.__dict__.update(f.__dict__)
    return g
  new_decorator.__name__ = decorator.__name__
  new_decorator.__doc__ = decorator.__doc__
  new_decorator.__dict__.update(decorator.__dict__)
  return new_decorator

@simple_decorator
def login_required(view):
  from django.conf import settings
  login_url = settings.LOGIN_URL
  
  def new_view(request, *args, **kwargs):
    if request.user.is_authenticated():
      return view(request, *args, **kwargs)
    return HttpResponseRedirect(login_url)
  
  return new_view