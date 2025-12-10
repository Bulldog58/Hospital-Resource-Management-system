from django.contrib import admin
from .models import Specialty, Hospital

# Optional: Customize the Hospital display for better clarity
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'total_capacity', 'current_occupancy_display')
    filter_horizontal = ('specialties',) # Use a nice interface for ManyToMany fields

    # Method to display the calculated occupancy in the admin list view
    def current_occupancy_display(self, obj):
        return obj.current_occupancy
    current_occupancy_display.short_description = 'Occupancy (IN)'

# Register the models
admin.site.register(Specialty)
admin.site.register(Hospital, HospitalAdmin)