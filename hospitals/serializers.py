from rest_framework import serializers
from .models import Specialty, Hospital

# --- 1. Specialty Serializer ---
class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = ['id', 'name']

# --- 2. Hospital Serializer ---
class HospitalSerializer(serializers.ModelSerializer):
    # This field will list the names of specialties, not just their IDs
    specialties = SpecialtySerializer(many=True, read_only=True)
    
    # Add a custom read-only field for the dynamically calculated occupancy
    current_occupancy = serializers.ReadOnlyField() 
    
    class Meta:
        model = Hospital
        fields = ['id', 'name', 'address', 'total_capacity', 'specialties', 'current_occupancy']
        read_only_fields = ['current_occupancy']

    # Custom handling for POST/PUT: allowing specialties to be set by ID
    def to_internal_value(self, data):
        # Convert list of specialty IDs back into model instances for saving
        if 'specialty_ids' in data:
            data['specialties'] = data.pop('specialty_ids')
        return super().to_internal_value(data)

    def to_representation(self, instance):
        # The default representation includes the full SpecialtySerializer output
        return super().to_representation(instance)
    