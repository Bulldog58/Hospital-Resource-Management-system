from rest_framework import viewsets
from .models import Specialty, Hospital
from .serializers import SpecialtySerializer, HospitalSerializer

# API ViewSet for Specialty Model
class SpecialtyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Specialties to be viewed or edited.
    """
    queryset = Specialty.objects.all().order_by('name')
    serializer_class = SpecialtySerializer

# API ViewSet for Hospital Model (The missing class!)
class HospitalViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Hospitals to be viewed or edited.
    Includes calculated current occupancy.
    """
    queryset = Hospital.objects.all().order_by('name')
    serializer_class = HospitalSerializer