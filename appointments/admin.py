from django.contrib import admin

from .models import Doctor, AvailabilityPeriod, AvailabilityRange, Appointment, CustomAvailability

admin.site.register(Doctor)
admin.site.register(AvailabilityPeriod)
admin.site.register(AvailabilityRange)
admin.site.register(CustomAvailability)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ["doctor", "date", "start_time", "patient_name", "status"]
    list_filter = ["status", "date"]
    search_fields = ["patient_name", "patient_phone"]
