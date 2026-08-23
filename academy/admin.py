from django.contrib import admin
from .models import CourseCategory, Course, StudentProfile, Enrollment, Module, Lesson, LessonProgress, Certificate


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1
    prepopulated_fields = {'slug': ('title',)}
    fields = ('title', 'slug', 'order', 'duration_minutes', 'is_preview', 'summary', 'video_url', 'content')


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'description', 'course__title')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonInline]
    ordering = ('course', 'order')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'get_course', 'order', 'duration_minutes', 'is_preview')
    list_filter = ('module__course', 'is_preview')
    search_fields = ('title', 'summary', 'content', 'module__title', 'module__course__title')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('module__course', 'module__order', 'order')

    def get_course(self, obj):
        return obj.module.course.title
    get_course.short_description = 'Course'


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'get_course', 'completed', 'completed_at')
    list_filter = ('completed', 'lesson__module__course')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'lesson__title')
    readonly_fields = ('completed_at',)

    def get_course(self, obj):
        return obj.lesson.module.course.title
    get_course.short_description = 'Course'


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'get_student_name', 'get_course_title', 'issue_date')
    search_fields = ('certificate_id', 'user__username', 'user__email', 'user__first_name', 'user__last_name', 'course__title', 'verification_code')
    readonly_fields = ('certificate_id', 'issue_date', 'verification_code')

    def get_student_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_student_name.short_description = 'Student'

    def get_course_title(self, obj):
        return obj.course.title
    get_course_title.short_description = 'Course'


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'active')
    list_editable = ('order', 'active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'format_type', 'duration', 'price', 'featured', 'active', 'created_at')
    list_filter = ('category', 'format_type', 'featured', 'active')
    search_fields = ('title', 'short_description', 'full_description', 'learning_outcomes', 'target_audience')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('featured', 'active')
    ordering = ('-featured', '-created_at')

    fieldsets = (
        ('Basic Course Information', {
            'fields': ('title', 'slug', 'category', 'format_type', 'short_description')
        }),
        ('Pricing & Duration', {
            'fields': ('price', 'duration')
        }),
        ('Media & Visuals', {
            'fields': ('thumbnail',)
        }),
        ('Detailed Curriculum & Syllabus', {
            'fields': ('full_description', 'learning_outcomes', 'target_audience', 'prerequisites')
        }),
        ('Publishing & Visibility', {
            'fields': ('featured', 'active')
        }),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'get_email', 'phone_number', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'user__username', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Student Name'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email Address'


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_user_email', 'course', 'enrollment_status', 'payment_status', 'created_at')
    list_filter = ('enrollment_status', 'payment_status', 'course__category', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'course__title')
    readonly_fields = ('created_at', 'updated_at')

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Student Email'




