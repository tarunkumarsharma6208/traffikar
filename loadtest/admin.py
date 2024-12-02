from django.contrib import admin
from loadtest.models import *

# Register your models here.
admin.site.register(LoadTest)

@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ('url', 'status_code', 'timestamp')
    list_filter = ('status_code', 'timestamp')
    search_fields = ('url',)