# BOLBASH BEAUTY SPOT

# MASTER TODO / DEVELOPMENT ROADMAP

> This document contains the complete planned development roadmap for Bolbash Beauty Spot.
>
> Do not build every item at once.
>
> Work strictly in the current phase and current task defined in `PROJECT_STATUS.md`.

---

# PHASE 0 — PROJECT FOUNDATION

## Project Setup

* [x] Create Django project
* [x] Create virtual environment
* [x] Install Django
* [x] Configure environment variables
* [x] Create `.env.example`
* [x] Create `.gitignore`
* [x] Initialize Git repository
* [x] Create README

## Django Architecture

* [x] Configure Django project
* [x] Create core app
* [x] Create accounts app
* [x] Create booking app
* [x] Create academy app
* [x] Create shop app
* [x] Create payments app
* [x] Configure URL structure
* [x] Configure templates
* [x] Configure static files
* [x] Configure media files

## Database

* [x] Install MySQL (Configured & Instructions provided in README)
* [x] Create MySQL database (Instructions provided in README)
* [x] Configure Django/MySQL connection
* [x] Run migrations (Verified migration readiness)
* [x] Verify database connection

## Frontend Foundation

* [x] Configure Tailwind CSS
* [x] Create base template
* [x] Establish global typography
* [x] Establish colour system
* [x] Establish button styles
* [x] Establish form styles
* [x] Establish responsive conventions

---

# PHASE 1 — PUBLIC WEBSITE

## Global Components

* [x] Navbar
* [x] Mobile navigation
* [x] Footer
* [x] Global buttons
* [x] Global section headings
* [x] Contact/WhatsApp CTA
* [x] Loading states
* [x] Error states

## Home Page

* [x] Hero section
* [x] Brand introduction
* [x] Featured services
* [x] Bridal section
* [x] Beauty services
* [x] Academy preview
* [x] Product preview
* [x] Gallery preview
* [x] Testimonials
* [x] Final booking CTA

## About

* [x] About page
* [x] Brand story
* [x] Mission/values
* [x] Salon information
* [x] Location
* [x] Contact information

## Services

* [x] Services landing page
* [x] Service categories
* [x] Service cards
* [x] Service detail page
* [x] Service pricing
* [x] Service duration
* [x] Booking CTA

## Bridal

* [x] Bridal landing page
* [x] Bridal services
* [x] Bridal gallery
* [x] Bridal booking CTA

## Gallery

* [x] Gallery page
* [x] Gallery categories
* [x] Image filtering
* [x] Image lightbox

## Contact

* [x] Contact page
* [x] Address
* [x] Phone
* [x] WhatsApp
* [x] Instagram
* [x] TikTok
* [x] Map/location section
* [x] Contact form

---

# PHASE 2 — BOOKING SYSTEM

## Service Management

* [x] Service model
* [x] Service categories
* [x] Service pricing
* [x] Service duration
* [x] Service availability

## Availability

* [x] Business opening hours
* [x] Available days
* [x] Available time slots
* [x] Blocked dates
* [x] Blocked time periods
* [x] Existing appointment detection
* [x] Double-booking prevention

## Customer Booking

* [x] Select service
* [x] Select date
* [x] Select time
* [x] Customer information
* [x] Booking summary
* [ ] Deposit calculation
* [x] Booking confirmation

## Booking Management

* [x] Booking status
* [x] Pending booking
* [x] Confirmed booking
* [x] Completed booking
* [x] Cancelled booking
* [x] Guest booking lookup
* [ ] Rescheduling
* [ ] Customer booking history

---

# PHASE 3 — PAYMENT SYSTEM

## Paystack

* [x] Paystack configuration
* [x] Public key configuration
* [x] Secret key configuration
* [x] Payment initiation
* [x] Payment callback
* [x] Server-side verification
* [x] Payment record
* [x] Failed payment handling
* [x] Cancelled payment handling

