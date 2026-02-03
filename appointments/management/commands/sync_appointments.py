"""
Django management command to manually sync appointments to doctor platform
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from appointments.models import Appointment
from appointments.services import DoctorPlatformAPIService


class Command(BaseCommand):
    help = 'Sync appointments to doctor platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Sync all appointments (including already synced)',
        )
        parser.add_argument(
            '--unsynced-only',
            action='store_true',
            help='Sync only unsynced appointments (default)',
        )
        parser.add_argument(
            '--failed-only',
            action='store_true',
            help='Retry only failed appointments',
        )
        parser.add_argument(
            '--appointment-id',
            type=int,
            help='Sync specific appointment by ID',
        )
        parser.add_argument(
            '--days',
            type=int,
            help='Sync appointments from the last N days',
        )

    def handle(self, *args, **options):
        api_service = DoctorPlatformAPIService()

        if not api_service.config:
            self.stdout.write(self.style.ERROR('No active doctor platform configuration found'))
            return

        self.stdout.write(self.style.SUCCESS(f'Using platform: {api_service.config.name}'))
        self.stdout.write(self.style.SUCCESS(f'API URL: {api_service.config.api_url}'))

        # Determine which appointments to sync
        if options['appointment_id']:
            # Sync specific appointment
            try:
                appointment = Appointment.objects.get(id=options['appointment_id'])
                appointments = [appointment]
                self.stdout.write(f'Syncing appointment ID: {options["appointment_id"]}')
            except Appointment.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Appointment {options["appointment_id"]} not found'))
                return

        elif options['failed_only']:
            # Sync only appointments with errors
            appointments = Appointment.objects.filter(
                synced_to_platform=False
            ).exclude(sync_error_message='')
            self.stdout.write(f'Found {appointments.count()} failed appointments')

        elif options['all']:
            # Sync all appointments
            if options['days']:
                cutoff_date = timezone.now() - timedelta(days=options['days'])
                appointments = Appointment.objects.filter(created_at__gte=cutoff_date)
            else:
                appointments = Appointment.objects.all()
            self.stdout.write(f'Found {appointments.count()} appointments to sync')

        else:
            # Default: sync only unsynced appointments
            if options['days']:
                cutoff_date = timezone.now() - timedelta(days=options['days'])
                appointments = Appointment.objects.filter(
                    synced_to_platform=False,
                    created_at__gte=cutoff_date
                )
            else:
                appointments = Appointment.objects.filter(synced_to_platform=False)
            self.stdout.write(f'Found {appointments.count()} unsynced appointments')

        if not appointments:
            self.stdout.write(self.style.WARNING('No appointments to sync'))
            return

        # Sync appointments
        success_count = 0
        failure_count = 0

        for appointment in appointments:
            self.stdout.write(f'\nSyncing appointment {appointment.id}...')
            self.stdout.write(f'  Patient: {appointment.patient_name}')
            self.stdout.write(f'  Date: {appointment.appointment_date} at {appointment.appointment_time}')

            success, message, platform_id = api_service.send_appointment(appointment)

            if success:
                success_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Success (Platform ID: {platform_id})'))
            else:
                failure_count += 1
                self.stdout.write(self.style.ERROR(f'  ✗ Failed: {message}'))

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'Successfully synced: {success_count}'))
        if failure_count > 0:
            self.stdout.write(self.style.ERROR(f'Failed: {failure_count}'))
        self.stdout.write('='*50)
