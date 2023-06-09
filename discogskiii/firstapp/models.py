from django.db import models

# Create your models here.
class MasterRelease(models.Model):
    artist = models.CharField(max_length=240) 
    master_id = models.CharField(max_length=15)
    title = models.CharField(max_length=240)
    uri = models.CharField(max_length=500)
    year = models.CharField(max_length=10)
    thumb = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.title} by {self.artist}"