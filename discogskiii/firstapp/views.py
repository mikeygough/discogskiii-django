# imports
from django.shortcuts import render
from firstapp.config import *
from firstapp.utils import *


artist_markets = [
    "Sun Ra",
    "John Coltrane",
    "Miles Davis",
    "Alice Coltrane"
]

# Create your views here.
def index(request):
    return render(request, "firstapp/index.html", {
        "artist_markets": artist_markets
    })

def amarkets(request, artist):

    # get random master id
    master_id = get_master_id(artist)
    print(master_id)
    print("-------------------------------")
    # get the main release id (original pressing id) from that random master
    print(f"get_main_release_id({master_id})")
    main_release_id = get_main_release_id(master_id)
    print(main_release_id)
    print("-------------------------------")
    # get the listing_ids (the original pressings available for sale) based on that random master
    print(f"get_listing_ids({main_release_id})")
    listing_ids = get_listing_ids(main_release_id)
    print(listing_ids)
    print("-------------------------------")
    print(f"get_marketplace_listing{listing_ids[0]}")
    marketplace_listing = get_marketplace_listing(listing_ids[0])
    print(marketplace_listing)

    return render(request, "firstapp/artist_markets.html", {
        "artist": artist
    })