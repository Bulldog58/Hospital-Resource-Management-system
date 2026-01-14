from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q, F
from django.db import models
from django.utils import timezone
from django.contrib import messages
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
import json

# Import your models
from .models import Hospital, Specialty, Patient, Appointment 
from .serializers import HospitalSerializer, SpecialtySerializer

# --- 1. THE DASHBOARD VIEW ---
def dashboard(request):
    query = request.GET.get('search')
    hospitals = Hospital.objects.all()
    
    if query:
        hospitals = hospitals.filter(
            Q(name__icontains=query) | Q(address__icontains=query)
        )

    specialties = Specialty.objects.all()
    
    upcoming_appointments = Appointment.objects.filter(
        appointment_date__gte=timezone.now(),
        status='scheduled'
    ).order_by('appointment_date')[:5]

    pending_count = Appointment.objects.filter(
        status='scheduled', 
        appointment_date__gte=timezone.now()
    ).count()

    chart_labels = [s.name for s in specialties]
    chart_data = [Hospital.objects.filter(specialties=s).count() for s in specialties]

    context = {
        'hospitals': hospitals,
        'specialties': specialties,
        'upcoming_appointments': upcoming_appointments,
        'pending_count': pending_count,
        'hosp_count': hospitals.count(),
        'spec_count': specialties.count(),
        'total_capacity': sum(h.total_capacity for h in hospitals),
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'hospitals/index.html', context)

# --- 2. THE MISSING VIEWSETS (The ones causing the error) ---

class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['address', 'name']

class SpecialtyViewSet(viewsets.ModelViewSet):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer

class RecommendationView(generics.ListAPIView):
    serializer_class = HospitalSerializer

    def get_queryset(self):
        issue_query = self.request.query_params.get('issue', None)
        if not issue_query:
            return Hospital.objects.none()

        queryset = Hospital.objects.annotate(
            active_patients=Count('admitted_patients', filter=Q(admitted_patients__status='IN'))
        ).filter(
            specialties__name__icontains=issue_query,
            active_patients__lt=models.F('total_capacity')
        ).order_by('active_patients')

        return queryset[:3]

def delete_hospital(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)
    if request.method == 'POST':
        hospital.delete()
    return redirect('dashboard')