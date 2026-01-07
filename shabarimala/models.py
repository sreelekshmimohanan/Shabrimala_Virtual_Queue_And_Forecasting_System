from django.db import models


class register(models.Model):
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    phone = models.CharField(max_length=120)
    password = models.CharField(max_length=120)


# Model for file uploads
class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.file.name


class Slot(models.Model):
    date = models.DateField()
    route = models.CharField(max_length=200)
    number_of_slots = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Slot for {self.date} - {self.route}"


class Weather(models.Model):
    date = models.DateField()
    low_temperature = models.DecimalField(max_digits=5, decimal_places=2)
    high_temperature = models.DecimalField(max_digits=5, decimal_places=2)
    windspeed = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Weather for {self.date}"


class Booking(models.Model):
    user = models.ForeignKey(register, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    aadhar_name = models.CharField(max_length=100, null=True, blank=True)
    aadhar_number = models.CharField(max_length=12)
    date_of_birth = models.DateField(null=True, blank=True)
    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking by {self.user.name} for {self.slot.date} - {self.slot.route}"


class Police(models.Model):
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=150, unique=True)
    phone = models.CharField(max_length=120)
    password = models.CharField(max_length=120)
    badge_number = models.CharField(max_length=50, unique=True)
    station = models.CharField(max_length=200)
    rank = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rank} {self.name} - {self.badge_number}"


class Emergency(models.Model):
    EMERGENCY_TYPES = [
        ('medical', 'Medical Emergency'),
        ('accident', 'Accident'),
        ('lost', 'Lost Person'),
        ('fire', 'Fire'),
        ('stampede', 'Stampede'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('responding', 'Responding'),
        ('resolved', 'Resolved'),
        ('cancelled', 'Cancelled'),
    ]
    
    reporter = models.ForeignKey(Police, on_delete=models.CASCADE, related_name='emergency_reports')
    emergency_type = models.CharField(max_length=20, choices=EMERGENCY_TYPES)
    description = models.TextField()
    location = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=15)
    medical_help_needed = models.BooleanField(default=False)
    medical_details = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reported_at = models.DateTimeField(auto_now_add=True)
    responded_by = models.ForeignKey(Police, on_delete=models.SET_NULL, null=True, blank=True, related_name='emergency_responses')
    response_notes = models.TextField(blank=True, null=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    medical_staff_assigned = models.ForeignKey('MedicalStaff', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_emergencies')
    medical_response_notes = models.TextField(blank=True, null=True)
    medical_response_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.emergency_type} - {self.location} ({self.status})"


class MedicalStaff(models.Model):
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=150, unique=True)
    phone = models.CharField(max_length=120)
    password = models.CharField(max_length=120)
    license_number = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(max_length=100)
    hospital = models.CharField(max_length=200)
    experience_years = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.name} - {self.specialization} ({self.license_number})"
