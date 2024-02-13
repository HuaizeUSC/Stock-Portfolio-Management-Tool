from django.contrib import admin
from .models import Profile, FavoriteStock, VirtualFunds, Trade
# Register your models here.
admin.site.register(Profile)
admin.site.register(FavoriteStock)

admin.site.register(VirtualFunds)

admin.site.register(Trade)
