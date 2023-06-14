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
        
        # **** ----- I REALLY DON'T LIKE THAT PAGINATION SUPPORT IS CONTINGENT ON ACTIVE CACHING ----- **** #

        # pagination
        # instantiate Paginator, 10 records
        paginator = Paginator(artist_releases, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # get release statistics (num_for_sale, lowest_price)
        # **** ----- I REALLY DON'T LIKE THAT THIS RELIES ON HAVING THE MAIN_RELEASE_ID RELATIONSHIP MAPPED TO THE MASTER_RELEASE_ID CACHED----- **** #
        release_stats = []
        for release in page_obj.object_list:
            try:
                # if cached, load from db
                if MainRelease.objects.filter(master=release).exists():
                    main_release_id = MainRelease.objects.get(master=release).main_id
                    release_stats.append(get_release_statistics(main_release_id))
                    print(main_release_id)
                else:
                    # request data from discogs
                    main_release_id = get_main_release_id(release.master_id)
                    # add to cache
                    MainRelease(master=release, main_id=main_release_id).save()
                    release_stats.append(get_release_statistics(main_release_id))
                    print(main_release_id)
            except:
                release_stats.append(0)

        # zip artist_releases data and release_stats for django templating support
        zipped_data = zip(page_obj, release_stats)

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

    # clean up
    for listing in sorted_listings:
        # currency
        listing["price"]["value"] = format_currency(listing["price"]["value"])
        # date
        listing["posted"] = format_date(listing["posted"])

    print(listing_ids)
    
    # calculate minimum tick for order book display
    # maybe clean up conditions to just be codes (ie VG instead of text Very Good)
    
    return render(request, "firstapp/release_market.html", {
        "artist": artist,
        "master_release": master_release,
        "marketplace_listings": sorted_listings
    })