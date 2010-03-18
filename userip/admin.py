from django.contrib import admin
from models import UserIP

class UserIPAdmin(admin.ModelAdmin):
  list_display = ('user', 'ip')

admin.site.register(UserIP, UserIPAdmin)