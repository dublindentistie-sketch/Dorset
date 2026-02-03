# Dublin Dentist Clinic - Appointment Booking System

A modern, Django-based dental clinic appointment management system with a single-page booking form design.

![Django](https://img.shields.io/badge/Django-5.2-green.svg)
![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![License](https://img.shields.io/badge/License-Private-red.svg)

## 🦷 Overview

Dublin Dentist Clinic is a professional web-based appointment booking system designed for dental practices. The system features a streamlined single-page booking form inspired by modern clinic booking interfaces.

### Key Features

- **Single-Page Booking Form** - Simplified user experience with no multi-step process
- **Real-time Validation** - Instant feedback on form inputs
- **Business Hours Enforcement** - Automatic validation of appointment times
- **Responsive Design** - Works seamlessly on desktop, tablet, and mobile
- **Google Calendar Integration** - Sync appointments with Google Calendar
- **Email Notifications** - Automatic confirmation emails
- **Admin Dashboard** - Full appointment management via Django Admin

## 📋 Requirements

- Python 3.8+
- Django 5.2+
- SQLite (development) / PostgreSQL (production)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository_url>
cd Dorset
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Admin User
```bash
python manage.py createsuperuser
```

### 6. Collect Static Files
```bash
python manage.py collectstatic
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to see the application.

## 📁 Project Structure

```
Dorset/
├── appointments/           # Main Django application
│   ├── admin.py           # Admin configuration
│   ├── models.py          # Data models
│   ├── views.py           # View functions
│   ├── urls.py            # URL routing
│   ├── services.py        # Business logic
│   └── google_calendar_service.py
│
├── dental_clinic/         # Django project settings
│   ├── settings.py        # Development settings
│   ├── urls.py            # Root URL configuration
│   └── wsgi.py            # WSGI configuration
│
├── templates/             # HTML templates
│   ├── home.html          # Homepage
│   ├── booking.html       # Booking form
│   └── privacy-policy.html
│
├── static/                # Static assets
│   ├── css/styles.css     # Main stylesheet
│   ├── js/script.js       # JavaScript
│   └── images/            # Images
│
├── manage.py              # Django CLI
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### Business Hours

Default business hours are configured in `appointments/views.py`:

| Day | Hours |
|-----|-------|
| Monday - Friday | 9:00 AM - 6:00 PM |
| Saturday | 10:00 AM - 4:00 PM |
| Sunday | Closed |

## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete system architecture documentation
- **[BOOKING_SYSTEM_DOCUMENTATION_EN.md](BOOKING_SYSTEM_DOCUMENTATION_EN.md)** - Booking system technical documentation (English)
- **[BOOKING_SYSTEM_DOCUMENTATION.md](BOOKING_SYSTEM_DOCUMENTATION.md)** - Booking system technical documentation (Chinese)

## 🔌 API Endpoints

### Create Appointment
```http
POST /api/appointments/create/
Content-Type: application/json
X-CSRFToken: <token>
```

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "0879098400",
  "service": "checkup",
  "date": "2025-12-15",
  "time": "10:30",
  "message": "Optional message"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Your appointment request has been received.",
  "appointment_id": 123
}
```

## 🔐 Security Features

- CSRF Protection
- XSS Prevention
- SQL Injection Protection
- Secure Session Management
- HTTPS Ready (production)
- GDPR Compliant

## 📱 Responsive Design

The application is fully responsive and optimized for:
- Desktop (1024px+)
- Tablet (768px - 1024px)
- Mobile (< 768px)

## 🛠️ Development

### Running Tests
```bash
python manage.py test
```

### Code Style
The project follows PEP 8 style guidelines for Python code.

## 📦 Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn dental_clinic.wsgi:application --bind 0.0.0.0:8000
```

### Nginx Configuration
See `nginx.conf` for sample configuration.

### Systemd Service
See `gunicorn.service` for sample systemd configuration.

## 📞 Contact

**Dublin Dentist Clinic**  
- **Address**: 43 Lower Dorset Street, Dublin 1, Ireland
- **Phone**: 087 909 8400
- **Email**: Dublindentist.ie@gmail.com

## 📄 License

This project is proprietary software. All rights reserved.

---

**Built with ❤️ for Dublin Dentist Clinic**