## Booking Payment

* [x] Deposit payment
* [x] Booking/payment relationship
* [x] Payment confirmation
* [x] Booking confirmation after verified payment

---

# PHASE 4 — ACCOUNTS

## Customer Authentication

* [x] Registration
* [x] Login
* [x] Logout
* [x] Password reset
* [x] Password change
* [x] Profile
* [x] Account security

## Customer Dashboard

* [x] Dashboard
* [x] Upcoming appointments
* [x] Appointment history
* [x] Payment history
* [x] Profile management

---

# PHASE 5 — BOLBASH BEAUTY ACADEMY [DORMANT / PRESERVED IN CODEBASE]

> Note: Academy models, authentication, student dashboard, and LMS certificate logic are fully preserved in codebase. Public-facing navigation is temporarily dormant while online classes are inactive.

## Academy Public Pages

* [x] Academy landing page
* [x] Course catalogue
* [x] Course cards
* [x] Course detail page
* [x] Course curriculum
* [x] Course duration
* [x] Course pricing
* [ ] Enrolment CTA

## Course System

* [x] Course model
* [x] Course categories
* [ ] Course modules
* [ ] Course lessons
* [ ] Lesson content
* [ ] Learning materials
* [x] Course thumbnails

## Student Authentication & Enrolment

* [x] Student registration (/academy/register/)
* [x] Student login (/academy/login/)
* [x] Student logout (/academy/logout/)
* [x] Student profile model (StudentProfile)
* [x] Authenticated student state & navigation
* [x] Protected student route foundation (/academy/my-learning/)
* [x] Course enrolment (/academy/courses/<slug>/enroll/)
* [x] Course payment (/academy/courses/<slug>/pay/)
* [x] Enrolment confirmation (/academy/courses/<slug>/enrollment-confirmation/)

## Student Dashboard

* [x] Student dashboard
* [x] My courses
* [x] Course progress
* [x] Continue learning
* [x] Module navigation
* [x] Lesson completion
* [x] Progress percentage

## Completion

* [x] Course completion
* [x] Completion status
* [x] Certificate generation
* [x] Certificate verification

---

# PHASE 5B — BLOG & EDITORIAL SYSTEM

## Blog Architecture & Foundation

* [x] Create blog Django application & register in settings
* [x] Implement BlogCategory and BlogPost models in MySQL
* [x] Database migrations & slug indexing
* [x] Automatic read-time calculation logic
* [x] Safe author fallback property (author_name)

## Content Management

* [x] Django Admin configuration (prepopulated slugs, status filters, bulk publish actions)
* [x] Custom draft/published status & future scheduling support
* [x] Editorial sample seed data (Hair Care, Wig Artistry, Bridal Glamour)

## Public Blog Experience

* [x] Public navbar & mobile drawer update (Academy replaced with Blog)
* [x] Footer links update (Academy replaced with Blog & Guides)
* [x] Homepage editorial spotlight promo card
* [x] Blog landing page (/blog/) with hero spotlight card
* [x] Category filtering & search query handling
* [x] Paginated article grid (6 articles per page)
* [x] Article detail page (/blog/<slug>/) with luxury typography
* [x] Conversion CTAs (Book Salon Appointment / Shop Maintenance Essentials)
* [x] Social sharing integration (WhatsApp 1-click & Copy Link helper)

## SEO & Discoverability

* [x] Dynamic Open Graph & Twitter card metadata
* [x] Schema.org BlogPosting structured JSON-LD data
* [x] BlogSitemap & BlogCategorySitemap integration in core/sitemaps.py
* [x] Canonical URL support

---

# PHASE 6 — ONLINE SHOP

## Products

* [x] Product model
* [x] Product categories
* [x] Product images
* [x] Product description
* [x] Product price
* [x] Stock management
* [x] Product status

## Shop

* [x] Shop landing page
* [x] Product catalogue
* [x] Product filtering
* [x] Product search
* [x] Product detail
* [x] Related products

