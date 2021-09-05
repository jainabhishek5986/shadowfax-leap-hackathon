from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Hub)
class HubAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'address')
