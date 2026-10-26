from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import RegisterForm, ServiceForm, SlotForm, BookingForm, ReviewForm
from .models import Profile, Service, AvailabilitySlot, Booking, Review

def role_of(user):
    if user.is_superuser:
        return "admin"
    try:
        return user.profile.role
    except Profile.DoesNotExist:
        return "customer"

def home(request):
    services = Service.objects.filter(active=True).select_related("provider")
    return render(request, "home.html", {"services": services})

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created.")
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})

@login_required
def dashboard(request):
    role = role_of(request.user)
    if role in ("provider", "admin"):
        services = Service.objects.all() if role == "admin" else Service.objects.filter(provider=request.user)
        bookings = Booking.objects.filter(slot__service__in=services).select_related("customer", "slot__service")
        slots = AvailabilitySlot.objects.filter(service__in=services).select_related("service")
        return render(request, "dashboard_provider.html", {"services": services, "bookings": bookings, "slots": slots, "role": role})
    bookings = Booking.objects.filter(customer=request.user).select_related("slot__service", "slot__service__provider")
    return render(request, "dashboard_customer.html", {"bookings": bookings})

def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk, active=True)
    slots = service.slots.filter(is_active=True, start_time__gte=timezone.now()).order_by("start_time")
    reviews = service.reviews.select_related("customer")
    form = ReviewForm()
    return render(request, "service_detail.html", {"service": service, "slots": slots, "reviews": reviews, "review_form": form})

@login_required
def add_service(request):
    if role_of(request.user) != "provider":
        return HttpResponseForbidden("Only service providers can add services.")
    form = ServiceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        service = form.save(commit=False)
        service.provider = request.user
        service.save()
        messages.success(request, "Service created. Add available time slots next.")
        return redirect("dashboard")
    return render(request, "form_page.html", {"form": form, "title": "Add a service", "button": "Save service"})

@login_required
def add_slot(request):
    if role_of(request.user) != "provider":
        return HttpResponseForbidden("Only service providers can add time slots.")
    form = SlotForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        slot = form.save(commit=False)
        if slot.start_time <= timezone.now():
            form.add_error("start_time", "Choose a future time.")
        else:
            try:
                slot.save()
                messages.success(request, "Availability slot added.")
                return redirect("dashboard")
            except IntegrityError:
                form.add_error(None, "This time slot already exists.")
    return render(request, "form_page.html", {"form": form, "title": "Add availability", "button": "Add slot"})

@login_required
def book_slot(request, slot_id):
    slot = get_object_or_404(AvailabilitySlot.objects.select_related("service"), pk=slot_id, is_active=True)
    if role_of(request.user) != "customer":
        messages.error(request, "Only customer accounts can book services.")
        return redirect("service_detail", pk=slot.service_id)
    if request.method != "POST":
        return redirect("service_detail", pk=slot.service_id)
    form = BookingForm(request.POST)
    if form.is_valid():
        try:
            with transaction.atomic():
                # OneToOne constraint on slot is the final protection against duplicate bookings.
                slot = AvailabilitySlot.objects.select_for_update().get(pk=slot_id, is_active=True)
                if slot.start_time <= timezone.now() or Booking.objects.filter(slot=slot, status__in=["pending", "confirmed", "completed"]).exists():
                    messages.error(request, "Sorry, that slot is no longer available.")
                else:
                    booking = form.save(commit=False)
                    booking.customer = request.user
                    booking.slot = slot
                    booking.save()
                    messages.success(request, "Booking request submitted.")
        except (IntegrityError, AvailabilitySlot.DoesNotExist):
            messages.error(request, "This slot was just booked by someone else. Please choose another.")
    else:
        messages.error(request, "Please check the booking details.")
    return redirect("service_detail", pk=slot.service_id)

@login_required
def update_booking_status(request, pk):
    booking = get_object_or_404(Booking.objects.select_related("slot__service"), pk=pk)
    if request.method != "POST" or (role_of(request.user) != "admin" and booking.slot.service.provider_id != request.user.id):
        return HttpResponseForbidden("Not allowed.")
    new_status = request.POST.get("status")
    if new_status in dict(Booking.STATUS_CHOICES):
        booking.status = new_status
        booking.save(update_fields=["status"])
        if new_status == "cancelled":
            # Keep history, but make the slot bookable again.
            booking.slot.is_active = True
            booking.slot.save(update_fields=["is_active"])
        messages.success(request, "Booking status updated.")
    return redirect("dashboard")

@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, customer=request.user)
    if request.method == "POST" and booking.status in ("pending", "confirmed"):
        booking.status = "cancelled"
        booking.save(update_fields=["status"])
        booking.slot.is_active = True
        booking.slot.save(update_fields=["is_active"])
        messages.success(request, "Booking cancelled.")
    return redirect("dashboard")

@login_required
def add_review(request, pk):
    service = get_object_or_404(Service, pk=pk, active=True)
    completed = Booking.objects.filter(customer=request.user, slot__service=service, status="completed").exists()
    if request.method == "POST" and completed:
        form = ReviewForm(request.POST)
        if form.is_valid():
            Review.objects.update_or_create(service=service, customer=request.user,
                defaults={"rating": form.cleaned_data["rating"], "comment": form.cleaned_data["comment"]})
            messages.success(request, "Thank you for your review.")
    else:
        messages.error(request, "A completed booking is required to review this service.")
    return redirect("service_detail", pk=pk)

def available_slots_api(request, service_id):
    slots = AvailabilitySlot.objects.filter(service_id=service_id, is_active=True, start_time__gte=timezone.now()).order_by("start_time")
    data = [{"id": s.id, "start": timezone.localtime(s.start_time).strftime("%d %b %Y, %I:%M %p"),
             "end": timezone.localtime(s.end_time).strftime("%I:%M %p")} for s in slots if not Booking.objects.filter(slot=s, status__in=["pending","confirmed","completed"]).exists()]
    return JsonResponse({"slots": data})
