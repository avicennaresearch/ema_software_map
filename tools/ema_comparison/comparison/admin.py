from django.contrib import admin
from ema_comparison.base_admin import BaseAdmin
from comparison.models import Url
from comparison.models import Software

# Register your models here.
@admin.register(Software)
class SoftwareAdmin(BaseAdmin):
    list_per_page = 10
    list_display = (
        "id",
        "name",
    )
    search_fields = ("name", )

@admin.register(Url)
class UrlAdmin(BaseAdmin):
    list_per_page = 30
    list_display = (
        "id",
        "url",
        "software",
        "last_updated",
        "is_monitored",
    )
    search_fields = ("url",)
    readonly_fields = (
        "id",
        "ai_summary"

    )