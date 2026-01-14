from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q, F
from django.db import models
from django.utils import timezone # For filtering upcoming appointments
from django.contrib import messages
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
import json

# Import your models - Ensure Patient and Appointment are here!
from .models import Hospital, Specialty, Patient, Appointment 
from .serializers import HospitalSerializer, SpecialtySerializer

# --- Template View for Frontend ---

def dashboard(request):
    query = request.GET.get('search')
    hospitals = Hospital.objects.all()
    
    if query:
        hospitals = hospitals.filter(
            Q(name__icontains=query) | Q(address__icontains=query)
        )

    specialties = Specialty.objects.all()
    
    # 1. NEW: Fetch 5 Upcoming Appointments for the Sidebar/List
    upcoming_appointments = Appointment.objects.filter(
        appointment_date__gte=timezone.now(),
        status='scheduled'
    ).order_by('appointment_date')[:5]

    # 2. NEW: Count Pending Appointments for the Stat Box
    pending_count = Appointment.objects.filter(
        status='scheduled', 
        appointment_date__gte=timezone.now()
    ).count()

    # 3. Data for the Chart (Optimized)
    chart_labels = [s.name for s in specialties]
    chart_data = [Hospital.objects.filter(specialties=s).count() for s in specialties]

    context = {
        'hospitals': hospitals,
        'specialties': specialties,
        'upcoming_appointments': upcoming_appointments, # For Step 1
        'pending_count': pending_count,                 # New Stat
        'hosp_count': hospitals.count(),
        'spec_count': specialties.count(),
        'total_capacity': sum(h.total_capacity for h in hospitals),
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'hospitals/index.html', context)

# ... (Keep your HospitalViewSet, RecommendationView, and SpecialtyViewSet as they are) ...