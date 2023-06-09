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


def release_market(request, artist, release_id):

    # master represents meta information about the record
    # we get this from our internal db
    release = MainRelease.objects.get(master_id=release_id)
    master_release_id = release.master_id
    print("master_release_id", master_release_id)
    
    # main represents the original pressing
    # we have to obtain this from discogs
    # -- but maybe we could store it in our db
    # weighing the design decision of moving this up into the amarkets view
    # we could fetch this when we write to the db to store and access later.
    # it might slow down amarkets, but would speed up this release_market view.
    main_release_id = get_main_release_id(master_release_id)
    print("main_release_id", main_release_id)
    
    # listing_ids represent the original pressings available for sale
    # we have to obtain this by webscraping dicogs each and every
    # time because markets change
    listing_ids = get_listing_ids(main_release_id)
    
    # initialize list for all marketplace listings of the original pressing
    marketplace_listings = []

    for listing in listing_ids:
        marketplace_listings.append(get_marketplace_listing(listing))
    
    print(marketplace_listings)
    # sort by price
    sorted_listings = sorted(marketplace_listings, key=lambda d: d["price"]["value"], reverse=True)

    # should apply some formatting here
    # round dollar amounts
    # calculate minimum tick for order book display
    # format date (posted)
    # maybe clean up conditions to just be codes (ie VG instead of text Very Good)
    
    return render(request, "firstapp/release_market.html", {
        "artist": artist,
        "release": release,
        "marketplace_listings": sorted_listings
    })