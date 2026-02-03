"""
Django signals for automatic appointment sync to doctor platform and Google Calendar
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import logging
from .models import Appointment
from .services import DoctorPlatformAPIService
from .google_calendar_service import GoogleCalendarService

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Appointment)
def sync_appointment_to_platform(sender, instance, created, **kwargs):
    """
    Automatically sync appointment to doctor platform after creation or update
    """
    # Check if auto-sync is enabled in settings
    auto_sync_enabled = getattr(settings, 'AUTO_SYNC_APPOINTMENTS', True)

    if not auto_sync_enabled:
        logger.info(f"Auto-sync disabled for appointment {instance.id}")
        return

    # Only sync if not already synced or if updated
    if created or not instance.synced_to_platform:
        # Use threading to avoid blocking the request
        from threading import Thread

        def sync_task():
            try:
                api_service = DoctorPlatformAPIService()
                success, message, platform_id = api_service.send_appointment(instance)

                if success:
                    logger.info(f"Auto-synced appointment {instance.id} to platform (ID: {platform_id})")
                else:
                    logger.warning(f"Failed to auto-sync appointment {instance.id}: {message}")
            except Exception as e:
                logger.exception(f"Error in auto-sync for appointment {instance.id}: {str(e)}")

        # Start sync in background thread
        sync_thread = Thread(target=sync_task)
        sync_thread.daemon = True
        sync_thread.start()

    elif instance.synced_to_platform and instance.platform_appointment_id:
        # If already synced and has platform ID, update instead
        from threading import Thread

        def update_task():
            try:
                api_service = DoctorPlatformAPIService()
                success, message, _ = api_service.update_appointment(instance)

                if success:
                    logger.info(f"Auto-updated appointment {instance.id} on platform")
                else:
                    logger.warning(f"Failed to auto-update appointment {instance.id}: {message}")
            except Exception as e:
                logger.exception(f"Error in auto-update for appointment {instance.id}: {str(e)}")

        # Start update in background thread
        update_thread = Thread(target=update_task)
        update_thread.daemon = True
        update_thread.start()


@receiver(post_save, sender=Appointment)
def sync_appointment_to_google_calendar(sender, instance, created, **kwargs):
    """
    Automatically sync appointment to Google Calendar after creation or update
    """
    # Check if auto-sync to Google Calendar is enabled in settings
    auto_sync_google_enabled = getattr(settings, 'AUTO_SYNC_GOOGLE_CALENDAR', True)

    if not auto_sync_google_enabled:
        logger.info(f"Google Calendar auto-sync disabled for appointment {instance.id}")
        return

    # Only sync if not already synced or if updated
    if created or not instance.synced_to_google_calendar:
        # Use threading to avoid blocking the request
        from threading import Thread

        def google_sync_task():
            try:
                calendar_service = GoogleCalendarService()
                success, message, event_id = calendar_service.create_appointment_event(instance)

                if success:
                    logger.info(f"Auto-synced appointment {instance.id} to Google Calendar (Event ID: {event_id})")
                else:
                    logger.warning(f"Failed to auto-sync appointment {instance.id} to Google Calendar: {message}")
            except Exception as e:
                logger.exception(f"Error in Google Calendar auto-sync for appointment {instance.id}: {str(e)}")

        # Start sync in background thread
        google_sync_thread = Thread(target=google_sync_task)
        google_sync_thread.daemon = True
        google_sync_thread.start()

    elif instance.synced_to_google_calendar and instance.google_calendar_event_id:
        # If already synced and has event ID, update instead
        from threading import Thread

        def google_update_task():
            try:
                calendar_service = GoogleCalendarService()
                success, message, _ = calendar_service.update_appointment_event(instance)

                if success:
                    logger.info(f"Auto-updated appointment {instance.id} on Google Calendar")
                else:
                    logger.warning(f"Failed to auto-update appointment {instance.id} on Google Calendar: {message}")
            except Exception as e:
                logger.exception(f"Error in Google Calendar auto-update for appointment {instance.id}: {str(e)}")

        # Start update in background thread
        google_update_thread = Thread(target=google_update_task)
        google_update_thread.daemon = True
        google_update_thread.start()
