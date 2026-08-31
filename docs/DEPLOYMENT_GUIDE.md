# BOLBASH BEAUTY SPOT — PRODUCTION DEPLOYMENT GUIDE

This document provides step-by-step instructions for deploying the **Bolbash Beauty Spot** platform to **Render** with a production **MySQL** database, custom domain, SSL/HTTPS certificates, and Paystack live payments.

---

## 1. Prerequisites

Before deploying to production, ensure you have:
1. A [GitHub](https://github.com/) account with access to `https://github.com/Azeez-Lukman/bolbash.git`.
2. A [Render](https://render.com/) account.
3. A managed MySQL database (Render External MySQL, [Aiven](https://aiven.io/), [PlanetScale](https://planetscale.com/), [DigitalOcean](https://digitalocean.com/), or [AWS RDS](https://aws.amazon.com/rds/)).
4. A [Paystack](https://paystack.com/) live merchant account with live API keys (`pk_live_...` and `sk_live_...`).
5. A registered domain name (e.g., `bolbashbeautyspot.com`) with DNS management access.

---

## 2. Production Architecture Overview

- **Web Server**: Gunicorn WSGI Server (`gunicorn config.wsgi:application`)
- **Static Assets**: Django static files collected, compressed, and served with HTTP caching headers via **WhiteNoise**.
- **Database**: Cloud MySQL 8.x with `utf8mb4` encoding and strict SQL mode.
- **SSL / HTTPS**: Managed automatically by Render Let's Encrypt certificates with HSTS preload.
- **Media Uploads**: Server media directory or persistent disk volume attached at `/var/data/media`.

---

## 3. Step-by-Step Render Deployment

### Step A: Connect Repository to Render
1. Log in to the [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** → **Web Service**.
3. Select **Build and deploy from a Git repository** and connect `Azeez-Lukman/bolbash`.
4. Fill in the service configuration:
   - **Name**: `bolbash-beautyspot`
   - **Region**: Choose closest to target audience (e.g., *Frankfurt* or *London*).
   - **Branch**: `main`
   - **Root Directory**: Leave blank (root).
   - **Runtime**: `Python 3`
   - **Build Command**: `bash build.sh`
   - **Start Command**: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120`
   - **Instance Type**: `Starter` (or higher).

---

### Step B: Configure Production Environment Variables
In the **Environment** tab of your Render Web Service, add the following variables:

| Variable Name | Value / Description |
|---|---|
| `PYTHON_VERSION` | `3.12.0` |
| `DEBUG` | `False` |
| `SECRET_KEY` | *(Click "Generate" or provide a secure 50+ character random string)* |
| `ALLOWED_HOSTS` | `bolbash-beautyspot.onrender.com,www.bolbashbeautyspot.com,bolbashbeautyspot.com` |
| `CSRF_TRUSTED_ORIGINS` | `https://*.onrender.com,https://www.bolbashbeautyspot.com,https://bolbashbeautyspot.com` |
| `DATABASE_URL` | `mysql://username:password@mysql-host.cloud.provider:3306/bolbash_beautyspot_db` |
| `PAYSTACK_PUBLIC_KEY` | `pk_live_your_live_public_key_here` |
| `PAYSTACK_SECRET_KEY` | `sk_live_your_live_secret_key_here` |
| `PAYSTACK_PAYMENT_URL` | `https://api.paystack.co` |
| `PAYSTACK_BANK_NAME` | `OPay` |
| `PAYSTACK_ACCOUNT_NUMBER` | `8148281423` |
| `PAYSTACK_ACCOUNT_NAME` | `Lukexx Business And Technology` |
| `BOOKING_DEPOSIT_AMOUNT` | `100.00` |
| `EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` | `smtp.gmail.com` |
| `EMAIL_PORT` | `587` |
| `EMAIL_HOST_USER` | `officialbolbash@gmail.com` |
| `EMAIL_HOST_PASSWORD` | `your_gmail_app_password` |
| `EMAIL_USE_TLS` | `True` |
| `DEFAULT_FROM_EMAIL` | `Bolbash Beauty Spot <no-reply@bolbashbeautyspot.com>` |
| `SECURE_SSL_REDIRECT` | `True` |
| `SESSION_COOKIE_SECURE` | `True` |
| `CSRF_COOKIE_SECURE` | `True` |

---

### Step C: Deploy and Build
1. Click **Create Web Service** (or **Manual Deploy** → **Deploy latest commit**).
2. Render will execute `build.sh`:
   - Installs all dependencies from `requirements.txt`.
   - Runs `python manage.py collectstatic --no-input` (Whitenoise compiles all CSS, JS, fonts, and video assets).
   - Runs `python manage.py migrate --no-input` (Creates/updates all MySQL tables).
3. Once the build completes, the status will show **Live**.

---

### Step D: Create Initial Superuser
1. In the Render Dashboard, go to your service → **Shell** tab.
2. Run:
   ```bash
   python manage.py createsuperuser
   ```
3. Enter admin username, email, and password to enable `/admin-portal/` access.

---

## 4. Custom Domain & DNS Configuration

1. In Render, go to **Settings** → **Custom Domains**.
2. Add your custom domains:
   - `bolbashbeautyspot.com`
   - `www.bolbashbeautyspot.com`
3. Configure your DNS provider (e.g. Namecheap, Cloudflare, GoDaddy):
   - **CNAME Record**: `www` pointing to `bolbash-beautyspot.onrender.com`
   - **ANAME/ALIAS Record** (or Cloudflare CNAME flattening): `@` pointing to `bolbash-beautyspot.onrender.com`
4. Render will automatically issue and renew a free **Let's Encrypt SSL/TLS Certificate** within 5-15 minutes.

---

## 5. Paystack Live Webhook Configuration

1. Log in to [Paystack Dashboard](https://dashboard.paystack.com/#/settings/developer).
2. Switch toggle to **Live Mode**.
3. Under **API Keys & Webhooks**:
   - **Live Webhook URL**: `https://www.bolbashbeautyspot.com/payments/webhook/` (or `https://bolbash-beautyspot.onrender.com/payments/webhook/`)
   - Copy **Live Secret Key** and **Live Public Key** into your Render environment variables.

---

## 6. Post-Deployment Verification Checklist

- [ ] Visit `https://www.bolbashbeautyspot.com/` — Homepage renders with full styling and static images.
- [ ] Visit `https://www.bolbashbeautyspot.com/bridal/` — Background video plays smoothly with luxury overlay.
- [ ] Visit `https://www.bolbashbeautyspot.com/services/` — Service catalog and pricing display correctly.
- [ ] Test booking appointment flow at `/booking/` — Select service, pick date & slot, verify Paystack initiation.
- [ ] Test student course enrollment at `/academy/`.
- [ ] Test product cart & checkout at `/shop/`.
- [ ] Log in to `/admin-portal/` as superuser and verify dashboard analytics.
- [ ] Verify SSL certificate padlock shows **Connection Secure** (HTTPS).
