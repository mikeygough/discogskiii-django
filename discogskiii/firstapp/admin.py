from django.contrib import admin

from firstapp.models import MasterRelease, MainRelease, SavedMarkets

# Register your models here.
admin.site.register(MasterRelease)
admin.site.register(MainRelease)
admin.site.register(SavedMarkets)