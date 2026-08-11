from django.contrib import admin

# Register your models here.
from .models import User, ProviderProfile

admin.site.register(User)


@admin.register(ProviderProfile)
class ProviderProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "service_type", "employer", "approved"]
    list_filter = ["service_type", "approved"]
    list_editable = ["approved"]
    search_fields = ["user__phone_number", "user__first_name", "user__last_name"]