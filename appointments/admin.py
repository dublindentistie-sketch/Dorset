from django.contrib import admin
from django.utils.html import format_html
from .models import Appointment, DoctorPlatformConfig, GoogleCalendarConfig
from .services import DoctorPlatformAPIService

@admin.register(GoogleCalendarConfig)
class GoogleCalendarConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'calendar_id', 'auth_type', 'auth_status_badge', 'is_active_badge', 'created_at')
    list_filter = ('is_active', 'auth_type', 'is_authorized')
    search_fields = ('name', 'calendar_id')

    fieldsets = (
        ('Google Calendar Information', {
            'fields': ('name', 'calendar_id', 'is_active')
        }),
        ('Authentication', {
            'fields': ('auth_type', 'credentials_json'),
            'description': 'Choose OAuth 2.0 (recommended) or Service Account. Paste your credentials JSON file content below.'
        }),
        ('OAuth Status', {
            'fields': ('is_authorized', 'token_json'),
            'classes': ('collapse',),
            'description': 'OAuth authorization status and token (auto-managed)'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at', 'is_authorized', 'token_json')

    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">●</span> Active')
        return format_html('<span style="color: red;">●</span> Inactive')
    is_active_badge.short_description = 'Status'

    def auth_status_badge(self, obj):
        if obj.auth_type == 'service_account':
            return format_html('<span style="color: blue;">Service Account</span>')
        elif obj.is_authorized:
            return format_html('<span style="color: green;">✓ Authorized</span>')
        else:
            return format_html('<span style="color: orange;">⚠ Not Authorized</span>')
    auth_status_badge.short_description = 'Auth Status'


@admin.register(DoctorPlatformConfig)
class DoctorPlatformConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'api_url', 'is_active_badge', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'api_url')

    fieldsets = (
        ('Platform Information', {
            'fields': ('name', 'api_url', 'is_active')
        }),
        ('Authentication', {
            'fields': ('api_key', 'api_secret'),
            'description': 'Configure API authentication credentials'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">●</span> Active')
        return format_html('<span style="color: red;">●</span> Inactive')
    is_active_badge.short_description = 'Status'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'patient_name',
        'patient_email',
        'service_type',
        'appointment_date',
        'appointment_time',
        'status',
        'sync_status_badge',
        'google_calendar_status_badge',
        'created_at'
    )
    list_filter = ('status', 'service_type', 'appointment_date', 'synced_to_platform', 'synced_to_google_calendar', 'created_at')
    search_fields = ('patient_name', 'patient_email', 'patient_phone', 'platform_appointment_id')
    date_hierarchy = 'appointment_date'
    ordering = ('-created_at',)

    fieldsets = (
        ('Personal Information', {
            'fields': ('patient_name', 'patient_email', 'patient_phone')
        }),
        ('Appointment Details', {
            'fields': ('service_type', 'appointment_date', 'appointment_time', 'additional_notes')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Platform Sync', {
            'fields': (
                'synced_to_platform',
                'platform_sync_date',
                'platform_appointment_id',
                'sync_error_message'
            ),
            'classes': ('collapse',),
            'description': 'API integration status with doctor platform'
        }),
        ('Google Calendar Sync', {
            'fields': (
                'synced_to_google_calendar',
                'google_calendar_event_id',
                'google_calendar_sync_date',
                'google_calendar_error_message'
            ),
            'classes': ('collapse',),
            'description': 'Google Calendar integration status'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = (
        'created_at', 'updated_at',
        'synced_to_platform', 'platform_sync_date', 'platform_appointment_id',
        'synced_to_google_calendar', 'google_calendar_event_id', 'google_calendar_sync_date'
    )

    actions = [
        'mark_as_confirmed',
        'mark_as_cancelled',
        'mark_as_completed',
        'sync_to_platform',
        'resync_to_platform',
        'sync_to_google_calendar'
    ]

    def sync_status_badge(self, obj):
        if obj.synced_to_platform:
            return format_html(
                '<span style="color: green;" title="Synced on {}">✓ Synced</span>',
                obj.platform_sync_date.strftime('%Y-%m-%d %H:%M') if obj.platform_sync_date else 'Unknown'
            )
        elif obj.sync_error_message:
            return format_html(
                '<span style="color: red;" title="{}">✗ Error</span>',
                obj.sync_error_message[:100]
            )
        return format_html('<span style="color: orange;">○ Not Synced</span>')
    sync_status_badge.short_description = 'Platform Sync'

    def google_calendar_status_badge(self, obj):
        if obj.synced_to_google_calendar:
            return format_html(
                '<span style="color: green;" title="Synced on {}">✓ Cal Synced</span>',
                obj.google_calendar_sync_date.strftime('%Y-%m-%d %H:%M') if obj.google_calendar_sync_date else 'Unknown'
            )
        elif obj.google_calendar_error_message:
            return format_html(
                '<span style="color: red;" title="{}">✗ Cal Error</span>',
                obj.google_calendar_error_message[:100]
            )
        return format_html('<span style="color: orange;">○ Not in Cal</span>')
    google_calendar_status_badge.short_description = 'Google Calendar'

    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, f'{queryset.count()} appointments marked as confirmed.')
    mark_as_confirmed.short_description = 'Mark selected appointments as confirmed'

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f'{queryset.count()} appointments marked as cancelled.')
    mark_as_cancelled.short_description = 'Mark selected appointments as cancelled'

    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
        self.message_user(request, f'{queryset.count()} appointments marked as completed.')
    mark_as_completed.short_description = 'Mark selected appointments as completed'

    def sync_to_platform(self, request, queryset):
        """Sync selected unsynced appointments to doctor platform"""
        api_service = DoctorPlatformAPIService()

        if not api_service.config:
            self.message_user(request, 'No active doctor platform configuration found.', level='error')
            return

        # Only sync unsynced appointments
        unsynced = queryset.filter(synced_to_platform=False)

        if not unsynced.exists():
            self.message_user(request, 'All selected appointments are already synced.', level='warning')
            return

        success_count, failure_count, errors = api_service.bulk_sync_appointments(unsynced)

        if success_count > 0:
            self.message_user(request, f'Successfully synced {success_count} appointments.', level='success')
        if failure_count > 0:
            self.message_user(request, f'Failed to sync {failure_count} appointments.', level='error')

    sync_to_platform.short_description = 'Sync to doctor platform'

    def resync_to_platform(self, request, queryset):
        """Force resync all selected appointments"""
        api_service = DoctorPlatformAPIService()

        if not api_service.config:
            self.message_user(request, 'No active doctor platform configuration found.', level='error')
            return

        success_count, failure_count, errors = api_service.bulk_sync_appointments(queryset)

        if success_count > 0:
            self.message_user(request, f'Successfully synced {success_count} appointments.', level='success')
        if failure_count > 0:
            self.message_user(request, f'Failed to sync {failure_count} appointments.', level='error')

    resync_to_platform.short_description = 'Force resync to doctor platform'

    def sync_to_google_calendar(self, request, queryset):
        """Sync selected appointments to Google Calendar"""
        from .google_calendar_service import GoogleCalendarService

        calendar_service = GoogleCalendarService()

        if not calendar_service.config:
            self.message_user(request, 'No active Google Calendar configuration found.', level='error')
            return

        success_count = 0
        failure_count = 0

        for appointment in queryset:
            if appointment.synced_to_google_calendar:
                continue

            success, message, event_id = calendar_service.create_appointment_event(appointment)
            if success:
                success_count += 1
            else:
                failure_count += 1

        if success_count > 0:
            self.message_user(request, f'Successfully synced {success_count} appointments to Google Calendar.', level='success')
        if failure_count > 0:
            self.message_user(request, f'Failed to sync {failure_count} appointments to Google Calendar.', level='error')

    sync_to_google_calendar.short_description = 'Sync to Google Calendar'
