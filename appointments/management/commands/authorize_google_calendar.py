"""
Management command to authorize Google Calendar OAuth access
Usage: python manage.py authorize_google_calendar
"""
import json
from django.core.management.base import BaseCommand
from google_auth_oauthlib.flow import InstalledAppFlow
from appointments.models import GoogleCalendarConfig


class Command(BaseCommand):
    help = 'Authorize Google Calendar OAuth access'

    SCOPES = ['https://www.googleapis.com/auth/calendar']

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Google Calendar OAuth Authorization'))
        self.stdout.write('')

        # Get active OAuth config
        config = GoogleCalendarConfig.objects.filter(
            is_active=True,
            auth_type='oauth'
        ).first()

        if not config:
            self.stdout.write(self.style.ERROR(
                'No active OAuth Google Calendar configuration found.'
            ))
            self.stdout.write(
                'Please create a Google Calendar Config in Django Admin first:'
            )
            self.stdout.write('  1. Go to /admin/appointments/googlecalendarconfig/')
            self.stdout.write('  2. Add a new configuration')
            self.stdout.write('  3. Set Auth Type to "OAuth 2.0"')
            self.stdout.write('  4. Paste your client_secret JSON content')
            return

        if not config.credentials_json:
            self.stdout.write(self.style.ERROR(
                'Credentials JSON is empty in the configuration.'
            ))
            return

        self.stdout.write(f'Found configuration: {config.name}')
        self.stdout.write(f'Calendar ID: {config.calendar_id}')
        self.stdout.write('')

        try:
            # Parse credentials
            credentials_info = json.loads(config.credentials_json)

            # Check if it's a valid OAuth client secret file
            if 'web' not in credentials_info and 'installed' not in credentials_info:
                self.stdout.write(self.style.ERROR(
                    'Invalid OAuth credentials format. '
                    'Please ensure you uploaded an OAuth 2.0 Client Secret JSON file.'
                ))
                return

            self.stdout.write(self.style.WARNING(
                'Starting OAuth authorization flow...'
            ))
            self.stdout.write('')
            self.stdout.write(
                'A browser window will open for you to authorize access to your Google Calendar.'
            )
            self.stdout.write(
                'If the browser does not open automatically, please copy and paste the URL shown below.'
            )
            self.stdout.write('')

            # Check client type and handle accordingly
            if 'installed' in credentials_info:
                # Desktop app type
                flow = InstalledAppFlow.from_client_config(
                    credentials_info,
                    scopes=self.SCOPES
                )
                credentials = flow.run_local_server(
                    port=8080,
                    prompt='consent',
                    success_message='Authorization successful! You can close this window.'
                )
            else:
                # Web app type - use manual flow
                self.stdout.write(self.style.WARNING(
                    'Detected web-type OAuth client. Using manual authorization flow.'
                ))
                self.stdout.write('')

                # For web type, we need to add redirect URI
                if 'web' in credentials_info:
                    credentials_info = credentials_info.copy()
                    # Add localhost redirect URI
                    if 'redirect_uris' not in credentials_info['web']:
                        credentials_info['web']['redirect_uris'] = ['http://localhost:8080/']

                flow = InstalledAppFlow.from_client_config(
                    credentials_info,
                    scopes=self.SCOPES,
                    redirect_uri='http://localhost:8080/'
                )

                credentials = flow.run_local_server(
                    port=8080,
                    prompt='consent',
                    success_message='Authorization successful! You can close this window.'
                )

            # Save token to database
            config.token_json = credentials.to_json()
            config.is_authorized = True
            config.save(update_fields=['token_json', 'is_authorized'])

            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS(
                '✓ Successfully authorized Google Calendar access!'
            ))
            self.stdout.write('')
            self.stdout.write('You can now use Google Calendar integration.')
            self.stdout.write('The token has been saved and will be automatically refreshed.')

        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(
                f'Error parsing credentials JSON: {str(e)}'
            ))
            self.stdout.write('Please check the credentials in Django Admin.')

        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Authorization failed: {str(e)}'
            ))
            self.stdout.write('')
            self.stdout.write('Common issues:')
            self.stdout.write('  - Port 8080 is already in use')
            self.stdout.write('  - Browser blocked the authorization popup')
            self.stdout.write('  - Invalid OAuth credentials')
