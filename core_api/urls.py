from django.urls import path
from . import views

urlpatterns = [
    # The CORE LOGIC endpoint
    path('recommend/<str:patient_issue>/', views.HospitalRecommendationView.as_view(), name='hospital-recommendation'),
    
    # The DASHBOARD endpoint (NEW)
    path('dashboard/', views.DashboardMetricsView.as_view(), name='dashboard-metrics'),
]