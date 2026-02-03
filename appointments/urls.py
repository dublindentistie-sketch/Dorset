from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.home, name='home'),
    path('booking/', views.booking, name='booking'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('api/appointments/create/', views.create_appointment, name='create_appointment'),
]
