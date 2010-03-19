from rain.decorators import login_required
from django.views.generic.list_detail import object_list, object_detail

class Profile(object):
  def __init__(self, user):
    self._user = user
    self.table_headers = []
    self.tables = []
  
  @property
  def user(self):
    return self._user
  
  def add_table(self, table_dict):
    self.table_headers.append(table_dict['header'])
    self.tables.append(table_dict)
  
  def yield_tables(self):
    for i, table in enumerate(self.tables):
      self._current_table = i
      yield table
  
  def yield_headers(self):
    return self.tables[self._current_table]['header']
  
  def yield_titles(self):
    for title in self.tables[self._current_table]['titles']:
      yield title
  
  def yield_rows(self):
    for i, row in enumerate(self.tables[self._current_table]['values']):
      yield row
      
@login_required
def user_list(*args, **kwargs):
  return object_list(template_name="user_profiles/user_list.html", *args, **kwargs)

@login_required
def user_profile(*args, **kwargs):
  return object_detail(template_name="user_profiles/user_detail.html", slug_field="username", *args, **kwargs)