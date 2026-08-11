from django.contrib import admin

from .models import Cause, CauseDocument


class CauseDocumentInline(admin.TabularInline):
    model = CauseDocument
    extra = 0


@admin.register(Cause)
class CauseAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "submitted_by", "goal_amount", "approved", "created_at"]
    list_filter = ["approved", "category"]
    search_fields = ["name", "submitted_by__phone_number", "submitted_by__first_name", "submitted_by__last_name"]
    list_editable = ["approved"]
    inlines = [CauseDocumentInline]
