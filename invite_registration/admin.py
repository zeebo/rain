from django.contrib import admin
from models import Invite

class InviteAdmin(admin.ModelAdmin):
  list_display = ('hash_code', 'owner', 'child', 'active', 'join_date')

admin.site.register(Invite, InviteAdmin)