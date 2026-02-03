"""
Management command to authorize Google Calendar OAuth access (Manual Flow)
This works with web-type OAuth clients
Usage: python manage.py authorize_google_calendar_manual
"""
import json
from django.core.management.base import BaseCommand
from google_auth_oauthlib.flow import Flow
from appointments.models import GoogleCalendarConfig


class Command(BaseCommand):
    help = 'Authorize Google Calendar OAuth access using manual flow (for web-type clients)'

    SCOPES = ['https://www.googleapis.com/auth/calendar']

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Google Calendar OAuth Authorization (Manual Flow)'))
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

            # Handle web-type credentials
            if 'web' in credentials_info:
                # Use urn:ietf:wg:oauth:2.0:oob for manual flow
                flow = Flow.from_client_config(
                    credentials_info,
                    scopes=self.SCOPES,
                    redirect_uri='urn:ietf:wg:oauth:2.0:oob'
                )

                # Get authorization URL
                auth_url, _ = flow.authorization_url(prompt='consent')

                self.stdout.write(self.style.WARNING('=' * 80))
                self.stdout.write(self.style.WARNING('STEP 1: Open this URL in your browser:'))
                self.stdout.write('')
                self.stdout.write(self.style.HTTP_INFO(auth_url))
                self.stdout.write('')
                self.stdout.write(self.style.WARNING('=' * 80))
                self.stdout.write('')
                self.stdout.write('1. Copy the URL above and paste it into your browser')
                self.stdout.write('2. Sign in with your Google account')
                self.stdout.write('3. Grant permission to access your calendar')
                self.stdout.write('4. You will see an authorization code')
                self.stdout.write('5. Copy that code and paste it below')
                self.stdout.write('')
                self.stdout.write(self.style.WARNING('=' * 80))

                # Get authorization code from user
                auth_code = input('STEP 2: Enter the authorization code: ').strip()

                if not auth_code:
                    self.stdout.write(self.style.ERROR('No authorization code provided.'))
                    return

                self.stdout.write('')
                self.stdout.write('Processing authorization code...')

                # Exchange code for token
                flow.fetch_token(code=auth_code)
                credentials = flow.credentials

                # Save token to database
                config.token_json = credentials.to_json()
                config.is_authorized = True
                config.save(update_fields=['token_json', 'is_authorized'])

                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS('=' * 80))
                self.stdout.write(self.style.SUCCESS('✓ Successfully authorized Google Calendar access!'))
                self.stdout.write(self.style.SUCCESS('=' * 80))
                self.stdout.write('')
                self.stdout.write('You can now use Google Calendar integration.')
                self.stdout.write('The token has been saved and will be automatically refreshed.')

            else:
                self.stdout.write(self.style.ERROR(
                    'This command is for web-type OAuth clients. '
                    'Please use authorize_google_calendar for desktop-type clients.'
                ))

        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(
                f'Error parsing credentials JSON: {str(e)}'
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Authorization failed: {str(e)}'
            ))
            self.stdout.write('')
            self.stdout.write('Please check:')
            self.stdout.write('  - The authorization code is correct')
            self.stdout.write('  - The code has not expired (use it within a few minutes)')
            self.stdout.write('  - Your Google account has access to Google Calendar')
