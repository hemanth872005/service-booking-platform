from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

class Profile(models.Model):
    ROLE_CHOICES = [("customer", "Customer"), ("provider", "Service Provider")]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=12, choices=ROLE_CHOICES, default="customer")
    phone = models.CharField(max_length=20, blank=True)
    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Service(models.Model):
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=80)
    description = models.TextField()
    price = models.DecimalField(max_digits=9, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(default=60)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["category", "name"]
    def __str__(self):
        return self.name

class AvailabilitySlot(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="slots")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ["start_time"]
        constraints = [
            models.UniqueConstraint(fields=["service", "start_time", "end_time"], name="unique_service_slot")
        ]
    def __str__(self):
        return f"{self.service.name}: {self.start_time:%d %b %Y, %I:%M %p}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"), ("confirmed", "Confirmed"),
        ("completed", "Completed"), ("cancelled", "Cancelled"),
    ]
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_bookings")
    slot = models.ForeignKey(AvailabilitySlot, on_delete=models.PROTECT, related_name="bookings")
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="pending")
    notes = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["slot"],
                condition=Q(status__in=["pending", "confirmed", "completed"]),
                name="one_active_booking_per_slot",
            )
        ]
    def __str__(self):
        return f"Booking #{self.pk} - {self.slot.service.name}"
    @property
    def is_upcoming(self):
        return self.slot.start_time >= timezone.now() and self.status not in ("cancelled", "completed")

class Review(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="reviews")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["service", "customer"], name="one_review_per_customer_service")]
        ordering = ["-created_at"]
    def __str__(self):
        return f"{self.service.name}: {self.rating}/5"
