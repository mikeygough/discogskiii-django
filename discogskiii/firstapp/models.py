from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class MasterRelease(models.Model):
    ''' represents the master pressing '''
    artist = models.CharField(max_length=240) 
    master_id = models.CharField(max_length=15)
    title = models.CharField(max_length=240)
    uri = models.CharField(max_length=500)
    # think about changing this to models.DateField() since we order by it
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
    

class SavedMarkets(models.Model):
    ''' represents a users saved markets (MainRelease) '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    market = models.ForeignKey(MainRelease, on_delete=models.CASCASE)