<div align="center">

# 🚢 NautiCore — Backend API

**Maritime Shipyard Management System**

A production-grade REST API built with Django REST Framework for managing vessel construction projects, spare parts inventory, maintenance scheduling, and more.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?style=flat&logo=django&logoColor=white)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-3.17-a30000?style=flat)](https://django-rest-framework.org)
[![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=flat&logo=jsonwebtokens&logoColor=white)](https://jwt.io)
[![Swagger](https://img.shields.io/badge/Swagger-UI-85EA2D?style=flat&logo=swagger&logoColor=black)](http://127.0.0.1:8000/api/docs/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)

[Live API Docs](#) · [Frontend Repo](https://github.com/Vincent088/nauticore-frontend-react) · [Report Bug](#)

</div>

---

## 📌 Table of Contents

- [About the Application](#-about-the-application)
- [System Overview](#-system-overview)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [Modules](#-modules)
- [API Endpoints](#-api-endpoints)
- [Authentication](#-authentication)
- [Security](#-security)
- [Database](#-database)
- [Seed Data](#-seed-data)
- [Admin Panel](#-admin-panel)
- [Test Accounts](#-test-accounts)

---

## 🌐 About the Application

**NautiCore** is a full-stack Maritime Shipyard Management System designed for ship craft companies. It manages the complete operational lifecycle of a shipyard — from tracking vessel construction projects and managing clients, to controlling spare parts inventory, monitoring progress milestones, handling documents and certifications, and scheduling maintenance for delivered vessels.

### The Full System

| Layer             | Technology                       | Repository                                                                         |
| ----------------- | -------------------------------- | ---------------------------------------------------------------------------------- |
| **Backend API**   | Django REST Framework            | This repo                                                                          |
| **Frontend**      | React 18 + TypeScript            | [nauticore-frontend-react](https://github.com/Vincent088/nauticore-frontend-react) |
| **Database**      | SQLite (dev) / PostgreSQL (prod) | Managed by Django ORM                                                              |
| **Documentation** | Swagger UI / ReDoc               | `/api/docs/`                                                                       |

### Who Uses It

| Role            | Access                                        |
| --------------- | --------------------------------------------- |
| **Admin**       | Full access including user management         |
| **Manager**     | Manage projects and operations                |
| **Engineer**    | Log work, update progress, record maintenance |
| **Procurement** | Manage spare parts and materials              |
| **Viewer**      | Read-only access to everything                |

### Core Modules

```
accounts    → Authentication, users, roles
clients     → Client companies and contacts
vessels     → Vessel projects (main module)
materials   → Spare parts and inventory
progress    → Milestones, tasks, work logs
documents   → Files and certifications
maintenance → Scheduled maintenance and service history
```

---

## 🏗 System Overview

```
┌─────────────────────────────────────────────────────┐
│                   React Frontend                     │
│         (nauticore-frontend repository)              │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP / JSON
                       │ Authorization: Bearer <token>
┌──────────────────────▼──────────────────────────────┐
│              Django REST Framework API               │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────┐ │
│  │  JWT     │  │ Swagger  │  │   Jazzmin Admin    │ │
│  │  Auth    │  │   Docs   │  │   /secret-url/     │ │
│  └──────────┘  └──────────┘  └────────────────────┘ │
│                                                      │
│  accounts │ clients │ vessels │ materials            │
│  progress │ documents │ maintenance                  │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │           core/                                │ │
│  │  BaseModel · validators · permissions          │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│               SQLite / PostgreSQL                    │
└─────────────────────────────────────────────────────┘
```

---

## 🛠 Tech Stack

| Category  | Technology                    | Purpose               |
| --------- | ----------------------------- | --------------------- |
| Language  | Python 3.11                   | Core language         |
| Framework | Django 5.2                    | Web framework         |
| API       | Django REST Framework 3.17    | REST API layer        |
| Auth      | djangorestframework-simplejwt | JWT authentication    |
| Admin UI  | django-jazzmin                | Modern admin theme    |
| Filtering | django-filter                 | Query param filtering |
| CORS      | django-cors-headers           | Cross-origin requests |
| Docs      | drf-spectacular               | Swagger / OpenAPI     |
| Images    | Pillow                        | Image processing      |
| Seed Data | Faker                         | Realistic dummy data  |
| Formatter | Black                         | Code formatting       |
| Database  | SQLite → PostgreSQL           | Data persistence      |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- pip
- virtualenv or venv

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Vincent088/nauticore-backend-django.git
cd nauticore-backend-django

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Create superuser (for admin panel access)
python manage.py createsuperuser

# 6. Seed the database with dummy data
python manage.py seed_nauticore

# 7. Start the development server
python manage.py runserver
```

### Access Points

| URL                                                  | Description              |
| ---------------------------------------------------- | ------------------------ |
| `http://127.0.0.1:8000/api/`                         | REST API root            |
| `http://127.0.0.1:8000/api/docs/`                    | Swagger UI documentation |
| `http://127.0.0.1:8000/api/redoc/`                   | ReDoc documentation      |
| `http://127.0.0.1:8000/super-secret-nauticore-2026/` | Admin panel              |

---

## 📁 Project Structure

```
NautiCore/
│
├── config/                          # Project configuration
│   ├── settings/
│   │   ├── base.py                  # Shared settings
│   │   ├── local.py                 # Development (SQLite)
│   │   └── production.py            # Production (PostgreSQL)
│   ├── urls.py                      # Root URL router
│   └── wsgi.py
│
├── apps/                            # All feature modules
│   ├── accounts/                    # Auth & user management
│   │   ├── models.py                # CustomUser, Profile
│   │   ├── views.py                 # Auth views
│   │   ├── serializers.py           # User serializers
│   │   ├── urls.py                  # Auth endpoints
│   │   └── admin.py
│   │
│   ├── clients/                     # Client management
│   ├── vessels/                     # Vessel projects (main)
│   │   └── management/
│   │       └── commands/
│   │           └── seed_nauticore.py
│   ├── materials/                   # Spare parts inventory
│   ├── progress/                    # Construction tracking
│   ├── documents/                   # Files & certifications
│   └── maintenance/                 # Maintenance scheduling
│
├── core/                            # Shared utilities
│   ├── models.py                    # BaseModel (UUID, timestamps)
│   ├── validators.py                # Security validators
│   ├── permissions.py               # Custom permissions
│   ├── pagination.py                # Custom pagination
│   └── throttles.py                 # Rate limiting
│
├── requirements.txt
├── manage.py
└── .env                             # Environment variables (not committed)
```

---

## 📦 Modules

### `core` — Foundation

Every model in the system inherits from `BaseModel`:

```python
class BaseModel(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

This gives every table:

- **UUID primary key** — prevents ID enumeration attacks
- **created_at** — automatically set on creation
- **updated_at** — automatically updated on every save

---

### `accounts` — Authentication & Users

**Models:** `CustomUser` (extends Django User), `Profile`

**User Roles:**

| Role          | Permissions                               |
| ------------- | ----------------------------------------- |
| `admin`       | Full access including user management     |
| `manager`     | All modules except user management        |
| `engineer`    | Vessels, progress, documents, maintenance |
| `procurement` | Spare parts and materials only            |
| `viewer`      | Read-only access to everything            |

**Key endpoints:**

```
POST  /api/auth/login/               → get access + refresh tokens
POST  /api/auth/register/            → create new account
POST  /api/auth/logout/              → blacklist refresh token
POST  /api/auth/token/refresh/       → refresh access token
GET   /api/auth/me/detail/           → current user info
PATCH /api/auth/me/update/           → update profile
POST  /api/auth/me/password/change/  → change password
GET   /api/auth/users/list/          → list all users
```

---

### `clients` — Client Management

**Models:** `Client`, `ClientContact`

Manages shipyard customers with industry classification:
`shipping` · `oil_gas` · `military` · `fishing` · `tourism` · `government` · `other`

---

### `vessels` — Vessel Projects (Main Module)

**Models:** `Vessel`, `VesselSpec`, `VesselPart`

The core of the system. Every other module connects back to a vessel.

**Vessel Types:** `new_build` · `repair` · `maintenance` · `conversion`

**Ship Types:** `tugboat` · `cargo` · `tanker` · `barge` · `ferry` · `fishing` · `patrol` · `dredger`

**Status Flow:**

```
planning → in_progress → testing → completed → delivered
                    ↓
               on_hold / cancelled
```

**Three-serializer pattern** (used across all modules):

- `VesselListSerializer` — minimal fields for list pages (fast)
- `VesselDetailSerializer` — full nested data for detail pages
- `VesselWriteSerializer` — only writable fields for create/update

---

### `materials` — Spare Parts Inventory

**Models:** `MaterialCategory`, `Material`, `StockMovement`, `MaterialRequest`

Key features:

- `is_low_stock` — auto-computed when `current_stock <= minimum_stock`
- `stock_value` — auto-computed as `current_stock × unit_price`
- `StockMovement.save()` — automatically updates stock levels on every movement
- Movement types: `in` · `out` · `transfer` · `adjust` · `return`

---

### `progress` — Construction Tracking

**Models:** `Milestone`, `Task`, `WorkLog`

**Auto-calculation chain:**

```
Task completion updated
        ↓
Milestone.update_completion() recalculates milestone %
        ↓
Vessel completion_pct = average of all milestones
```

**8 standard construction milestones:**

1. Design & Engineering
2. Steel Cutting & Forming
3. Hull Construction
4. Superstructure
5. Machinery Installation
6. Electrical & Navigation
7. Outfitting & Interior
8. Sea Trial & Delivery

---

### `documents` — Files & Certifications

**Models:** `Document`, `Certification`

- Auto-tracks expiry dates
- `is_expiring_soon` — True if expiry within 30 days
- `Certification.update_status()` — auto-updates status based on expiry

**Supported file types:** PDF, JPEG, PNG, WebP, Word, Excel, ZIP (max 50MB)

---

### `maintenance` — Scheduled Maintenance

**Models:** `MaintenanceType`, `MaintenanceSchedule`, `MaintenancePart`, `ServiceHistory`

**Priority levels:** `low` · `medium` · `high` · `critical`

**Status flow:**

```
scheduled → in_progress → completed
     ↓              ↓
  overdue    cancelled / postponed
```

When a schedule is marked complete via `POST /api/maintenance/schedules/{id}/complete/`:

1. Status → `completed`
2. `actual_hours` and `findings` saved
3. `next_due_date` auto-calculated: `completed_date + interval_days`
4. `ServiceHistory` record auto-created

**10 built-in maintenance types:**

| Type                        | Interval |
| --------------------------- | -------- |
| Main Engine Service         | 90 days  |
| Hull Inspection             | 180 days |
| Navigation Equipment Check  | 30 days  |
| Safety Equipment Inspection | 30 days  |
| Electrical System Check     | 60 days  |
| Propeller & Shaft Service   | 365 days |
| Anchor & Mooring Check      | 90 days  |
| Bilge System Service        | 60 days  |
| Generator Service           | 120 days |
| Steering Gear Service       | 90 days  |

---

## 🔗 API Endpoints

All endpoints follow a descriptive naming convention:

```
Standard DRF:          NautiCore:
GET  /api/vessels/  →  GET  /api/vessels/list/
POST /api/vessels/  →  POST /api/vessels/create/
GET  /api/vessels/1/→  GET  /api/vessels/{id}/detail/
```

### Full endpoint list by module

<details>
<summary><strong>Auth endpoints</strong></summary>

```
POST  /api/auth/login/
POST  /api/auth/register/
POST  /api/auth/logout/
POST  /api/auth/token/refresh/
GET   /api/auth/me/detail/
PATCH /api/auth/me/update/
PATCH /api/auth/me/profile/update/
POST  /api/auth/me/password/change/
GET   /api/auth/users/list/
```

</details>

<details>
<summary><strong>Clients endpoints</strong></summary>

```
GET    /api/clients/list/
POST   /api/clients/create/
GET    /api/clients/{id}/detail/
PATCH  /api/clients/{id}/update/
DELETE /api/clients/{id}/delete/
GET    /api/clients/{id}/contacts/
POST   /api/clients/{id}/add-contact/
GET    /api/clients/contacts/list/
POST   /api/clients/contacts/create/
PATCH  /api/clients/contacts/{id}/update/
DELETE /api/clients/contacts/{id}/delete/
```

</details>

<details>
<summary><strong>Vessels endpoints</strong></summary>

```
GET    /api/vessels/list/
POST   /api/vessels/create/
GET    /api/vessels/dashboard/
GET    /api/vessels/{id}/detail/
PATCH  /api/vessels/{id}/update/
DELETE /api/vessels/{id}/delete/
GET    /api/vessels/{id}/spec/
POST   /api/vessels/{id}/spec/
PUT    /api/vessels/{id}/spec/
GET    /api/vessels/{id}/parts/
POST   /api/vessels/{id}/parts/
PATCH  /api/vessels/parts/{id}/update/
DELETE /api/vessels/parts/{id}/delete/
```

</details>

<details>
<summary><strong>Materials endpoints</strong></summary>

```
GET    /api/materials/list/
POST   /api/materials/create/
GET    /api/materials/low-stock/
GET    /api/materials/summary/
GET    /api/materials/{id}/detail/
PATCH  /api/materials/{id}/update/
DELETE /api/materials/{id}/delete/
GET    /api/materials/{id}/movements/
POST   /api/materials/{id}/movements/
GET    /api/materials/categories/list/
POST   /api/materials/categories/create/
PATCH  /api/materials/categories/{id}/update/
DELETE /api/materials/categories/{id}/delete/
GET    /api/materials/requests/list/
POST   /api/materials/requests/create/
POST   /api/materials/requests/{id}/approve/
POST   /api/materials/requests/{id}/reject/
```

</details>

<details>
<summary><strong>Progress endpoints</strong></summary>

```
GET    /api/progress/milestones/list/
POST   /api/progress/milestones/create/
GET    /api/progress/milestones/overdue/
GET    /api/progress/milestones/{id}/detail/
PATCH  /api/progress/milestones/{id}/update/
DELETE /api/progress/milestones/{id}/delete/
GET    /api/progress/milestones/{id}/tasks/
POST   /api/progress/milestones/{id}/tasks/
GET    /api/progress/tasks/list/
PATCH  /api/progress/tasks/{id}/update/
POST   /api/progress/tasks/{id}/complete/
POST   /api/progress/tasks/{id}/update-progress/
GET    /api/progress/worklogs/list/
POST   /api/progress/worklogs/create/
GET    /api/progress/worklogs/my-logs/
GET    /api/progress/worklogs/summary/
```

</details>

<details>
<summary><strong>Documents endpoints</strong></summary>

```
GET    /api/documents/list/
POST   /api/documents/create/
GET    /api/documents/expiring/
GET    /api/documents/expired/
GET    /api/documents/{id}/detail/
PATCH  /api/documents/{id}/update/
DELETE /api/documents/{id}/delete/
GET    /api/documents/certifications/list/
POST   /api/documents/certifications/create/
GET    /api/documents/certifications/expiring/
GET    /api/documents/certifications/expired/
PATCH  /api/documents/certifications/{id}/update/
DELETE /api/documents/certifications/{id}/delete/
POST   /api/documents/certifications/{id}/refresh-status/
```

</details>

<details>
<summary><strong>Maintenance endpoints</strong></summary>

```
GET    /api/maintenance/types/list/
POST   /api/maintenance/types/create/
PATCH  /api/maintenance/types/{id}/update/
DELETE /api/maintenance/types/{id}/delete/
GET    /api/maintenance/schedules/list/
POST   /api/maintenance/schedules/create/
GET    /api/maintenance/schedules/dashboard/
GET    /api/maintenance/schedules/overdue/
GET    /api/maintenance/schedules/upcoming/
GET    /api/maintenance/schedules/{id}/detail/
PATCH  /api/maintenance/schedules/{id}/update/
DELETE /api/maintenance/schedules/{id}/delete/
POST   /api/maintenance/schedules/{id}/complete/
GET    /api/maintenance/schedules/{id}/parts/
POST   /api/maintenance/schedules/{id}/parts/
GET    /api/maintenance/history/list/
POST   /api/maintenance/history/create/
GET    /api/maintenance/history/{id}/detail/
PATCH  /api/maintenance/history/{id}/update/
DELETE /api/maintenance/history/{id}/delete/
```

</details>

---

## 🔐 Authentication

NautiCore uses **JWT (JSON Web Token)** authentication following the OAuth 2.0 standard.

### Login response

```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "Bearer",
  "expires_in": 28800
}
```

### Using the token

```bash
curl -H "Authorization: Bearer <access_token>" \
     http://127.0.0.1:8000/api/vessels/list/
```

### Token lifecycle

| Token         | Lifetime | Purpose                   |
| ------------- | -------- | ------------------------- |
| Access token  | 8 hours  | Authenticate API requests |
| Refresh token | 7 days   | Get new access token      |

### Token blacklisting

On logout, the refresh token is **blacklisted server-side** — even if someone has the token, it cannot be used again.

---

## 🛡 Security

### Input validation

All user input is validated through `core/validators.py`:

| Validator                 | Rules                                                      |
| ------------------------- | ---------------------------------------------------------- |
| `validate_username`       | ASCII only, 3-30 chars, no spaces, no emoji, no CJK        |
| `validate_email_field`    | Valid format, no CJK, blocks disposable domains            |
| `validate_password_field` | Min 8 chars, uppercase + lowercase + number + special char |
| `validate_name`           | All languages allowed, blocks emoji + SQL injection + XSS  |
| `validate_phone`          | Digits, +, -, spaces only                                  |
| `validate_no_sql_xss`     | Blocks SQL injection and XSS on any text field             |

### Rate limiting

| Endpoint            | Limit                 |
| ------------------- | --------------------- |
| Login               | 5 attempts per minute |
| Register            | 10 per hour           |
| Authenticated users | 1000 per day          |
| Anonymous users     | 100 per day           |

### Other security measures

- **UUID primary keys** — prevents ID enumeration
- **Secret admin URL** — admin panel not at `/admin/`
- **Swagger hidden in production** — API docs not exposed
- **CORS configured** — only allowed origins can call the API
- **File type validation** — only safe file types accepted
- **Disposable email blocking** — prevents throwaway accounts

---

## 🗄 Database

### Development

SQLite — zero configuration, file-based:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Production

Switch to PostgreSQL in `config/settings/production.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nauticore_db',
        'USER': 'nauticore_user',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Entity relationships

```
CustomUser ──────────────────────────────────┐
    │                                         │
    │ manages                                 │ performed_by
    ▼                                         │
  Vessel ──────── Client                      │
    │                                         │
    ├── VesselSpec (OneToOne)                 │
    ├── VesselPart                            │
    ├── Milestone → Task → WorkLog            │
    ├── Document                              │
    ├── Certification                         │
    ├── MaintenanceSchedule ─────────────────┘
    │       └── MaintenancePart → Material
    │       └── ServiceHistory
    └── MaterialRequest → Material
                              └── StockMovement
```

---

## 🌱 Seed Data

```bash
python manage.py seed_nauticore
```

Creates realistic related data:

| Data                  | Count                             |
| --------------------- | --------------------------------- |
| Users                 | 8 (across all roles)              |
| Clients               | 8 with contacts                   |
| Vessels               | 10 at various build stages        |
| Material categories   | 6                                 |
| Materials             | 24 with stock movements           |
| Milestones per vessel | 8 with tasks and work logs        |
| Certifications        | 6 per active vessel               |
| Maintenance schedules | 5 per vessel with service history |

---

## 🖥 Admin Panel

Accessible at: `http://127.0.0.1:8000/super-secret-nauticore-2026/`

Features:

- **Jazzmin theme** — dark mode following system preference
- **Colored status badges** — green, orange, red per status
- **Inline related records** — e.g. contacts inside client, parts inside vessel
- **Bulk actions** — mark multiple records at once
- **Date drill-down** — filter by year/month/day
- **Search and filters** — on every model

---

## 🧪 Test Accounts

After running `seed_nauticore`:

| Username     | Password         | Role        |
| ------------ | ---------------- | ----------- |
| `admin_john` | `NautiCore@2026` | Admin       |
| `mgr_sarah`  | `NautiCore@2026` | Manager     |
| `mgr_david`  | `NautiCore@2026` | Manager     |
| `eng_ali`    | `NautiCore@2026` | Engineer    |
| `eng_maria`  | `NautiCore@2026` | Engineer    |
| `eng_raj`    | `NautiCore@2026` | Engineer    |
| `proc_kevin` | `NautiCore@2026` | Procurement |
| `viewer_tom` | `NautiCore@2026` | Viewer      |

---

## 🔗 Related

- **Frontend Repository**: [nauticore-frontend](https://github.com/Vincent088/nauticore-frontend-react)
- **API Documentation**: Available at `/api/docs/` when running locally

---

<div align="center">
Built with Django REST Framework · Maritime Shipyard Management System
</div>