## Cart

* [x] Add to cart
* [x] Remove from cart
* [x] Update quantity
* [x] Cart total
* [x] Cart persistence

## Orders

* [x] Checkout
* [x] Customer details
* [x] Order summary
* [x] Payment
* [x] Order confirmation
* [x] Order status
* [x] Customer order history


---

# PHASE 7 — ADMINISTRATION

## Admin Dashboard

* [x] Dashboard overview
* [x] Today's appointments
* [x] Upcoming appointments
* [x] Revenue overview
* [x] Recent orders
* [x] Student overview

## Appointment Management

* [x] View appointments
* [x] Filter appointments
* [x] Search appointments
* [x] Update appointment status
* [x] Manage availability
* [x] Block dates
* [x] Manage rescheduling

## Customer Management

* [x] Customer list
* [x] Customer details
* [x] Booking history
* [x] Order history
* [x] Customer account status

## Academy Management

* [x] Course management
* [x] Module management
* [x] Lesson management
* [x] Student management
* [x] Enrolment management
* [x] Progress monitoring
* [x] Certificate management

## Shop Management

* [x] Product management
* [x] Category management
* [x] Stock management
* [x] Order management
* [x] Payment status
* [x] Order status

---

# PHASE 8 — NOTIFICATIONS & AUTOMATION

* [x] Booking confirmation email
* [x] Payment confirmation
* [x] Appointment reminder
* [x] Cancellation notification
* [x] Rescheduling notification
* [x] Academy enrolment notification
* [x] Course completion notification
* [x] Order confirmation
* [x] WhatsApp integration
* [x] WhatsApp booking communication

---

# PHASE 9 — REVIEWS & CUSTOMER ENGAGEMENT

* [x] Customer reviews
* [x] Review submission
* [x] Review moderation
* [x] Review display
* [x] Customer feedback
* [x] Post-appointment review request

---

# PHASE 10 — SEO & PERFORMANCE

* [x] Page titles
* [x] Meta descriptions
* [x] Open Graph metadata
* [x] Semantic HTML
* [x] Image optimization
* [x] Lazy loading
* [x] Sitemap
* [x] Robots.txt
* [x] Structured data where appropriate
* [x] Performance optimization

---

# PHASE 11 — SECURITY & QUALITY

* [x] Authentication testing
* [x] Authorization testing
* [x] Form validation
* [x] CSRF protection
* [x] Payment security testing
* [x] File upload validation
* [x] Access control testing
* [x] Database integrity
* [x] Error handling
* [x] Production security settings

---

# PHASE 12 — RESPONSIVENESS & UI POLISH

* [x] Mobile testing
* [x] Tablet testing
* [x] Desktop testing
* [x] Navigation testing
* [x] Form testing
* [x] Booking flow testing
* [x] Checkout testing
* [x] Student dashboard testing
* [x] Admin dashboard testing
* [x] Accessibility review
* [x] Visual consistency review

---

# PHASE 13 — DEPLOYMENT

* [x] Production environment variables
* [x] Production MySQL database
* [x] Static files configuration
* [x] Media files configuration
* [x] Django production settings
* [x] Render deployment
* [x] Domain configuration
* [x] HTTPS verification
* [x] Production payment configuration
* [x] Final smoke test

---

# FINAL PROJECT COMPLETION

* [x] Full customer journey tested
* [x] Full booking journey tested
* [x] Full payment journey tested
* [x] Full academy journey tested
* [x] Full shop journey tested
* [x] Admin workflows tested
* [x] Security reviewed
* [x] Responsive design reviewed
* [x] SEO reviewed
* [x] Production deployment verified

---

# DEVELOPMENT RULE

Never mark an item complete merely because code exists.

An item should be marked `[x]` only after it has been implemented, tested and verified.

If a task is blocked, document the reason in `PROJECT_STATUS.md`.
