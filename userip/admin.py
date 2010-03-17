from django.contrib import admin
from rain.userip.models import UserIP

class UserIPAdmin(admin.ModelAdmin):
  list_display = ('user', 'ip')

admin.site.register(UserIP, UserIPAdmin)