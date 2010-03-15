from django.contrib import admin
from rain.invite_registration.models import Invite

class InviteAdmin(admin.ModelAdmin):
  list_display = ('hash_code', 'owner', 'child', 'active')

admin.site.register(Invite, InviteAdmin)