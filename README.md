# 🎟️ Event Management & Ticket Booking API

A robust, production-ready RESTful API built with Django and Django REST Framework (DRF) for managing events, ticket bookings, and user profiles.

## 🚀 Key Features

* **User Authentication & Profiles:** Custom registration with automatic `UserProfile` creation and JWT/Token auth support.
* **Role-Based Access Control (RBAC):** Custom permissions ensuring only Organizers/Admins can edit events, and users manage their own bookings.
* **Event Management:** Full CRUD operations for events with category filtering, location search, and date/price ordering.
* **Smart Ticket Booking System:** 
  * Real-time ticket availability checks & custom field validations.
  * Nested serialization (`EventSummarySerializer`) for sleek response payloads.
* **Database Optimization:** Optimized querysets using `select_related` to eliminate N+1 database performance hits.
* **Pagination & Filtering:** Standardized pagination (5 items/page) with `DjangoFilterBackend`, `SearchFilter`, and `OrderingFilter`.

## 🛠️ Tech Stack

* **Backend:** Python 3.x, Django 5.x, Django REST Framework (DRF)
* **Database:** SQLite (Development) / PostgreSQL-ready
* **Filtering:** `django-filter`

## 🔗 API Endpoints

| Method | Endpoint | Description | Permission |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/register/` | Register a new user | Public |
| `GET` / `POST` | `/api/events/` | List all events (with search/filter) / Create Event | Admin/Organizer |
| `GET` / `PUT` / `DELETE` | `/api/events/<id>/` | Event detail, update, delete | Organizer Only |
| `GET` / `POST` | `/api/bookings/` | List user bookings / Book tickets | Authenticated |
| `PUT` | `/api/bookings/<id>/cancel/` | Cancel a booking | Booking Owner |
| `POST` | `/api/events/<id>/book/` | Quick book ticket for event | Authenticated |
| `GET` | `/api/events/my-events/` | List events hosted by logged-in user | Authenticated |
| `GET` | `/api/bookings/my-bookings/` | List bookings made by logged-in user | Authenticated |
| `GET` / `PUT` | `/api/profile/` | Manage user profile | Owner |

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Abdurohman-Dev/event_api_project.git](https://github.com/Abdurohman-Dev/event_api_project.git)
   cd event_api_project