from django.contrib import admin
from .models import Patient, IssueSpecialtyMap

# Optional: Customize the Patient display
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'health_issue', 'assigned_hospital', 'check_in_date')
    list_filter = ('status', 'assigned_hospital')
    search_fields = ('name', 'health_issue')

# Register the models
admin.site.register(Patient, PatientAdmin)
admin.site.register(IssueSpecialtyMap)