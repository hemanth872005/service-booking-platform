# ServiceHub — Service Booking and Management Platform

A complete educational full-stack project based on the uploaded presentation. It uses **only the presentation's technologies**: Python 3, Django, Django ORM/migrations, SQLite, HTML5, CSS3, Bootstrap, JavaScript/AJAX (`fetch`), Git/GitHub, VS Code and Postman. Bootstrap is loaded from its official CDN, so internet access is needed for the styling.

## Features
- Customer and service-provider registration/login using Django authentication.
- Role-aware dashboards and server-side access checks.
- Service catalogue, category/search filtering, service detail pages and pricing.
- Providers can add services and future availability slots.
- Customers can request a booking, view booking history and cancel pending/confirmed bookings.
- Providers can update booking status to pending, confirmed, completed or cancelled.
- AJAX endpoint for live slot count.
- Reviews (one per customer/service; only after a completed booking).
- SQLite persistence, Django admin, form validation, CSRF protection and database uniqueness constraints.
- Atomic booking transaction plus a conditional database uniqueness constraint on active bookings to prevent duplicate bookings.

## Setup (Windows PowerShell)
1. Install Python 3.11 or newer and open this folder in VS Code.
2. Create and activate a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, use `\.venv\Scripts\python.exe` directly in the commands below.
3. Install dependency:
   ```powershell
   python -m pip install -r requirements.txt
   ```
4. Create database tables:
   ```powershell
   python manage.py makemigrations bookings
   python manage.py migrate
   ```
5. Create an admin account:
   ```powershell
   python manage.py createsuperuser
   ```
6. Start the server:
   ```powershell
   python manage.py runserver
   ```
7. Visit `http://127.0.0.1:8000/`. Admin site: `http://127.0.0.1:8000/admin/`.

## First demo walkthrough
1. Register a user with role **Service Provider**.
2. Log in and add a service (e.g. “Home Appliance Repair”, category “Home Services”, price `500`, duration `60`).
3. Add one or more future availability slots.
4. Log out and register a second user with role **Customer**.
5. Browse the service and request a booking.
6. Log back in as provider and update the request to Confirmed, then Completed.
7. Log in as customer again and submit a review on the service detail page.
8. Use the dashboard to demonstrate status history; use `/admin/` to inspect stored records.

## Useful routes
- `/` service catalogue
- `/register/`, `/login/`, `/logout/`
- `/dashboard/`
- `/provider/services/add/`
- `/provider/slots/add/`
- `/services/<id>/`
- `/api/services/<id>/slots/` (JSON availability response)
- `/admin/`

## Postman checks
Run the Django server first. Test:
- `GET http://127.0.0.1:8000/` → `200 OK`
- `GET http://127.0.0.1:8000/api/services/1/slots/` → JSON `{ "slots": [...] }` (use a real service ID)
- `GET http://127.0.0.1:8000/services/1/` → `200 OK` (use a real service ID)
- Unauthenticated `GET /dashboard/` → redirects to login.
For POST forms, use the browser initially because Django CSRF protection is enabled. For direct Postman POST tests, obtain and send a valid CSRF cookie/token.

## Git / GitHub
```powershell
git init
git add .
git commit -m "Initial ServiceHub implementation"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/servicehub.git
git push -u origin main
```

## Notes and production hardening
- This is a local educational prototype. `DEBUG=True` and the development `SECRET_KEY` are for local use only. Before deployment, set environment variables, disable debug, configure allowed hosts, HTTPS, secure cookies, logging, backups and a production database.
- SQLite is suitable for a demo. Database row-lock semantics vary by database; the `OneToOneField` uniqueness constraint is the final duplicate-booking safeguard.
- A production version should add email verification/password reset, provider availability conflict detection across overlapping intervals, payment integration only if required, rate limiting, and automated tests.
- This implementation uses no external framework beyond Django and Bootstrap. No React, Node.js, MySQL, APIs requiring keys, or third-party backend is required.
