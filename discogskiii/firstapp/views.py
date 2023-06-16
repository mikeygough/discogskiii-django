# imports
from django.shortcuts import render
from django.core.paginator import Paginator
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
    "Coleman Hawkins",
    "Art Blakey"
]

# index
def index(request):

    # right now this is checking all or none...
    # there's no reason to redownload everything if one artist is missing
    # get unique artists in database (cached)
    try:
        cached_artists = list(MasterRelease.objects.all().values_list('artist', flat=True).distinct())
    except: # database not initialized
        cached_artists = []

    # if not cached
    if not all(elem in cached_artists for elem in artist_markets):
        # initialize database, get all artist markets
        for artist in artist_markets:
        # request data from discogs
            artist_releases = get_artist_releases(artist)
            # add to cache
            for release in artist_releases:
                MasterRelease.objects.create(artist=release["artist"],
                                            master_id=release["master_id"],
                                            title=release["title"],
                                            uri=release["uri"],
                                            year=release["year"],
                                            thumb=release["thumb"])

     
    return render(request, "firstapp/index.html", {
        "artist_markets": artist_markets
    })


# all releases by an arist
def artist_releases(request, artist):
    # cached, load from database
    artist_releases = MasterRelease.objects.all().filter(artist=artist).order_by("year")

    # pagination
    # instantiate Paginator, 10 records
    paginator = Paginator(artist_releases, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    page_obj_list = page_obj.object_list
    print(page_obj_list)
    # get master ids
    master_ids = list(page_obj_list.values_list('master_id', flat=True))
    print("master_ids", master_ids)
    # get release ids
    release_ids = asyncio.run(get_main_release_ids_async(master_ids=master_ids))
    # get release_statistics
    release_stats = asyncio.run(get_release_statistics_async(release_ids=release_ids))

    print("master_ids", master_ids)
    print("release_ids", release_ids)
    print("release_stats", release_stats)

    # zip artist_releases data and release_stats for django templating support
    zipped_data = zip(page_obj_list, release_stats)

    print(zipped_data)

    return render(request, "firstapp/artist_releases.html", {
        "artist": artist,
        "artist_releases": artist_releases,
        "base_url": SITE_BASE_URL,
        "page_obj": page_obj,
        "paginator": paginator,
        "zipped_data": zipped_data
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
        MainRelease.objects.create(master=master_release, main_id=main_release_id)
    
    # marketplace_listing_ids represent the original pressings available for sale
    # we obtain this by webscraping discogs each time because markets change
    marketplace_listing_ids = get_listing_ids(main_release_id)
    
    marketplace_listings = asyncio.run(get_marketplace_listings_async(marketplace_listing_ids=marketplace_listing_ids))
    
    # sort by price
    try:
        marketplace_listings = sorted(marketplace_listings, key=lambda d: d["price"]["value"], reverse=True)
    except:
        pass

    # clean up
    for listing in marketplace_listings:
        # currency
        try:
            listing["price"]["value"] = format_currency(listing["price"]["value"])
        except KeyError:
            pass
        # date
        try:
            listing["posted"] = format_date(listing["posted"])
        except KeyError:
            pass
    
    # calculate minimum tick for order book display
    # maybe clean up conditions to just be codes (ie VG instead of text Very Good)
    
    return render(request, "firstapp/release_market.html", {
        "artist": artist,
        "master_release": master_release,
        "marketplace_listings": marketplace_listings
    })