# patients/models.py

from django.db import models
from hospitals.models import Specialty # Import the Specialty model

class IssueSpecialtyMap(models.Model):
    issue_term = models.CharField(
        max_length=100,
        unique=True,
        help_text="Specific patient issue (e.g., 'Broken leg', 'Flu', 'Aortic event')"
    )
    primary_specialty = models.ForeignKey(
        Specialty,
        on_delete=models.CASCADE,
        related_name='mapped_issues',
        help_text="The standardized specialty this issue belongs to."
    )

    class Meta:
        verbose_name = "Issue to Specialty Map"
        verbose_name_plural = "Issue to Specialty Maps"

    def __str__(self):
        return f"{self.issue_term} -> {self.primary_specialty.name}"
    # patients/models.py (Continuation)

# Import Hospital model from the hospitals app
from hospitals.models import Hospital

class Patient(models.Model):
    # Status Choices for the recommendation/assignment logic
    STATUS_CHOICES = [
        ('PENDING', 'Pending Assignment'),
        ('IN', 'Admitted (In-Patient)'),
        ('OUT', 'Discharged (Out-Patient)'),
    ]

    name = models.CharField(max_length=255)
    age = models.IntegerField(null=True, blank=True)
    health_issue = models.CharField(
        max_length=255,
        help_text="The specific issue reported by the patient (e.g., 'Fractured arm')."
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text="Current status of the patient."
    )
    # ForeignKey relationship to Hospital (Null=True for unassigned patients)
    assigned_hospital = models.ForeignKey(
        Hospital,
        on_delete=models.SET_NULL, # If a hospital is deleted, keep the patient record but set this field to NULL
        null=True,
        blank=True,
        related_name='admitted_patients'
    )
    check_in_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Automatically set when the patient is assigned/admitted."
    )

    def __str__(self):
        return self.name