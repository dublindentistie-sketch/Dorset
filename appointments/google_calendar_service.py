"""
Google Calendar API Service for syncing appointments
Supports both OAuth 2.0 and Service Account authentication
"""
import json
import logging
from datetime import datetime, timedelta
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.utils import timezone
from .models import Appointment, GoogleCalendarConfig

logger = logging.getLogger(__name__)


class GoogleCalendarService:
    """Service class to handle Google Calendar API integration"""

    SCOPES = ['https://www.googleapis.com/auth/calendar']

    def __init__(self):
        self.config = None
        self.service = None
        self._load_config()

    def _load_config(self):
        """Load active Google Calendar configuration"""
        try:
            self.config = GoogleCalendarConfig.objects.filter(is_active=True).first()
            if not self.config:
                logger.warning("No active Google Calendar configuration found")
                return

            # Initialize Google Calendar service
            self._initialize_service()

        except Exception as e:
            logger.error(f"Error loading Google Calendar config: {str(e)}")

    def _initialize_service(self):
        """Initialize Google Calendar API service"""
        try:
            if self.config.auth_type == 'oauth':
                self._initialize_oauth_service()
            else:  # service_account
                self._initialize_service_account()

        except json.JSONDecodeError as e:
            logger.error(f"Invalid credentials JSON: {str(e)}")
            self.service = None
        except Exception as e:
            logger.error(f"Error initializing Google Calendar service: {str(e)}")
            self.service = None

    def _initialize_oauth_service(self):
        """Initialize service using OAuth 2.0"""
        if not self.config.token_json:
            logger.warning("OAuth token not found. Authorization required.")
            self.service = None
            return

        try:
            # Load token
            token_info = json.loads(self.config.token_json)
            credentials = Credentials.from_authorized_user_info(token_info, self.SCOPES)

            # Check if token is expired and refresh if needed
            if credentials.expired and credentials.refresh_token:
                from google.auth.transport.requests import Request
                credentials.refresh(Request())

                # Save refreshed token
                self.config.token_json = credentials.to_json()
                self.config.save(update_fields=['token_json'])
                logger.info("OAuth token refreshed successfully")

            # Build the service
            self.service = build('calendar', 'v3', credentials=credentials)
            logger.info("Google Calendar service initialized with OAuth")

        except Exception as e:
            logger.error(f"Error initializing OAuth service: {str(e)}")
            self.service = None

    def _initialize_service_account(self):
        """Initialize service using Service Account"""
        try:
            # Parse credentials JSON
            credentials_info = json.loads(self.config.credentials_json)

            # Create credentials
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=self.SCOPES
            )

            # Build the service
            self.service = build('calendar', 'v3', credentials=credentials)
            logger.info("Google Calendar service initialized with Service Account")

        except Exception as e:
            logger.error(f"Error initializing Service Account: {str(e)}")
            self.service = None

    def _prepare_event_data(self, appointment):
        """
        Prepare event data for Google Calendar
        """
        # Combine date and time
        start_datetime = datetime.combine(
            appointment.appointment_date,
            appointment.appointment_time
        )

        # Assume 1 hour appointment duration (you can customize this)
        end_datetime = start_datetime + timedelta(hours=1)

        # Format for Google Calendar (ISO format with timezone)
        # Using UTC timezone for consistency
        start_iso = start_datetime.isoformat()
        end_iso = end_datetime.isoformat()

        # Create event description
        description_parts = [
            f"Patient: {appointment.patient_name}",
            f"Email: {appointment.patient_email}",
            f"Phone: {appointment.patient_phone}",
            f"Service: {appointment.get_service_display_name()}",
        ]

        if appointment.doctor_name:
            description_parts.append(f"Doctor: {appointment.doctor_name}")

        if appointment.additional_notes:
            description_parts.append(f"\nNotes: {appointment.additional_notes}")

        description = "\n".join(description_parts)

        # Create event
        event = {
            'summary': f"Dental Appointment - {appointment.patient_name}",
            'description': description,
            'start': {
                'dateTime': start_iso,
                'timeZone': 'UTC',  # You can customize this based on your clinic timezone
            },
            'end': {
                'dateTime': end_iso,
                'timeZone': 'UTC',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                    {'method': 'popup', 'minutes': 60},  # 1 hour before
                ],
            },
        }

        return event

    def create_appointment_event(self, appointment):
        """
        Create a Google Calendar event for an appointment
        Returns: (success: bool, message: str, event_id: str)
        """
        if not self.config or not self.service:
            return False, "Google Calendar service not configured", None

        try:
            # Prepare event data
            event = self._prepare_event_data(appointment)

            logger.info(f"Creating Google Calendar event for appointment {appointment.id}")

            # Create the event
            created_event = self.service.events().insert(
                calendarId=self.config.calendar_id,
                body=event
            ).execute()

            event_id = created_event.get('id')

            # Update appointment
            appointment.synced_to_google_calendar = True
            appointment.google_calendar_event_id = event_id
            appointment.google_calendar_sync_date = timezone.now()
            appointment.google_calendar_error_message = ''
            appointment.save(update_fields=[
                'synced_to_google_calendar',
                'google_calendar_event_id',
                'google_calendar_sync_date',
                'google_calendar_error_message'
            ])

            logger.info(f"Successfully created Google Calendar event {event_id} for appointment {appointment.id}")
            return True, "Successfully added to Google Calendar", event_id

        except HttpError as e:
            error_msg = f"Google Calendar API error: {str(e)}"
            logger.error(f"Failed to create event for appointment {appointment.id}: {error_msg}")

            appointment.google_calendar_error_message = error_msg
            appointment.save(update_fields=['google_calendar_error_message'])

            return False, error_msg, None

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.exception(f"Error creating event for appointment {appointment.id}: {error_msg}")

            appointment.google_calendar_error_message = error_msg
            appointment.save(update_fields=['google_calendar_error_message'])

            return False, error_msg, None

    def update_appointment_event(self, appointment):
        """
        Update an existing Google Calendar event
        """
        if not self.config or not self.service or not appointment.google_calendar_event_id:
            return False, "Cannot update: No event ID or service not configured", None

        try:
            # Prepare updated event data
            event = self._prepare_event_data(appointment)

            logger.info(f"Updating Google Calendar event {appointment.google_calendar_event_id}")

            # Update the event
            updated_event = self.service.events().update(
                calendarId=self.config.calendar_id,
                eventId=appointment.google_calendar_event_id,
                body=event
            ).execute()

            # Update sync date
            appointment.google_calendar_sync_date = timezone.now()
            appointment.google_calendar_error_message = ''
            appointment.save(update_fields=['google_calendar_sync_date', 'google_calendar_error_message'])

            logger.info(f"Successfully updated Google Calendar event for appointment {appointment.id}")
            return True, "Successfully updated in Google Calendar", appointment.google_calendar_event_id

        except HttpError as e:
            error_msg = f"Google Calendar API error: {str(e)}"
            logger.error(f"Failed to update event for appointment {appointment.id}: {error_msg}")

            appointment.google_calendar_error_message = error_msg
            appointment.save(update_fields=['google_calendar_error_message'])

            return False, error_msg, None

        except Exception as e:
            error_msg = f"Error updating event: {str(e)}"
            logger.exception(error_msg)

            appointment.google_calendar_error_message = error_msg
            appointment.save(update_fields=['google_calendar_error_message'])

            return False, error_msg, None

    def delete_appointment_event(self, appointment):
        """
        Delete a Google Calendar event
        """
        if not self.config or not self.service or not appointment.google_calendar_event_id:
            return False, "Cannot delete: No event ID or service not configured"

        try:
            logger.info(f"Deleting Google Calendar event {appointment.google_calendar_event_id}")

            # Delete the event
            self.service.events().delete(
                calendarId=self.config.calendar_id,
                eventId=appointment.google_calendar_event_id
            ).execute()

            # Update appointment
            appointment.synced_to_google_calendar = False
            appointment.google_calendar_event_id = ''
            appointment.google_calendar_error_message = ''
            appointment.save(update_fields=[
                'synced_to_google_calendar',
                'google_calendar_event_id',
                'google_calendar_error_message'
            ])

            logger.info(f"Successfully deleted Google Calendar event for appointment {appointment.id}")
            return True, "Successfully deleted from Google Calendar"

        except HttpError as e:
            error_msg = f"Google Calendar API error: {str(e)}"
            logger.error(f"Failed to delete event for appointment {appointment.id}: {error_msg}")
            return False, error_msg

        except Exception as e:
            error_msg = f"Error deleting event: {str(e)}"
            logger.exception(error_msg)
            return False, error_msg
