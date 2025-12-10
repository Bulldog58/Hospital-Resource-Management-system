from django.db import models

class Specialty(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="e.g., Orthopedics, Cardiology, General Surgery"
    )

    class Meta:
        verbose_name_plural = "Specialties"
        ordering = ['name']

    def __str__(self):
        return self.name
    # hospitals/models.py (Continuation)

class Hospital(models.Model):
    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255)
    total_capacity = models.IntegerField(
        help_text="Maximum number of patients the hospital can admit."
    )
    # Many-to-Many relationship to Specialty
    specialties = models.ManyToManyField(
        Specialty,
        related_name='hospitals',
        help_text="Select all specialties offered by this hospital."
    )

    def __str__(self):
        return f"{self.name} ({self.address})"

    # --- Derived / Calculated Field (Week 2 Logic) ---
    # This property calculates current occupancy without storing it in the database.
    @property
    def current_occupancy(self):
        # The 'patient_set' is automatically available because Patient has a ForeignKey to Hospital.
        # We filter for patients whose status is 'IN' (admitted).
        return self.admitted_patients.filter(status='IN').count()