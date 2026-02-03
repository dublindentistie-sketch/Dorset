# Dublin Dentist Clinic - Booking System Technical Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Technology Stack](#technology-stack)
3. [System Architecture](#system-architecture)
4. [File Structure](#file-structure)
5. [Database Design](#database-design)
6. [API Documentation](#api-documentation)
7. [Frontend Implementation](#frontend-implementation)
8. [Backend Logic](#backend-logic)
9. [Deployment Guide](#deployment-guide)
10. [Maintenance Guide](#maintenance-guide)

---

## System Overview

### Project Introduction
Dublin Dentist Clinic Booking System is a Django-based online dental clinic appointment platform, featuring a single-page form design inspired by Clinic4u's clean style, providing convenient appointment services.

### Core Features
- ✅ Single-page form booking system
- ✅ Multiple dental service options
- ✅ Date and time selection
- ✅ Business hours validation
- ✅ Form data validation
- ✅ AJAX asynchronous submission
- ✅ Responsive design (mobile-friendly)
- ✅ Appointment management

### Design Philosophy
Inspired by Clinic4u's clean booking system design, using a single-page form instead of multi-step process to enhance user experience.

---

## Technology Stack

### Backend Technologies
- **Framework**: Django 5.2
- **Language**: Python 3.x
- **Database**: SQLite (development) / PostgreSQL (recommended for production)
- **API**: RESTful JSON API

### Frontend Technologies
- **HTML5**: Semantic markup
- **CSS3**: Responsive design, Flexbox, Grid
- **JavaScript**: ES6+, Fetch API
- **Fonts**: Google Fonts (Lora, Varela)

### Development Tools
- **Version Control**: Git
- **Package Manager**: pip
- **Static Files**: Django Static Files

---

## System Architecture

```
┌─────────────────────────────────────────────────┐
│                   User Interface                 │
│  (HTML5 + CSS3 + JavaScript)                    │
└─────────────────┬───────────────────────────────┘
                  │
                  │ AJAX Request (JSON)
                  ▼
┌─────────────────────────────────────────────────┐
│              Django Backend Service              │
│  ┌─────────────────────────────────────────┐   │
│  │         URL Router (urls.py)            │   │
│  └────────────────┬────────────────────────┘   │
│                   │                              │
│  ┌────────────────▼────────────────────────┐   │
│  │         Views (views.py)                │   │
│  │  - Form validation                      │   │
│  │  - Business logic processing            │   │
│  │  - Time validation                      │   │
│  └────────────────┬────────────────────────┘   │
│                   │                              │
│  ┌────────────────▼────────────────────────┐   │
│  │       Models (models.py)                │   │
│  │  - Appointment Model                    │   │
│  └────────────────┬────────────────────────┘   │
└───────────────────┼──────────────────────────────┘
                    │
                    ▼
          ┌──────────────────┐
          │  SQLite/PostgreSQL│
          │      Database     │
          └──────────────────┘
```

---

## File Structure

```
Dorset/
├── appointments/                 # Appointments application
│   ├── migrations/              # Database migration files
│   ├── __init__.py
│   ├── admin.py                 # Django Admin configuration
│   ├── apps.py                  # Application configuration
│   ├── models.py                # Data models (Appointment)
│   ├── urls.py                  # URL routing configuration
│   ├── views.py                 # View functions
│   ├── services.py              # Business logic
│   ├── signals.py               # Django signals
│   └── google_calendar_service.py  # Google Calendar integration
│
├── dental_clinic/               # Project configuration
│   ├── __init__.py
│   ├── settings.py              # Project settings
│   ├── urls.py                  # Main URL configuration
│   ├── wsgi.py                  # WSGI configuration
│   └── asgi.py                  # ASGI configuration
│
├── templates/                   # HTML templates
│   ├── home.html                # Homepage (with Hero section)
│   ├── booking.html             # Booking form page ⭐
│   └── privacy-policy.html      # Privacy policy
│
├── static/                      # Static resources
│   ├── css/
│   │   └── styles.css           # Main stylesheet
│   ├── js/
│   │   └── script.js            # Main JavaScript file
│   └── images/                  # Image resources
│       ├── favicon.jpg
│       └── 4.jpg
│
├── manage.py                    # Django management script
└── requirements.txt             # Python dependencies
```

---

## Database Design

### Appointment Model

**Model file**: `appointments/models.py`

```python
class Appointment(models.Model):
    """Appointment information model"""

    # Patient Information
    patient_name = CharField(max_length=200)       # Patient name
    patient_email = EmailField()                   # Patient email
    patient_phone = CharField(max_length=20)       # Patient phone

    # Appointment Details
    service_type = CharField(max_length=100)       # Service type
    doctor_name = CharField(max_length=200)        # Doctor name (optional)
    appointment_date = DateField()                 # Appointment date
    appointment_time = TimeField()                 # Appointment time
    additional_notes = TextField()                 # Additional notes

    # System Fields
    created_at = DateTimeField(auto_now_add=True)  # Created timestamp
    updated_at = DateTimeField(auto_now=True)      # Updated timestamp
    status = CharField(max_length=20)              # Appointment status
```

### Service Type Options
| Value | Description |
|-------|-------------|
| `checkup` | Check-up |
| `cleaning` | Cleaning and Polishing |
| `filling` | Filling |
| `root-canal` | Root Canal Treatment |
| `extraction` | Extraction |
| `implant` | Dental Implant |
| `crown` | Crown/Bridge/Veneer |
| `denture` | Dentures |
| `orthodontics` | Orthodontics |
| `pediatric` | Pediatric Dentistry |
| `emergency` | Emergency |
| `other` | Other |

---

## API Documentation

### 1. Create Appointment

**Endpoint**: `POST /api/appointments/create/`

**Request Headers**:
```http
Content-Type: application/json
X-CSRFToken: <csrf_token>
```

**Request Parameters**:
```json
{
  "name": "John Doe",                            // Required
  "email": "john@example.com",                   // Required
  "phone": "0879098400",                         // Required
  "service": "checkup",                          // Required
  "date": "2025-12-15",                          // Required (YYYY-MM-DD)
  "time": "10:30",                               // Required (HH:MM)
  "message": "Best time to call: morning\nHeard about us from: google\nMessage: Need cleaning service"  // Optional
}
```

**Success Response** (200):
```json
{
  "success": true,
  "message": "Thank you! Your appointment request has been received. We will contact you within 24 hours to confirm your booking.",
  "appointment_id": 123
}
```

**Error Response** (400):
```json
{
  "success": false,
  "message": "All required fields must be filled."
}
```

**Business Validation Rules**:
1. ✅ All required fields cannot be empty
2. ✅ Date format must be `YYYY-MM-DD`
3. ✅ Time format must be `HH:MM`
4. ✅ Cannot book on Sunday (clinic closed)
5. ✅ Monday to Friday business hours: 09:00 - 18:00
6. ✅ Saturday business hours: 10:00 - 16:00
7. ✅ Email format validation
8. ✅ Phone number format validation

---

## Frontend Implementation

### 1. Booking Form Page (booking.html)

#### Page Structure
```html
<div class="booking-page">
  <div class="booking-container">
    <div class="booking-header">
      <h2>Dublin Dentist Clinic Booking Form</h2>
    </div>

    <form id="bookingForm">
      <!-- Name Fields -->
      <div class="form-row">
        <div class="form-group">First Name*</div>
        <div class="form-group">Last Name*</div>
      </div>

      <!-- Contact Information -->
      <div class="form-group">Email Address*</div>
      <div class="form-group">Phone Number*</div>

      <!-- Appointment Information -->
      <div class="form-group">Appointment Type*</div>
      <div class="form-group">Preferred Appointment Date*</div>
      <div class="form-group">Preferred Appointment Time*</div>

      <!-- Additional Information -->
      <div class="form-group">Best time to call you?</div>
      <div class="form-group">Message (optional)</div>
      <div class="form-group">Where did you hear about us?*</div>

      <button type="submit">Submit</button>
      <div class="form-message"></div>
    </form>
  </div>
</div>
```

#### Key CSS Styles
```css
/* Form Container */
.booking-container {
  max-width: 600px;
  margin: 0 auto;
  background: white;
  padding: 50px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

/* Two-column Layout */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

/* Form Inputs */
.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #cbd5e0;
  border-radius: 5px;
  transition: all 0.3s ease;
}

/* Focus Effect */
.form-group input:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

/* Responsive Design */
@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
```

#### JavaScript Form Handling

**Core Functions**:

1. **Date Restriction**:
```javascript
// Set minimum date to today
const dateInput = document.getElementById('appointmentDate');
const today = new Date().toISOString().split('T')[0];
dateInput.setAttribute('min', today);
```

2. **Form Submission**:
```javascript
document.getElementById('bookingForm').addEventListener('submit', async function(e) {
  e.preventDefault();

  // Collect form data
  const formData = {
    name: firstName + ' ' + lastName,
    email: email,
    phone: phone,
    service: appointmentType,
    date: appointmentDate,
    time: appointmentTime,
    message: additionalNotes
  };

  // AJAX submission
  const response = await fetch('/api/appointments/create/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken
    },
    body: JSON.stringify(formData)
  });

  // Handle response
  const data = await response.json();
  if (data.success) {
    // Show success message
    // Reset form
    // Scroll to top
  }
});
```

---

## Backend Logic

### 1. URL Routing Configuration (appointments/urls.py)

```python
from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.home, name='home'),
    path('booking/', views.booking, name='booking'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('api/appointments/create/', views.create_appointment, name='create_appointment'),
]
```

### 2. View Functions (appointments/views.py)

#### Booking View
```python
def booking(request):
    """Booking page view - single-page booking form"""
    return render(request, 'booking.html')
```

#### Create Appointment View

**Processing Flow**:
```
1. Parse JSON request data
   ↓
2. Extract form fields
   ↓
3. Validate required fields
   ↓
4. Validate date and time format
   ↓
5. Check if Sunday (closed)
   ↓
6. Validate business hours
   - Monday-Friday: 9:00 - 18:00
   - Saturday: 10:00 - 16:00
   ↓
7. Create appointment record
   ↓
8. Return success response (with appointment ID)
```

---

## Deployment Guide

### 1. Development Environment Setup

```bash
# Clone project
git clone <repository_url>
cd Dorset

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Database migration
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run development server
python manage.py runserver
```

### 2. Production Deployment

#### Environment Variables
```bash
# .env file
DEBUG=False
SECRET_KEY=<your-secret-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
```

#### settings.py Configuration
```python
# Production settings
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000

# Database (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dental_clinic',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

#### Nginx Configuration Example
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /path/to/Dorset/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Maintenance Guide

### 1. Daily Maintenance Tasks

#### View Appointment Records
```bash
# Django Admin
Visit: http://yourdomain.com/admin

# Using Django Shell
python manage.py shell
>>> from appointments.models import Appointment
>>> Appointment.objects.all()
>>> Appointment.objects.filter(appointment_date='2025-12-15')
```

#### Data Backup
```bash
# Backup database
python manage.py dumpdata > backup.json

# Restore database
python manage.py loaddata backup.json
```

### 2. Common Troubleshooting

#### Form Submission Failure
1. Check if CSRF Token is correct
2. Check JavaScript console errors
3. Check network requests and responses
4. View Django logs

#### Date Validation Failure
1. Confirm client timezone settings
2. Check if date format is YYYY-MM-DD
3. Verify business hours logic

#### Static Files Not Loading
```bash
# Recollect static files
python manage.py collectstatic --noinput

# Check STATIC_URL and STATIC_ROOT configuration
```

### 3. Performance Optimization

1. **Database Optimization**
   - Add indexes for frequently queried fields
   - Use select_related to reduce query count

2. **Caching Strategy**
   - Use Redis to cache appointment time slots
   - Cache static content

3. **Frontend Optimization**
   - Minify CSS/JS files
   - Use CDN for static resources
   - Enable browser caching

### 4. Security Recommendations

1. **Regular Updates**
   - Regularly update Django version
   - Update dependency packages

2. **Access Control**
   - Restrict Admin panel access
   - Use strong password policy

3. **Log Monitoring**
   - Monitor abnormal appointment requests
   - Record API call frequency

---

## Feature Extension Roadmap

### Short-term Extensions
- ✅ Email confirmation notifications
- ✅ SMS reminders
- ✅ Google Calendar integration
- ✅ Appointment status management
- ✅ Cancel/Reschedule appointments

### Medium-term Extensions
- 🔲 Multi-language support
- 🔲 Payment integration
- 🔲 Customer account system
- 🔲 Appointment history
- 🔲 Doctor scheduling management

### Long-term Extensions
- 🔲 Mobile application (React Native)
- 🔲 AI smart time recommendations
- 🔲 Video consultation feature
- 🔲 Prescription management system
- 🔲 Data analytics dashboard

---

## Contact Information

**Project Maintainer**: Dublin Dentist Clinic IT Team  
**Email**: Dublindentist.ie@gmail.com  
**Phone**: 087 909 8400  
**Address**: 43 Lower Dorset Street, Dublin 1, Ireland

---

## Changelog

### Version 2.0.0 (2025-01-04)
- ✅ Refactored to single-page form design
- ✅ Clinic4u-inspired styling
- ✅ Added date and time selection
- ✅ Removed old multi-step process
- ✅ Improved responsive design
- ✅ Enhanced form validation logic

### Version 1.0.0 (Initial Release)
- ✅ Basic booking system
- ✅ Multi-step booking process
- ✅ Google Calendar integration

---

**Documentation Last Updated**: February 1, 2026  
**Django Version**: 5.2  
**Python Version**: 3.x
