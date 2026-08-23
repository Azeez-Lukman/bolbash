from django.db import models
from django.utils.text import slugify


class CourseCategory(models.Model):
    """
    Model representing training categories/areas within Bolbash Beauty Academy.
    (e.g., Hair Styling, Wig Making, Wig Installation, Hair Maintenance)
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, help_text="Brief description of the training area.")
    icon = models.CharField(max_length=50, blank=True, help_text="Optional icon identifier or emoji.")
    order = models.PositiveIntegerField(default=0, help_text="Display ordering weight.")
    active = models.BooleanField(default=True, help_text="Designates whether this category is active.")

    class Meta:
        verbose_name = "Course Category"
        verbose_name_plural = "Course Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Course(models.Model):
    """
    Model representing an official training course/program offered by Bolbash Beauty Academy.
    """
    FORMAT_PHYSICAL = 'PHYSICAL'
    FORMAT_ONLINE = 'ONLINE'
    FORMAT_HYBRID = 'HYBRID'

    FORMAT_CHOICES = [
        (FORMAT_PHYSICAL, 'Physical Training'),
        (FORMAT_ONLINE, 'Online Class'),
        (FORMAT_HYBRID, 'Hybrid Program'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(
        CourseCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses'
    )
    short_description = models.CharField(max_length=255, help_text="Concise summary for course cards.")
    full_description = models.TextField(help_text="Detailed course breakdown and syllabus overview.")
    thumbnail = models.ImageField(upload_to='academy/courses/', blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True, help_text="e.g. 4 Weeks, 2 Days, or Self-Paced")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Course fee in NGN. Leave blank if price is on enquiry.")
    format_type = models.CharField(max_length=20, choices=FORMAT_CHOICES, default=FORMAT_PHYSICAL)
    learning_outcomes = models.TextField(
        blank=True,
        help_text="Enter key skills/outcomes learned in this course, one per line."
    )
    target_audience = models.TextField(
        blank=True,
        help_text="Enter target student profiles for this course, one per line."
    )
    prerequisites = models.TextField(
        blank=True,
        help_text="Optional prerequisites or recommended tools."
    )
    active = models.BooleanField(default=True, help_text="Whether this course is publicly visible.")
    featured = models.BooleanField(default=False, help_text="Whether to feature this course prominently.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        ordering = ['-featured', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('academy:course_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_learning_outcomes_list(self):
        """Returns a list of non-empty lines from learning_outcomes."""
        if not self.learning_outcomes:
            return []
        return [line.strip() for line in self.learning_outcomes.splitlines() if line.strip()]

    def get_target_audience_list(self):
        """Returns a list of non-empty lines from target_audience."""
        if not self.target_audience:
            return []
        return [line.strip() for line in self.target_audience.splitlines() if line.strip()]

    def get_prerequisites_list(self):
        """Returns a list of non-empty lines from prerequisites."""
        if not self.prerequisites:
            return []
        return [line.strip() for line in self.prerequisites.splitlines() if line.strip()]

    def get_whatsapp_enquiry_url(self):
        """Generates dynamic WhatsApp enquiry URL with course title."""
        from urllib.parse import quote
        message = f"Hello Bolbash Beauty Spot, I am interested in the {self.title} training program. I would like to know more about the training."
        encoded_message = quote(message)
        return f"https://wa.me/message/UW6FRPKW3STAM1?text={encoded_message}"


class StudentProfile(models.Model):
    """
    Model representing an authenticated Academy student's profile.
    Associated 1-to-1 with Django's default User model.
    """
    from django.contrib.auth.models import User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    phone_number = models.CharField(max_length=20, blank=True, help_text="Contact phone number.")
    profile_image = models.ImageField(upload_to='academy/students/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"
        ordering = ['-created_at']

    def __str__(self):
        full_name = self.user.get_full_name()
        return f"{full_name or self.user.username} ({self.user.email})"


class Enrollment(models.Model):
    """
    Model representing a student's enrollment record in a Bolbash Beauty Academy course.
    Establishes a 1-to-many relationship between User (Student) and Course.
    Enforces database-level unique constraint preventing duplicate enrollments per student/course.
    """
    STATUS_PENDING = 'PENDING'
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'

    ENROLLMENT_STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    PAYMENT_UNPAID = 'UNPAID'
    PAYMENT_PENDING = 'PENDING'
    PAYMENT_PAID = 'PAID'
    PAYMENT_FAILED = 'FAILED'
    PAYMENT_REFUNDED = 'REFUNDED'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_UNPAID, 'Unpaid'),
        (PAYMENT_PENDING, 'Pending'),
        (PAYMENT_PAID, 'Paid'),
        (PAYMENT_FAILED, 'Failed'),
        (PAYMENT_REFUNDED, 'Refunded'),
    ]

    from django.contrib.auth.models import User
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_status = models.CharField(
        max_length=20,
        choices=ENROLLMENT_STATUS_CHOICES,
        default=STATUS_PENDING,
        help_text="Student's relationship status with this course."
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default=PAYMENT_UNPAID,
        help_text="Financial payment state for this course enrollment."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Course Enrollment"
        verbose_name_plural = "Course Enrollments"
        ordering = ['-created_at']
        unique_together = ['user', 'course']
        constraints = [
            models.UniqueConstraint(fields=['user', 'course'], name='unique_student_course_enrollment')
        ]

    def __str__(self):
        full_name = self.user.get_full_name() or self.user.username
        return f"{full_name} - {self.course.title} ({self.enrollment_status}/{self.payment_status})"

    def get_total_lessons_count(self):
        """Returns total number of lessons in the enrolled course."""
        return Lesson.objects.filter(module__course=self.course).count()

    def get_completed_lessons_count(self):
        """Returns count of completed lessons for this student in this course."""
        return LessonProgress.objects.filter(
            user=self.user,
            lesson__module__course=self.course,
            completed=True
        ).count()

    def get_progress_percentage(self):
        """Calculates completed percentage (0-100)."""
        total = self.get_total_lessons_count()
        if total == 0:
            return 0
        completed = self.get_completed_lessons_count()
        return round((completed / total) * 100)

    def get_progress_status_badge(self):
        """Returns human readable status string for UI cards."""
        if self.enrollment_status == self.STATUS_COMPLETED:
            return "Completed"
        pct = self.get_progress_percentage()
        if pct == 0:
            return "Not Started"
        return "In Progress"

    def get_next_unfinished_lesson(self):
        """
        Returns the first lesson that has not been completed by the student in order.
        If all are completed or no lessons exist, returns the first lesson or None.
        """
        lessons = Lesson.objects.filter(module__course=self.course).order_by('module__order', 'order')
        if not lessons.exists():
            return None

        completed_ids = LessonProgress.objects.filter(
            user=self.user,
            lesson__module__course=self.course,
            completed=True
        ).values_list('lesson_id', flat=True)

        unfinished = lessons.exclude(id__in=completed_ids).first()
        if unfinished:
            return unfinished
        return lessons.first()

    def check_and_update_completion(self):
        """
        Server-side validation: Checks if all lessons are completed.
        If 100% complete and total > 0, marks enrollment as STATUS_COMPLETED and generates Certificate.
        """
        total = self.get_total_lessons_count()
        completed = self.get_completed_lessons_count()

        if total > 0 and completed == total:
            if self.enrollment_status != self.STATUS_COMPLETED:
                self.enrollment_status = self.STATUS_COMPLETED
                self.save(update_fields=['enrollment_status', 'updated_at'])

            # Generate Certificate if not exists
            cert, _ = Certificate.get_or_create_for_enrollment(self)
            if cert:
                try:
                    from notifications.services import NotificationDispatcher
                    NotificationDispatcher.send_course_completion(cert)
                except Exception:
                    pass
            return True
        return False


class Module(models.Model):
    """
    Model representing a module/chapter within an Academy course.
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, blank=True)
    description = models.TextField(blank=True, help_text="Module overview and learning objectives.")
    order = models.PositiveIntegerField(default=1, help_text="Order weight within the course.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Course Module"
        verbose_name_plural = "Course Modules"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.course.title} - Module {self.order}: {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Lesson(models.Model):
    """
    Model representing an individual learning lesson within a Course Module.
    """
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, blank=True)
    summary = models.CharField(max_length=255, blank=True, help_text="Short summary of lesson topic.")
    content = models.TextField(help_text="Detailed lesson instructions, hair styling guides, text curriculum.")
    video_url = models.URLField(blank=True, help_text="Optional video tutorial URL (e.g. YouTube or Vimeo link).")
    duration_minutes = models.PositiveIntegerField(default=15, help_text="Estimated completion duration in minutes.")
    order = models.PositiveIntegerField(default=1, help_text="Order weight within the module.")
    is_preview = models.BooleanField(default=False, help_text="Whether unauthenticated users can preview this lesson.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.module.title} - Lesson {self.order}: {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def course(self):
        return self.module.course


class LessonProgress(models.Model):
    """
    Model tracking a student's completion record for an individual lesson.
    """
    from django.contrib.auth.models import User
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progresses')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progresses')
    completed = models.BooleanField(default=True)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Lesson Progress"
        verbose_name_plural = "Lesson Progresses"
        unique_together = ['user', 'lesson']
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} ({'Done' if self.completed else 'Pending'})"


