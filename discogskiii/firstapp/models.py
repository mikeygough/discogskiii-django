from django.db import models

# Create your models here.

class MasterRelease(models.Model):
    ''' represents the master pressing '''
    artist = models.CharField(max_length=240) 
    master_id = models.CharField(max_length=15)
    title = models.CharField(max_length=240)
    uri = models.CharField(max_length=500)
    year = models.CharField(max_length=10)
    thumb = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.title} by {self.artist}"


class MainRelease(models.Model):
    ''' represents the main release (original pressing) '''
    master = models.ForeignKey(MasterRelease, on_delete=models.CASCADE)
    main_id = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.main_id} is the original pressing of..."