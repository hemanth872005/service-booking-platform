from django.contrib import admin
from .models import Profile, Service, AvailabilitySlot, Booking, Review
admin.site.register(Profile)
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "provider", "price", "active")
    list_filter = ("category", "active")
    search_fields = ("name", "description", "provider__username")
@admin.register(AvailabilitySlot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ("service", "start_time", "end_time", "is_active")
    list_filter = ("is_active",)
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "slot", "status", "created_at")
    list_filter = ("status",)
admin.site.register(Review)
