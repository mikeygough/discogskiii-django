# imports
from django.shortcuts import render
from firstapp.config import *
from firstapp.utils import *

# import models
from firstapp.models import MainRelease

# statically declare supported markets
artist_markets = [
    "Sun Ra",
    "John Coltrane",
    "Miles Davis",
    "Alice Coltrane",
    "Lee Morgan",
    "Coleman Hawkins"
]

# index
def index(request):
    return render(request, "firstapp/index.html", {
        "artist_markets": artist_markets
    })


# artist markets
def amarkets(request, artist):

    # get unique artists in database (cached)
    cached_artists = MainRelease.objects.all().values_list('artist', flat=True).distinct()

    # if not cached
    if artist not in cached_artists:
        # request data from discogs
        new_l = get_artist_markets(artist)
    else:
        # cached, just load from database
        new_l = MainRelease.objects.all().filter(artist=artist)


    return render(request, "firstapp/artist_markets.html", {
        "artist": artist,
        "sorted_vinyls": new_l,
        "base_url": SITE_BASE_URL
    })