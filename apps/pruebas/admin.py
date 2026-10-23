from django.contrib import admin

# Register your models here.

from .models import Protocolo


@admin.register(Protocolo)
class ProtocoloAdmin(admin.ModelAdmin):
    list_display = ("nombreProtocolo", "activo")
    list_filter = ("activo",)
    search_fields = ("nombreProtocolo",)
