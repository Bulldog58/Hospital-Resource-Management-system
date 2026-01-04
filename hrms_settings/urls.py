"""
URL configuration for hrms_settings project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from hospitals.views import dashboard  # Import your dashboard view directly

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. THE FIX: Explicitly set the home page to your dashboard function
    path('', dashboard, name='dashboard'), 

    # 2. Keep your APIs grouped so they don't interfere with the UI
    path('api/v1/hospitals/', include('hospitals.urls')), 
    path('api/v1/patients/', include('patients.urls')),
    path('api/v1/core/', include('core_api.urls')), 
]
