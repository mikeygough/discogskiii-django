# imports
from django.shortcuts import render
from firstapp.config import *
from firstapp.utils import *

# import models
from firstapp.models import MasterRelease, MainRelease

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


# all releases by an arist
def artist_releases(request, artist):

    # get unique artists in database (cached)
    cached_artists = MasterRelease.objects.all().values_list('artist', flat=True).distinct()

    # if not cached
    if artist not in cached_artists:
        # request data from discogs
        artist_releases = get_artist_releases(artist)
        # add to cache
        for release in artist_releases:
            MasterRelease(artist=release["artist"],
                          master_id=release["master_id"],
                          title=release["title"],
                          uri=release["uri"],
                          year=release["year"],
                          thumb=release["thumb"]).save()
    else:
        # cached, load from database
        artist_releases = MasterRelease.objects.all().filter(artist=artist)

    return render(request, "firstapp/artist_releases.html", {
        "artist": artist,
        "artist_releases": artist_releases,
        "base_url": SITE_BASE_URL
    })


def release_market(request, artist, release_id):

    # master represents the album as an entity. fetch from db
    master_release = MasterRelease.objects.get(master_id=release_id)
    master_release_id = master_release.master_id
    
    # get main_release_id (original pressing)
    # if cached, load from db
    if MainRelease.objects.filter(master=master_release).exists():
        main_release_id = MainRelease.objects.get(master=master_release).main_id
    else:
        # request data from discogs
        main_release_id = get_main_release_id(master_release_id)
        # add to cache
        MainRelease(master=master_release, main_id=main_release_id).save()
    
    # listing_ids represent the original pressings available for sale
    # we obtain this by webscraping discogs each time because markets change
    listing_ids = get_listing_ids(main_release_id)
    
    # initialize list for all marketplace listings of the original pressing
    marketplace_listings = []

    for listing in listing_ids:
        marketplace_listings.append(get_marketplace_listing(listing))
    
    # sort by price
    sorted_listings = sorted(marketplace_listings, key=lambda d: d["price"]["value"], reverse=True)

    # should apply some formatting here
    # round dollar amounts
    # calculate minimum tick for order book display
    # format date (posted)
    # maybe clean up conditions to just be codes (ie VG instead of text Very Good)
    
    return render(request, "firstapp/release_market.html", {
        "artist": artist,
        "master_release": master_release,
        "marketplace_listings": sorted_listings
    })