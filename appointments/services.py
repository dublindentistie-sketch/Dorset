"""
API Service for sending appointments to doctor platform
"""
import requests
import logging
from django.utils import timezone
from .models import Appointment, DoctorPlatformConfig

logger = logging.getLogger(__name__)


class DoctorPlatformAPIService:
    """Service class to handle API communication with doctor platform"""

    def __init__(self):
        self.config = None
        self._load_config()

    def _load_config(self):
        """Load active platform configuration"""
        try:
            self.config = DoctorPlatformConfig.objects.filter(is_active=True).first()
            if not self.config:
                logger.warning("No active doctor platform configuration found")
        except Exception as e:
            logger.error(f"Error loading platform config: {str(e)}")

    def _prepare_appointment_data(self, appointment):
        """
        Prepare appointment data for API transmission
        Customize this method based on doctor platform's API requirements
        """
        return {
            'patient_name': appointment.patient_name,
            'patient_email': appointment.patient_email,
            'patient_phone': appointment.patient_phone,
            'service_type': appointment.service_type,
            'service_name': appointment.get_service_display_name(),
            'appointment_date': appointment.appointment_date.isoformat(),
            'appointment_time': appointment.appointment_time.strftime('%H:%M'),
            'additional_notes': appointment.additional_notes or '',
            'status': appointment.status,
            'internal_id': appointment.id,
            'created_at': appointment.created_at.isoformat(),
        }

    def _get_headers(self):
        """
        Get API request headers
        Customize based on doctor platform's authentication method
        """
        if not self.config:
            return {}

        headers = {
            'Content-Type': 'application/json',
        }

        # Add authentication headers
        if self.config.api_key:
            headers['X-API-Key'] = self.config.api_key
        if self.config.api_secret:
            headers['Authorization'] = f'Bearer {self.config.api_secret}'

        return headers

    def send_appointment(self, appointment):
        """
        Send appointment to doctor platform
        Returns: (success: bool, message: str, platform_id: str)
        """
        if not self.config:
            return False, "No active platform configuration", None

        try:
            # Prepare data
            data = self._prepare_appointment_data(appointment)
            headers = self._get_headers()

            logger.info(f"Sending appointment {appointment.id} to {self.config.name}")

            # Make API request
            response = requests.post(
                self.config.api_url,
                json=data,
                headers=headers,
                timeout=30
            )

            # Check response
            if response.status_code in [200, 201]:
                response_data = response.json()
                platform_id = response_data.get('id') or response_data.get('appointment_id', '')

                # Update appointment
                appointment.synced_to_platform = True
                appointment.platform_sync_date = timezone.now()
                appointment.platform_appointment_id = str(platform_id)
                appointment.sync_error_message = ''
                appointment.save(update_fields=[
                    'synced_to_platform',
                    'platform_sync_date',
                    'platform_appointment_id',
                    'sync_error_message'
                ])

                logger.info(f"Successfully synced appointment {appointment.id} (Platform ID: {platform_id})")
                return True, "Successfully synced to doctor platform", str(platform_id)

            else:
                error_msg = f"API returned status {response.status_code}: {response.text}"
                logger.error(f"Failed to sync appointment {appointment.id}: {error_msg}")

                # Update error message
                appointment.sync_error_message = error_msg
                appointment.save(update_fields=['sync_error_message'])

                return False, error_msg, None

        except requests.exceptions.Timeout:
            error_msg = "API request timeout"
            logger.error(f"Timeout syncing appointment {appointment.id}")
            appointment.sync_error_message = error_msg
            appointment.save(update_fields=['sync_error_message'])
            return False, error_msg, None

        except requests.exceptions.ConnectionError:
            error_msg = "Failed to connect to doctor platform API"
            logger.error(f"Connection error syncing appointment {appointment.id}")
            appointment.sync_error_message = error_msg
            appointment.save(update_fields=['sync_error_message'])
            return False, error_msg, None

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.exception(f"Error syncing appointment {appointment.id}: {error_msg}")
            appointment.sync_error_message = error_msg
            appointment.save(update_fields=['sync_error_message'])
            return False, error_msg, None

    def update_appointment(self, appointment):
        """
        Update an existing appointment on doctor platform
        """
        if not self.config or not appointment.platform_appointment_id:
            return False, "Cannot update: No platform ID or config", None

        try:
            # Prepare data
            data = self._prepare_appointment_data(appointment)
            headers = self._get_headers()

            # Construct update URL
            update_url = f"{self.config.api_url.rstrip('/')}/{appointment.platform_appointment_id}"

            logger.info(f"Updating appointment {appointment.id} on {self.config.name}")

            # Make API request (PUT or PATCH)
            response = requests.put(
                update_url,
                json=data,
                headers=headers,
                timeout=30
            )

            if response.status_code in [200, 204]:
                appointment.platform_sync_date = timezone.now()
                appointment.sync_error_message = ''
                appointment.save(update_fields=['platform_sync_date', 'sync_error_message'])

                logger.info(f"Successfully updated appointment {appointment.id}")
                return True, "Successfully updated on doctor platform", appointment.platform_appointment_id

            else:
                error_msg = f"Update failed: {response.status_code} - {response.text}"
                logger.error(f"Failed to update appointment {appointment.id}: {error_msg}")
                appointment.sync_error_message = error_msg
                appointment.save(update_fields=['sync_error_message'])
                return False, error_msg, None

        except Exception as e:
            error_msg = f"Error updating appointment: {str(e)}"
            logger.exception(error_msg)
            appointment.sync_error_message = error_msg
            appointment.save(update_fields=['sync_error_message'])
            return False, error_msg, None

    def bulk_sync_appointments(self, appointments_queryset):
        """
        Sync multiple appointments in bulk
        Returns: (success_count, failure_count, errors)
        """
        success_count = 0
        failure_count = 0
        errors = []

        for appointment in appointments_queryset:
            success, message, _ = self.send_appointment(appointment)
            if success:
                success_count += 1
            else:
                failure_count += 1
                errors.append(f"Appointment {appointment.id}: {message}")

        return success_count, failure_count, errors
