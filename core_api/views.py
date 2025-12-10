from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from hospitals.models import Hospital
from patients.models import IssueSpecialtyMap
from .serializers import HospitalRecommendationSerializer
from django.db.models import Sum, F, ExpressionWrapper, fields
from patients.models import Patient

class HospitalRecommendationView(APIView):
    """
    CORE LOGIC: Returns the top N hospitals based on specialty match and capacity score.
    Endpoint URL: /api/v1/recommend/{patient_issue}/
    """
    def get(self, request, patient_issue, format=None):
        
        # --- 1. Find the Specialty linked to the patient's Health Issue ---
        try:
            # Look up the standardized specialty based on the raw issue string
            issue_map = IssueSpecialtyMap.objects.select_related('primary_specialty').get(
                issue_term__iexact=patient_issue # Use iexact for case-insensitive match
            )
            required_specialty = issue_map.primary_specialty
        except IssueSpecialtyMap.DoesNotExist:
            return Response(
                {'error': f'No primary specialty map found for issue: "{patient_issue}".'},
                status=status.HTTP_404_NOT_FOUND
            )

        # --- 2. Filter Hospitals by that Specialty & Capacity ---
        eligible_hospitals = Hospital.objects.filter(
            specialties=required_specialty,
        ).prefetch_related('specialties') # Prefetch related specialties for efficiency

        if not eligible_hospitals.exists():
            return Response(
                {'message': f'No hospitals found specializing in {required_specialty.name}.'},
                status=status.HTTP_200_OK # Success, but empty list
            )
        
        scored_results = []
        for hospital in eligible_hospitals:
            current_occupancy = hospital.current_occupancy
            
            # --- 3. Capacity Check (Constraint) ---
            if current_occupancy >= hospital.total_capacity:
                continue # Skip hospitals that are full

            # --- 4. Calculate the Score for Ranking ---

            # Match Weight (Ensures specialty match is the priority)
            MATCH_WEIGHT = 100 
            
            # Capacity Weight (Rewards lower occupancy)
            capacity_utilization = (hospital.total_capacity - current_occupancy) / hospital.total_capacity
            CAPACITY_REWARD_SCALE = 50 
            
            # Formula: (100) + (Available_Capacity_Ratio * 50)
            score = MATCH_WEIGHT + (capacity_utilization * CAPACITY_REWARD_SCALE)

            # Build the output dictionary
            scored_results.append({
                'id': hospital.id,
                'name': hospital.name,
                'address': hospital.address,
                'specialty_match': required_specialty.name,
                'current_occupancy': current_occupancy,
                'total_capacity': hospital.total_capacity,
                'calculated_score': round(score, 2)
            })

        # Final Ranking: Sort by score (highest first) and return top N (N=3)
        final_recommendations = sorted(scored_results, key=lambda x: x['calculated_score'], reverse=True)[:3]
        
        # If no suitable hospital is found after capacity check:
        if not final_recommendations:
             return Response(
                {'message': f'Hospitals for {required_specialty.name} are available, but all are currently at capacity.'},
                status=status.HTTP_200_OK
            )
        
        # Serialize and return the top results
        serializer = HospitalRecommendationSerializer(final_recommendations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DashboardMetricsView(APIView):
    """
    API endpoint to provide aggregated metrics for the dashboard summary.
    """
    def get(self, request, format=None):
        
        # 1. Total Admitted Patients
        total_admitted_patients = Patient.objects.filter(status='IN').count()

        # 2. Total Beds and Available Capacity
        capacity_data = Hospital.objects.aggregate(
            total_capacity_sum=Sum('total_capacity'),
        )
        total_capacity_sum = capacity_data.get('total_capacity_sum') or 0
        
        # Total Current Occupancy (Calculated across all hospitals)
        total_current_occupancy = Patient.objects.filter(status='IN').count()
        
        total_available_beds = total_capacity_sum - total_current_occupancy
        
        # 3. Hospitals Near Capacity (>= 80% Occupancy)
        hospitals_near_capacity_list = []
        
        # Iterate through hospitals to calculate dynamic occupancy ratio
        for hospital in Hospital.objects.all():
            occupancy = hospital.current_occupancy
            capacity = hospital.total_capacity or 0
            
            if capacity > 0:
                occupancy_ratio = occupancy / capacity
                if occupancy_ratio >= 0.8:
                    hospitals_near_capacity_list.append({
                        'id': hospital.id,
                        'name': hospital.name,
                        'current_occupancy': occupancy,
                        'total_capacity': capacity,
                        'occupancy_ratio': round(occupancy_ratio, 2)
                    })

        data = {
            'total_admitted_patients': total_admitted_patients,
            'total_capacity': total_capacity_sum,
            'total_current_occupancy': total_current_occupancy,
            'total_available_beds': total_available_beds,
            'hospitals_near_capacity_count': len(hospitals_near_capacity_list),
            'hospitals_near_capacity': hospitals_near_capacity_list,
        }

        return Response(data, status=status.HTTP_200_OK)