from django.db import models

# Create your models here.
class MainRelease(models.Model):
    master_id = models.CharField()
    title = models.CharField()
    uri = models.CharField()
    year = models.CharField()
    thumb = models.CharField()