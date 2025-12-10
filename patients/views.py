from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import Patient, IssueSpecialtyMap
from .serializers import PatientSerializer, IssueSpecialtyMapSerializer # Ensure serializers are imported
from hospitals.models import Hospital

class IssueSpecialtyMapViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and managing Issue to Specialty mappings.
    """
    queryset = IssueSpecialtyMap.objects.all()
    serializer_class = IssueSpecialtyMapSerializer

# The missing class!
class PatientViewSet(viewsets.ModelViewSet): 
    """
    API endpoint for viewing, creating, and managing Patient records.
    """
    queryset = Patient.objects.all().order_by('-id')
    serializer_class = PatientSerializer

    # CORE ASSIGNMENT LOGIC (PUT/PATCH /patients/{id}/assign/)
    @action(detail=True, methods=['patch', 'put'])
    def assign(self, request, pk=None):
        """
        Assigns a patient to a specific hospital, updating their status and check-in date.
        """
        patient = self.get_object()
        hospital_id = request.data.get('hospital_id')

        if not hospital_id:
            return Response({'error': 'Hospital ID is required for assignment.'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(pk=hospital_id)
        except Hospital.DoesNotExist:
            return Response({'error': 'Hospital not found.'}, 
                            status=status.HTTP_404_NOT_FOUND)

        # Check Capacity 
        if hospital.current_occupancy >= hospital.total_capacity:
            return Response({'error': f'{hospital.name} is at full capacity ({hospital.total_capacity}).'}, 
                            status=status.HTTP_409_CONFLICT)
        
        # Update Patient Record
        patient.assigned_hospital = hospital
        patient.status = 'IN'
        patient.check_in_date = timezone.now()
        patient.save()

        # Return the updated patient data
        serializer = self.get_serializer(patient)
        return Response(serializer.data, status=status.HTTP_200_OK)