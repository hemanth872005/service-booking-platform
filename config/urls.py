from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from bookings import views
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("services/<int:pk>/", views.service_detail, name="service_detail"),
    path("provider/services/add/", views.add_service, name="add_service"),
    path("provider/slots/add/", views.add_slot, name="add_slot"),
    path("book/<int:slot_id>/", views.book_slot, name="book_slot"),
    path("booking/<int:pk>/status/", views.update_booking_status, name="update_booking_status"),
    path("booking/<int:pk>/cancel/", views.cancel_booking, name="cancel_booking"),
    path("services/<int:pk>/review/", views.add_review, name="add_review"),
    path("api/services/<int:service_id>/slots/", views.available_slots_api, name="available_slots_api"),
]
