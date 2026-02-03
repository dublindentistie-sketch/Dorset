from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

class GoogleCalendarConfig(models.Model):
    """Configuration for Google Calendar integration"""
    AUTH_TYPE_CHOICES = [
        ('oauth', 'OAuth 2.0 (Recommended)'),
        ('service_account', 'Service Account'),
    ]

    name = models.CharField(max_length=200, default="Google Calendar", help_text="Configuration name")
    calendar_id = models.EmailField(help_text="Google Calendar ID (usually your email)")
    auth_type = models.CharField(
        max_length=20,
        choices=AUTH_TYPE_CHOICES,
        default='oauth',
        help_text="Authentication type"
    )
    credentials_json = models.TextField(help_text="Google API credentials JSON content (OAuth client secret or Service Account key)")
    token_json = models.TextField(blank=True, help_text="OAuth token (auto-generated after authorization)")
    is_active = models.BooleanField(default=True, help_text="Enable/disable Google Calendar sync")
    is_authorized = models.BooleanField(default=False, help_text="OAuth authorization status")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Google Calendar Config'
        verbose_name_plural = 'Google Calendar Configs'

    def __str__(self):
        auth_status = "Authorized" if self.is_authorized or self.auth_type == 'service_account' else "Not Authorized"
        return f"{self.name} ({self.calendar_id}) - {auth_status} - {'Active' if self.is_active else 'Inactive'}"


class DoctorPlatformConfig(models.Model):
    """Configuration for external doctor platform API"""
    name = models.CharField(max_length=200, unique=True, help_text="Platform name (e.g., 'Main Doctor Platform')")
    api_url = models.URLField(help_text="API endpoint URL")
    api_key = models.CharField(max_length=500, blank=True, help_text="API authentication key")
    api_secret = models.CharField(max_length=500, blank=True, help_text="API secret/token")
    is_active = models.BooleanField(default=True, help_text="Enable/disable this platform")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Doctor Platform Config'
        verbose_name_plural = 'Doctor Platform Configs'

    def __str__(self):
        return f"{self.name} - {'Active' if self.is_active else 'Inactive'}"


class Appointment(models.Model):
    SERVICE_CHOICES = [
        ('checkup', 'Check Up'),
        ('cleaning', 'Cleaning'),
        ('filling', 'Filling'),
        ('custom', 'Custom'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    # Personal Information
    patient_name = models.CharField(max_length=200)
    patient_email = models.EmailField()
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    patient_phone = models.CharField(validators=[phone_regex], max_length=17)

    # Appointment Details
    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    doctor_name = models.CharField(max_length=200, blank=True, null=True, help_text="Assigned doctor")
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    additional_notes = models.TextField(blank=True, null=True)

    # Status and Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # API Integration
    synced_to_platform = models.BooleanField(default=False, help_text="Whether synced to doctor platform")
    platform_sync_date = models.DateTimeField(null=True, blank=True, help_text="Last sync date")
    platform_appointment_id = models.CharField(max_length=200, blank=True, help_text="ID from doctor platform")
    sync_error_message = models.TextField(blank=True, help_text="Last sync error message")

    # Google Calendar Integration
    google_calendar_event_id = models.CharField(max_length=500, blank=True, help_text="Google Calendar event ID")
    synced_to_google_calendar = models.BooleanField(default=False, help_text="Whether synced to Google Calendar")
    google_calendar_sync_date = models.DateTimeField(null=True, blank=True, help_text="Last Google Calendar sync date")
    google_calendar_error_message = models.TextField(blank=True, help_text="Last Google Calendar sync error")

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'

    def __str__(self):
        return f"{self.patient_name} - {self.appointment_date} at {self.appointment_time}"

    def get_service_display_name(self):
        return dict(self.SERVICE_CHOICES).get(self.service_type, self.service_type)
