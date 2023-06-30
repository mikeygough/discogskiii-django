from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class MasterRelease(models.Model):
    ''' represents the master pressing '''
    # for all of these charfields, I should really be more thoughtful about max_length.
    # to more efficiently design my database I should consider reviewing all data and seeing what max lengths are then adjust
    # the fields accordingly.
    artist = models.CharField(max_length=240)
    master_id = models.CharField(max_length=15)
    title = models.CharField(max_length=240)
    # is there maybe a URL field?
    uri = models.CharField(max_length=500)
    # think about changing this to models.DateField() since we order by it
    year = models.CharField(max_length=10)
    # is there maybe a URL field?
    thumb = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.title} by {self.artist}"


class MainRelease(models.Model):
    ''' represents the main release (original pressing) '''
    main_id = models.CharField(max_length=15)
    # is there maybe a URL field?
    uri = models.CharField(max_length=500)
    community_have = models.IntegerField(default=0)
    community_want = models.IntegerField(default=0)
    community_demand_score = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    num_for_sale = models.IntegerField(null=True, default=0)
    # should price really be a charfield?
    lowest_price = models.CharField(max_length=15, null=True)
    title = models.CharField(max_length=240)
    # think about changing this to models.DateField() since we order by it
    released = models.CharField(max_length=10)
    # is there maybe a URL field?
    thumb = models.CharField(max_length=500)
    # should this be a one-to-one relationship instead of the current many-to-one relationship?
    master = models.ForeignKey(MasterRelease, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.main_id} is the original pressing of {self.title}"
    

class SavedMarkets(models.Model):
    ''' represents a users saved markets (MainRelease) '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    market = models.ForeignKey(MainRelease, on_delete=models.CASCADE)