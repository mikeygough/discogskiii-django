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
    "Lee Morgan"
]

loaded_markets = [
    "Sun Ra",
    "John Coltrane",
    "Miles Davis",
    "Alice Coltrane",
    "Lee Morgan"
]

# index
def index(request):
    return render(request, "firstapp/index.html", {
        "artist_markets": artist_markets
    })


# artist markets
def amarkets(request, artist):

    # at this point i've stored all the Main Release items for the four artists in the artist_markets list inside the database
    # so if there's a new artist, we need to make the discogs api calls
    # else we'll just request from our own database
    if artist not in loaded_markets:        
        new_l = get_artist_markets(artist)
    else:
        new_l = MainRelease.objects.all().filter(artist=artist)


    return render(request, "firstapp/artist_markets.html", {
        "artist": artist,
        "sorted_vinyls": new_l,
        "base_url": SITE_BASE_URL
    })