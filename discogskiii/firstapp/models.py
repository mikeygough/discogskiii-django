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
    main_id = models.CharField(max_length=15)
    uri = models.CharField(max_length=500)
    community_have = models.IntegerField(default=0)
    community_want = models.IntegerField(default=0)
    community_demand_score = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    num_for_sale = models.IntegerField(null=True, default=0)
    lowest_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    title = models.CharField(max_length=240)
    released = models.DateField()
    thumb = models.CharField(max_length=500)
    # should this be a one-to-one relationship instead of the current foreignkey relationship?
    # django's documentation suggests that foreign keys be the related model name in lowercase, masterrelease
    master = models.ForeignKey(MasterRelease, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.main_id} is the original pressing of {self.title}"
    

class SavedMarkets(models.Model):
    ''' represents a users saved markets (MainRelease) '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    market = models.ForeignKey(MainRelease, on_delete=models.CASCADE)