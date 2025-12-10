from rest_framework import serializers

class HospitalRecommendationSerializer(serializers.Serializer):
    """
    Custom serializer for outputting the ranked list of hospitals.
    """
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    address = serializers.CharField(max_length=255)
    specialty_match = serializers.CharField(max_length=100)
    current_occupancy = serializers.IntegerField()
    total_capacity = serializers.IntegerField()
    calculated_score = serializers.FloatField()