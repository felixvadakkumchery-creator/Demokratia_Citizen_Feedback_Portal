from django.db import models
from django.contrib.auth.models import AbstractUser


class Login(AbstractUser):
    usertype=models.CharField(max_length=10)
    viewpassword=models.CharField(max_length=10)


class Citizen(models.Model):
    user = models.ForeignKey(Login, on_delete=models.CASCADE,null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=10, unique=True)
    pincode = models.CharField(max_length=6)
    address = models.TextField()

    state = models.CharField(max_length=100, blank=True, default='')
    district = models.CharField(max_length=100,blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')

    password = models.CharField(max_length=128, blank=True, null=True)

    aadhar = models.CharField(max_length=12, unique=True)

    proof = models.FileField(upload_to='citizen/proofs/')
    profile_pic = models.ImageField(upload_to='citizen/profile_pics/')

    registered_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.name
    
class Officers(models.Model):
    user=models.ForeignKey(Login,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    email=models.EmailField()
    mobile=models.CharField(max_length=10)
    address=models.TextField()
    department=models.CharField(max_length=100)
    district=models.CharField(max_length=100)
    taluk=models.CharField(max_length=100, blank=True, default='')
    state=models.CharField(max_length=100, blank=True, default='')
class activities(models.Model):
    user=models.ForeignKey(Login,on_delete=models.CASCADE)
    reference_number=models.CharField(max_length=100)
    date=models.DateField(auto_now_add=True)
    duration=models.DurationField()
    name_of_activity=models.CharField(max_length=100)
    department=models.CharField(max_length=100)
    village=models.CharField(max_length=100)
    taluk=models.CharField(max_length=100, blank=True, default='')
    district=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    pincode=models.CharField(max_length=6)
    description=models.TextField()
    image=models.ImageField(upload_to='activity_images/')
    before_description=models.TextField(blank=True)
    before_image=models.ImageField(upload_to='activity_images/before/', blank=True)
    after_description=models.TextField(blank=True)
    after_image=models.ImageField(upload_to='activity_images/after/', blank=True)
    map_location=models.CharField(max_length=100)


    timestamp=models.DateTimeField(auto_now_add=True)
    

class ActivityEvidence(models.Model):
    BEFORE = 'before'
    AFTER = 'after'
    STAGE_CHOICES = [
        (BEFORE, 'Before'),
        (AFTER, 'After'),
    ]

    activity = models.ForeignKey(
        activities,
        on_delete=models.CASCADE,
        related_name='evidence_images',
    )
    stage = models.CharField(max_length=6, choices=STAGE_CHOICES)
    image = models.ImageField(upload_to='activity_evidence/')

class CitizenFeedback(models.Model):

    # Optional citizen relationship for anonymous feedback
    citizen = models.ForeignKey(
        Citizen,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedbacks'
    )


    name = models.CharField(max_length=100)

    email = models.EmailField()

    message = models.TextField()

    feedback_text = models.TextField()

    rating = models.IntegerField()

    image = models.ImageField(
        upload_to='citizen_feedback_images/',
        blank=True,
        null=True
    )

    improvement_suggestions = models.TextField(
        blank=True,
        null=True
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    # Link feedback to the selected officer activity
    activity = models.ForeignKey(
        activities,
        on_delete=models.SET_NULL,
        related_name='citizen_feedback',
        blank=True,
        null=True
    )




def __str__(self):
        return f"{self.name} - {self.rating}/5"

class LocationState(models.Model):
    state=models.CharField(max_length=100)
    state_lgd_code=models.CharField(max_length=20, blank=True, default='')
class LocationDistrict(models.Model):
    state=models.ForeignKey(LocationState, on_delete=models.CASCADE)
    district=models.CharField(max_length=100)
    district_lgd_code=models.CharField(max_length=20, blank=True, default='')
class LocationTaluk(models.Model):
    state=models.ForeignKey(LocationState, on_delete=models.CASCADE)
    district=models.ForeignKey(LocationDistrict, on_delete=models.CASCADE)
    taluk=models.CharField(max_length=100, blank=True, default='')
    taluk_lgd_code=models.CharField(max_length=20, blank=True, default='')
class JsonData(models.Model):
    data = models.JSONField()
class JsonResponse(models.Model):
    response = models.JSONField()
