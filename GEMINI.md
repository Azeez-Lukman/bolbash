# BOLBASH BEAUTY SPOT

## Gemini / Antigravity Master Development Rules

> This file is the permanent source of truth for how this project must be planned, designed, developed, tested and maintained.
>
> Before making any code changes, read this file together with `TODO.md` and `PROJECT_STATUS.md`.

---

# 1. PROJECT IDENTITY

Project name:

**Bolbash Beauty Spot**

Project type:

A premium digital platform for a beauty salon, beauty academy and hair-maintenance product business.

The final platform will combine:

* Premium salon website
* Service catalogue
* Online appointment booking
* Appointment availability
* Online payment/deposit
* Customer accounts
* Customer appointment history
* Beauty product catalogue
* Online shop
* Bolbash Beauty Academy
* Online course registration
* Student accounts
* Student learning dashboard
* Course modules and lessons
* Learning progress tracking
* Certificates
* Admin management
* Customer management
* Appointment management
* Product/order management
* Course/student management
* Notifications
* WhatsApp communication
* SEO
* Responsive mobile experience

This is a real client project.

Code quality, maintainability, security, usability and visual quality are important.

---

# 2. NON-NEGOTIABLE TECHNOLOGY STACK

The project MUST use:

### Frontend

* HTML5
* Tailwind CSS
* Vanilla JavaScript
* Django Templates

### Backend

* Python
* Django

### Database

* MySQL

### Payment

* Paystack

### Version Control

* Git
* GitHub

### Deployment

* Render

---

# 3. FORBIDDEN TECHNOLOGIES

Do NOT introduce or migrate the project to:

* React
* Next.js
* Vue
* Angular
* Svelte
* PostgreSQL
* MongoDB
* Firebase
* Bootstrap
* jQuery
* Any frontend framework

Do not replace an agreed technology with another technology simply because it may be easier or more modern.

If a new dependency or technology appears genuinely necessary, explain why before introducing it.

Do not silently change the architecture.

---

# 4. DEVELOPMENT PHILOSOPHY

Build the project incrementally.

Never attempt to implement the entire application in one operation.

Each feature must be:

1. Planned
2. Implemented
3. Tested
4. Reviewed
5. Marked complete
6. Documented where necessary

Only then should development proceed to the next feature.

---

# 5. CHANGE CONTROL

When implementing a requested feature:

* Modify only files that are necessary.
* Do not rewrite unrelated working code.
* Do not remove working functionality without permission.
* Do not rename existing files or directories unnecessarily.
* Do not change the database architecture without a valid reason.
* Do not introduce unnecessary dependencies.
* Do not refactor unrelated code while implementing a feature.

If a requested change requires an architectural modification, explain the impact before making the change.

---

# 6. CODE QUALITY

Write code that is:

* Readable
* Maintainable
* Modular
* Secure
* Reusable
* Properly structured
* Consistent with Django conventions

Avoid:

* Massive files
* Duplicate code
* Hard-coded business logic where database-driven logic is appropriate
* Unnecessary abstraction
* Unnecessary complexity
* Dead code
* Unused dependencies
* Unused imports
* Temporary hacks presented as final solutions

Prefer simple solutions that are easy for the project owner to understand and maintain.

---

# 7. DJANGO RULES

Use Django conventions wherever practical.

Use:

* Django apps
* Django models
* Django forms where appropriate
* Django views
* Django templates
* Django URL routing
* Django authentication
* Django admin where appropriate
* Django ORM

Keep responsibilities separated logically.

Do not put large amounts of business logic directly inside templates.

Do not use raw SQL when the Django ORM is sufficient.

Use migrations for database schema changes.

Never manually alter production database structure without corresponding migrations.

---

# 8. DATABASE RULES

Database:

**MySQL**

The database must remain MySQL throughout development.

Use Django migrations for schema changes.

Do not:

* Switch to PostgreSQL
* Switch to MongoDB
* Use SQLite as the project's final database
* Store important application data in flat files

Local development may use temporary development configurations when necessary, but the intended application database is MySQL.

Database credentials must never be hard-coded into source code.

Use environment variables.

---

# 9. FRONTEND RULES

The frontend must use:

* Django templates
* HTML
* Tailwind CSS
* Vanilla JavaScript

Do not create a separate frontend application.

Use Django template inheritance.

Prefer:

```text
base.html
```

with child templates extending it.

Create reusable template partials/components when repetition genuinely exists.

Do not create abstractions merely for the sake of abstraction.

---

# 10. JAVASCRIPT RULES

Use vanilla JavaScript.

JavaScript should be used for:

* UI interactions
* Dynamic forms
* Modals
* Filtering
* Client-side validation where appropriate
* AJAX/fetch requests
* Booking interactions
* Cart interactions
* Payment-related frontend interactions

Do not introduce React or another JavaScript framework.

Keep JavaScript modular and readable.

---

# 11. TAILWIND RULES

Tailwind CSS is the primary styling system.

Do not introduce Bootstrap.

Maintain consistent:

* Spacing
* Typography
* Buttons
* Forms
* Cards
* Containers
* Responsive breakpoints
* Shadows
* Borders
* Radius
* Layout patterns

Avoid excessive arbitrary values unless genuinely necessary.

---

# 12. BRAND DESIGN SYSTEM

The primary brand colours are:

### White

Clean space, backgrounds and elegance.

### Pink

Primary brand/accent colour.

### Black

Typography, contrast and premium visual weight.

The overall visual direction must feel:

**Premium
Elegant
Feminine
Modern
Clean
Sophisticated**

Do NOT make the website look like a generic pink salon template.

Pink must be used intentionally.

White and black should provide balance and sophistication.

Subtle neutral shades may be used for borders, muted text and supporting surfaces.

