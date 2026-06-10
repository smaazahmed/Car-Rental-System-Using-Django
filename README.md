# Car Rental System Using Django

This is a Django-based car rental web application where users can browse cars, register and log in, manage profiles, save favorites, create bookings, view receipts, and leave reviews. Admin users can manage cars and bookings from dedicated dashboards.

## Features

- User registration, login, logout, and profile editing
- Car browsing with search, filters, sorting, and suggestions
- Favorites/wishlist support
- Booking checkout, confirmation, and receipt generation
- Review creation and deletion
- Admin car management and booking actions
- Basic revenue and dashboard analytics

## Requirements

- Python 3.11+ recommended
- Django 6.x
- Pillow for image uploads

Install the Python dependencies with:

```powershell
pip install -r requirements.txt
```

## How To Run

1. Open PowerShell in the project root.
2. Create and activate a virtual environment if needed:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Apply database migrations:

```powershell
python manage.py migrate
```

5. Load sample data if you want test cars/bookings:

```powershell
python seed_data.py
```

6. Start the development server:

```powershell
python manage.py runserver
```

7. Open the app in your browser:

```text
http://127.0.0.1:8000/
```

## Default App Flow

- Home page: `http://127.0.0.1:8000/`
- Car listing: `http://127.0.0.1:8000/cars/explore/`
- Register: `http://127.0.0.1:8000/accounts/register/`
- Login: `http://127.0.0.1:8000/accounts/login/`
- Customer dashboard: `http://127.0.0.1:8000/accounts/my-dashboard/`
- Admin dashboard: `http://127.0.0.1:8000/admin-dashboard/`

## Demo Credentials

If you run `python seed_data.py`, the following demo accounts are created:

- Admin: `admin` / `admin123`
- Customer: `customer` / `customer123`

Demo account emails:

- Admin: `admin@driveluxrentals.com`
- Customer: `customer@gmail.com`

## Project Structure

### Root files

- `manage.py`  
  Django command-line entry point used for migrations, running the server, and other project commands.

- `db.sqlite3`  
  SQLite database used during development.

- `requirements.txt`  
  Python package list for the project.

- `seed_data.py`  
  Script used to populate the database with sample data.

- `index.html` and `styles.css`  
  Standalone front-end assets kept in the project root. These appear to be legacy or reference files and are separate from the Django template system.

### `car_rental_project/`

This is the Django project configuration folder.

- `settings.py`  
  Project settings: installed apps, database, templates, static/media settings, authentication redirects, and email backend.

- `urls.py`  
  Root URL router. It connects the `core`, `accounts`, `cars`, and `bookings` apps.

- `asgi.py` / `wsgi.py`  
  Deployment entry points for ASGI and WSGI servers.

### `apps/core/`

This app contains the public pages and admin dashboard logic.

- `views.py`  
  Handles the home page, about page, contact page, dashboard redirect, admin dashboard, and revenue API.

- `urls.py`  
  Routes the public and dashboard endpoints.

- `models.py`  
  Currently minimal/no major business models in this app.

- `templates/core/`  
  Page templates for the home, about, contact, and admin dashboard views.

### `apps/accounts/`

This app handles authentication, user profiles, and favorites.

- `models.py`  
  Defines `UserProfile`, which stores role, phone number, address, profile picture, and favorite cars.

- `forms.py`  
  Registration and profile update forms.

- `views.py`  
  Registration, login, logout, customer dashboard, profile editing, and wishlist toggle logic.

- `urls.py`  
  Account-related routes.

- `migrations/`  
  Database schema changes for account-related models.

- `templates/accounts/`  
  Templates for login, registration, dashboard, and profile pages.

### `apps/cars/`

This app manages car inventory, car details, reviews, and admin car CRUD actions.

- `models.py`  
  Defines `Car`, `CarImage`, and `Review`.

- `forms.py`  
  Forms for adding/editing cars and submitting reviews.

- `views.py`  
  Handles car listing, detail pages, search suggestions, review posting, review deletion, and admin car management.

- `urls.py`  
  Car browsing, review, and admin car routes.

- `migrations/`  
  Database schema changes for car-related models.

- `templates/cars/`  
  Templates for car listing, detail pages, partial AJAX rendering, and admin car forms.

### `apps/bookings/`

This app handles booking creation, checkout, receipts, payment records, and admin booking actions.

- `models.py`  
  Defines `Booking` and `Payment`.

- `views.py`  
  Handles checkout initialization, booking confirmation, receipt generation, admin booking actions, and car availability API responses.

- `urls.py`  
  Booking and booking-admin routes.

- `migrations/`  
  Database schema changes for booking-related models.

- `templates/bookings/`  
  Checkout and receipt templates.

### `templates/`

Global template directory used by Django.

- `base.html`  
  Shared layout used by multiple pages.

- Subfolders like `accounts/`, `bookings/`, `cars/`, and `core/`  
  Group templates by app for easier maintenance.

### `static/`

Static assets served by Django during development.

- `static/css/style.css`  
  Main site styling.

- `static/js/main.js`  
  Front-end behavior, likely including dynamic UI interactions.

## How The App Is Organized

- The project-level URL configuration in `car_rental_project/urls.py` sends requests to app-level routers.
- `core` handles the public landing pages and dashboards.
- `accounts` manages authentication and user profile features.
- `cars` handles inventory browsing, search, reviews, and admin vehicle management.
- `bookings` handles checkout, availability checks, payment recording, and receipts.
- Templates are separated by app so each feature has its own HTML pages.
- Static CSS and JavaScript live in `static/` and are shared across the site.

## Notes

- The app uses SQLite by default through `db.sqlite3`.
- File uploads such as profile pictures and car images use the `media/` directory at runtime.
- Email notifications are simulated through the Django console email backend, so booking emails are printed to the terminal during development.
- Admin-only pages check the logged-in user profile role before allowing access.

## Helpful Commands

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
