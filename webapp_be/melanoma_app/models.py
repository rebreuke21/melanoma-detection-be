from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    pass

class Image_Classification(models.Model):
    classification = models.TextField()

class Region(models.Model):
    region = models.TextField()

class ImageManager(models.Manager):
    def get_by_natural_key(self, image_classification):
        return self.get(image_classification=image_classification.classification)

class Image(models.Model):
    objects = ImageManager()

    image = models.ImageField(upload_to='images/', default=0)
    name = models.TextField()
    date_uploaded = models.DateTimeField()
    image_classification = models.ForeignKey(Image_Classification, on_delete=models.RESTRICT, default=0)
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    region = models.ForeignKey(Region, on_delete=models.RESTRICT, default=0)
    lesion_id = models.IntegerField()

    description = models.TextField()

    directory = models.TextField()

class DoctorPatients(models.Model):
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_id'
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_id'
    )
    
