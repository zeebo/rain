from django.contrib import admin
from models import RatioInfo, UserRatio
from rain.admin import ReadOnlyModelAdmin

class RatioInfoAdmin(ReadOnlyModelAdmin):
  list_display = ('user', 'info_hash', 'download_size', 'upload_size', 'ratio')

class UserRatioAdmin(admin.ModelAdmin):
  list_display = ('user', 'download_size', 'upload_size', 'ratio')

admin.site.register(RatioInfo, RatioInfoAdmin)
admin.site.register(UserRatio, UserRatioAdmin)