---

# 13. RESPONSIVE DESIGN

Build mobile-first.

Every page and feature must work on:

* Mobile
* Tablet
* Laptop
* Desktop

Do not postpone responsive design until the end.

Test layouts at different viewport sizes during development.

---

# 14. USER EXPERIENCE

The website must prioritize a clear customer journey.

The primary salon journey should eventually be:

**Discover Bolbash
→ Understand the brand
→ Explore services
→ Select a service
→ Choose date/time
→ Enter customer information
→ Pay required deposit
→ Receive confirmation
→ Attend appointment**

The academy journey should eventually be:

**Discover Academy
→ Explore course
→ View course details
→ Register
→ Pay
→ Create/access student account
→ Learn
→ Track progress
→ Complete course
→ Receive certificate**

The shop journey should eventually be:

**Discover product
→ View product
→ Add to cart
→ Checkout
→ Pay
→ Receive order confirmation**

Always design with these journeys in mind.

---

# 15. BOOKING RULES

The booking system must eventually support:

* Services
* Service duration
* Service price
* Appointment date
* Available time slots
* Customer details
* Deposit/payment
* Booking status
* Confirmation
* Cancellation/rescheduling rules

The system must prevent obvious double-booking situations.

Do not implement booking functionality until instructed.

---

# 16. PAYMENT RULES

Payment provider:

**Paystack**

Payment integration must eventually:

* Initiate payment securely
* Verify transactions server-side
* Record payment status
* Associate payments with bookings/orders/course enrolments
* Handle failed payments
* Handle cancelled payments
* Avoid trusting client-side payment confirmation alone

Never expose secret payment keys in frontend code.

Never hard-code payment credentials.

Payment functionality must be tested carefully before production.

---

# 17. AUTHENTICATION

The application will eventually support:

### Customers

* Registration
* Login
* Logout
* Password reset
* Profile
* Booking history
* Order history

### Students

Students may use the customer account system where appropriate.

Do not create unnecessary duplicate authentication systems.

Use Django's authentication capabilities where practical.

---

# 18. ACADEMY RULES

The academy will eventually support:

* Courses
* Course descriptions
* Course pricing
* Course thumbnails
* Modules
* Lessons
* Learning materials
* Student enrolment
* Payment
* Student dashboard
* Lesson progress
* Course completion
* Certificates

Do not build an overly complicated LMS unless the requirements justify it.

Keep the first version practical and maintainable.

---

# 19. SHOP RULES

The shop will eventually support:

* Products
* Categories
* Product images
* Prices
* Product descriptions
* Stock
* Cart
* Checkout
* Orders
* Payment
* Order status

Do not implement e-commerce functionality until instructed.

---

# 20. SECURITY

Security must be considered from the beginning.

Never expose:

* Django secret key
* Database passwords
* Paystack secret key
* API credentials
* Private tokens

Use environment variables.

Use Django's built-in security features.

Validate and sanitize user input appropriately.

Use CSRF protection.

Use authentication and authorization correctly.

Do not trust client-side data for sensitive operations.

Server-side validation is mandatory for important business operations.

---

# 21. ERROR HANDLING

Do not hide errors simply to make the application appear functional.

When something fails:

1. Identify the cause.
2. Explain it clearly.
3. Fix the underlying issue.
4. Test again.

Do not replace real errors with fake success messages.

Do not silently swallow exceptions unless there is a valid reason.

---

# 22. TESTING

Every meaningful feature must be tested before being marked complete.

Test:

* Normal operation
* Invalid input
* Missing input
* Authentication boundaries
* Payment states where applicable
* Mobile responsiveness
* Database operations
* Permission restrictions

Do not mark a feature complete simply because the page visually loads.

---

# 23. PROJECT DOCUMENTATION

The following files are project-level sources of truth:

```text
GEMINI.md
TODO.md
PROJECT_STATUS.md
README.md
docs/
```

Before modifying the project:

1. Read `GEMINI.md`.
2. Read `TODO.md`.
3. Read `PROJECT_STATUS.md`.
4. Inspect the existing code before changing it.

After completing a meaningful feature:

* Update `TODO.md`.
* Update `PROJECT_STATUS.md`.
* Record significant architectural decisions in the appropriate documentation file.

---

# 24. CURRENT PROJECT PHASE

The project is currently in:

**FOUNDATION / SETUP**

Do not assume that later features have already been implemented.

Always inspect the actual codebase.

The documentation files describe intended work; the source code determines what actually exists.

---

# 25. STOP CONDITIONS

When a prompt asks you to implement a specific feature:

Implement ONLY that feature and its necessary supporting changes.

Do not automatically continue into the next feature.

At completion:

* Test the work.
* Report what changed.
* Report any manual steps.
* Report any unresolved issue.
* Update project status.
* STOP.

Wait for the next instruction.

---

# 26. WHEN REQUIREMENTS ARE UNCLEAR

Do not invent major requirements.

If an ambiguity can materially affect:

* Database structure
* Payment logic
* Authentication
* Booking rules
* User permissions
* Architecture
* Security

Ask for clarification before making the decision.

For minor implementation details, choose the simplest reasonable solution and document the decision.

---

# 27. PRIORITY ORDER

When making decisions, prioritize:

1. Correctness
2. Security
3. Maintainability
4. User experience
5. Performance
6. Visual polish
7. Convenience

Do not sacrifice security or correctness merely to make development faster.

---

# 28. FINAL RULE

This is a controlled, incremental development project.

Do not rush.

Do not over-engineer.

Do not change the agreed stack.

Do not build features that were not requested.

Do not assume.

Inspect first.

Plan carefully.

Implement cleanly.

Test properly.

Document meaningful changes.

Then stop and wait for the next instruction.
