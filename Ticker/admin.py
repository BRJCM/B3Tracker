from django.contrib import admin
from .models import Ticker
# Register your models here.

class TickerAdmin(admin.ModelAdmin):
    
    list_display = ('user','ticker','price','lower_bound','upper_bound', 'interval', 'last_update', 'investor_email') 
    
admin.site.register(Ticker, TickerAdmin)

# Register your models here.