class Certificate(models.Model):
    """
    Model representing an official graduation/completion certificate issued by Bolbash Beauty Academy.
    Contains a unique certificate ID and verification code for public authenticity validation.
    """
    from django.contrib.auth.models import User
    import secrets
    from django.utils import timezone

    certificate_id = models.CharField(max_length=50, unique=True, help_text="Unique Certificate Reference e.g. BBA-CERT-YYYYMMDD-XXXX")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='certificate')
    issue_date = models.DateField(auto_now_add=True)
    verification_code = models.CharField(max_length=64, unique=True, help_text="Cryptographic verification string.")
    is_active = models.BooleanField(default=True, help_text="Whether this certificate is valid and active.")

    class Meta:
        verbose_name = "Course Certificate"
        verbose_name_plural = "Course Certificates"
        ordering = ['-issue_date']

    def __str__(self):
        return f"Certificate {self.certificate_id} - {self.user.get_full_name() or self.user.username} ({self.course.title})"

    @classmethod
    def generate_certificate_id(cls):
        """Generates unique certificate ID e.g. BBA-CERT-20260819-A8F3."""
        import secrets
        from django.utils import timezone
        date_str = timezone.now().strftime("%Y%m%d")
        random_suffix = secrets.token_hex(2).upper()
        return f"BBA-CERT-{date_str}-{random_suffix}"

    @classmethod
    def get_or_create_for_enrollment(cls, enrollment):
        """
        Creates or retrieves an official Certificate for a completed Enrollment.
        """
        import secrets
        cert = getattr(enrollment, 'certificate', None)
        if cert:
            return cert, False

        cert_id = cls.generate_certificate_id()
        while cls.objects.filter(certificate_id=cert_id).exists():
            cert_id = cls.generate_certificate_id()

        verification_code = secrets.token_urlsafe(32)
        cert = cls.objects.create(
            certificate_id=cert_id,
            user=enrollment.user,
            course=enrollment.course,
            enrollment=enrollment,
            verification_code=verification_code
        )
        return cert, True



