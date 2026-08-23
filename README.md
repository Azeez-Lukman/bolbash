# Bolbash Beauty Spot

A premium digital web platform and business management system for **Bolbash Beauty Spot**, a luxury beauty salon and beauty training academy based in Ibadan, Nigeria.

---

## 📌 Project Overview

This platform provides a complete digital solution for Bolbash Beauty Spot, including:
- **Core Salon Website**: High-end visual presentation, service catalog, and brand showcase.
- **Online Booking System**: Service appointment reservation with deposit/payment integration.
- **Bolbash Beauty Academy**: Course management, online registration, and student portal.
- **E-Commerce Shop**: Beauty and hair care products ordering.
- **Admin Management**: Unified control dashboard for appointments, students, courses, and sales.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12+, Django 5.x
- **Frontend**: HTML5, Vanilla JavaScript, Tailwind CSS 3.4+
- **Database**: MySQL (configured with PyMySQL driver)
- **Environment Management**: `python-dotenv`
- **Version Control**: Git / GitHub

> **Note**: No heavy single-page frontend frameworks (React/Next/Vue) or alternative databases (PostgreSQL/MongoDB) are used. The architecture uses Django templates for simple, maintainable server-side rendering.

---

## 📁 Project Architecture

```
bolbash-beautyspot/
├── manage.py
├── config/                  # Django project configuration package
│   ├── settings.py          # Central environment-aware settings
│   ├── urls.py              # Root URL routing
│   ├── asgi.py              # ASGI config
│   └── wsgi.py              # WSGI config
├── core/                    # Core brand website & public views
├── accounts/                # User authentication & client/student profiles
├── booking/                 # Service appointment scheduling engine
├── academy/                 # Course registration & student portal
├── shop/                    # Beauty products catalog & ordering
├── payments/                # Paystack integration & transactions
├── templates/               # Global & modular HTML5 Django templates
│   └── base.html            # Foundation master layout
├── static/                  # Static assets
│   ├── css/
│   │   ├── input.css        # Source Tailwind CSS with custom design tokens
│   │   └── output.css       # Compiled production CSS
│   ├── js/
│   │   └── main.js          # Vanilla JavaScript core scripts
│   └── images/              # Logos & brand icons
├── media/                   # User and admin uploaded media assets
├── .env.example             # Template for local environment variables
├── .env                     # Local environment configuration (Git ignored)
├── package.json             # Tailwind CSS & Node build scripts
├── tailwind.config.js       # Custom brand theme configuration
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

---

## 🎨 Global Design System & Brand Palette

The platform follows a sophisticated, high-end beauty brand identity:
- **White (`#FFFFFF` / `#FAFAFA`)**: Clean space and high visual clarity.
- **Pink (`#DB2777`)**: Strategic accent and luxury highlight color.
- **Black (`#0B0F19`)**: Strong visual weight, contrast, and premium typography.
- **Typography**: `Playfair Display` (Headings) & `Plus Jakarta Sans` (Body).

---

## 🚀 Local Development Setup

### 1. Prerequisites
- Python 3.10+
- Node.js (v18+) & npm
- MySQL Server (v8.0+ or MariaDB)

### 2. Virtual Environment Setup
```bash
# Clone the repository
git clone https://github.com/your-org/bolbash-beautyspot.git
cd bolbash-beautyspot

# Create and activate virtual environment
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# Install Node packages for Tailwind CSS
npm install
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your local credentials:
```bash
cp .env.example .env
```

Edit `.env`:
```ini
SECRET_KEY=your-dev-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.mysql
DB_NAME=bolbash_beautyspot_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

### 5. MySQL Database Setup
Open your MySQL client or command prompt and execute:
```sql
CREATE DATABASE bolbash_beautyspot_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. Run Migrations & Checks
```bash
# Verify system configuration
python manage.py check

# Run initial Django database migrations
python manage.py migrate
```

### 7. Compile Tailwind CSS
```bash
# Compile CSS once
npm run build:css

# Or run CSS compiler in watch mode during development
npm run watch:css
```

### 8. Start Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🏢 Business Context

- **Business Name**: Bolbash Beauty Spot
- **Location**: No. 40, SIOA Plaza, at the entrance of E Exclusive Hotel, Ore-Ofe Bus Stop, Sango-Eleyele Road, Ibadan, Nigeria.
- **Phone**: 08168956606
- **Services**: Bridal hair styling, 360 & frontal installations, wigging units, haircuts, nail fixing, pedicure/manicure, weavon bleaching & revamping, piercing, beauty training & hair maintenance products.