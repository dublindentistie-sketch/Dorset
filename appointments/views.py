from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .models import Appointment
from datetime import datetime
import json

def home(request):
    """Home page view"""
    return render(request, 'home.html')

def booking(request):
    """Booking page view - single page booking form"""
    return render(request, 'booking.html')

def privacy_policy(request):
    """Privacy policy page view"""
    return render(request, 'privacy-policy.html')

@require_http_methods(["POST"])
def create_appointment(request):
    """Handle appointment creation via AJAX"""
    try:
        # Parse JSON data from request
        data = json.loads(request.body)

        # Extract form data
        patient_name = data.get('name')
        patient_email = data.get('email')
        patient_phone = data.get('phone')
        service_type = data.get('service')
        custom_service = data.get('custom_service', '')
        doctor_name = data.get('doctor', '')
        appointment_date = data.get('date')
        appointment_time = data.get('time')
        additional_notes = data.get('message', '')

        # If custom service is selected, validate custom_service input
        if service_type == 'custom':
            if not custom_service or custom_service.strip() == '':
                return JsonResponse({
                    'success': False,
                    'message': 'Please specify the custom service.'
                }, status=400)
            # Add custom service to notes
            additional_notes = f"Custom Service: {custom_service}\n{additional_notes}".strip()

        # Validate required fields
        if not all([patient_name, patient_email, patient_phone, service_type, appointment_date, appointment_time]):
            return JsonResponse({
                'success': False,
                'message': 'All required fields must be filled.'
            }, status=400)

        # Validate date and time
        try:
            date_obj = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            time_obj = datetime.strptime(appointment_time, '%H:%M').time()
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid date or time format.'
            }, status=400)

        # Check if date is Sunday
        if date_obj.weekday() == 6:
            return JsonResponse({
                'success': False,
                'message': 'Sorry, we are closed on Sundays. Please select another date.'
            }, status=400)

        # Check business hours
        hour = time_obj.hour
        if date_obj.weekday() == 5:  # Saturday
            if hour < 10 or hour >= 16:
                return JsonResponse({
                    'success': False,
                    'message': 'Saturday hours are 10:00 AM - 4:00 PM. Please select a valid time.'
                }, status=400)
        else:  # Weekdays
            if hour < 9 or hour >= 18:
                return JsonResponse({
                    'success': False,
                    'message': 'Weekday hours are 9:00 AM - 6:00 PM. Please select a valid time.'
                }, status=400)

        # Create appointment
        appointment = Appointment.objects.create(
            patient_name=patient_name,
            patient_email=patient_email,
            patient_phone=patient_phone,
            service_type=service_type,
            doctor_name=doctor_name,
            appointment_date=date_obj,
            appointment_time=time_obj,
            additional_notes=additional_notes
        )

        return JsonResponse({
            'success': True,
            'message': 'Thank you! Your appointment request has been received. We will contact you within 24 hours to confirm your booking.',
            'appointment_id': appointment.id
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)
