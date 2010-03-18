from django.contrib import admin
from models import Invite

class InviteAdmin(admin.ModelAdmin):
  list_display = ('hash_code', 'owner', 'child', 'active')

admin.site.register(Invite, InviteAdmin)