from django.contrib import admin
from .models import AdvUser

class AdvUserAdmin(admin.ModelAdmin):
    exclude = ('slug',)

admin.site.register(AdvUser, AdvUserAdmin)