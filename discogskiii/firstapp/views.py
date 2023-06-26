# imports
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.urls import reverse
from firstapp.config import *
from firstapp.utils import *
import time
import math
import itertools

# import models
from firstapp.models import User, MasterRelease, MainRelease, SavedMarkets

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
        cached_artists = list(MasterRelease.objects.values_list("artist", flat=True).distinct())
    except: # database not initialized
        cached_artists = []

    # if not cached
    if not all(elem in cached_artists for elem in artist_markets):
        # initialize database, get all artist markets
        for artist in artist_markets:
        # request data from discogs
            print(f"Getting Artist {artist}")
            artist_releases = get_artist_releases(artist)
            for release in artist_releases:
                print(artist, release["title"])
                # add MasterRelease
                MasterRelease.objects.create(artist=release["artist"],
                                             master_id=release["master_id"],
                                             title=release["title"],
                                             uri=release["uri"],
                                             year=release["year"],
                                             thumb=release["thumb"])
            
            print("sleeping for 5")
            time.sleep(5)
     
        print("Done Fetching Artist Releases!")
    
    print("Database Initialized, Enjoy!")

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("firstapp:login"))

    return render(request, "firstapp/index.html", {
        "artist_markets": artist_markets
    })


def login_view(request):
    if request.method == "POST":

        # attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("firstapp:index"))
        else:
            return render(request, "firstapp/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "firstapp/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("firstapp:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # ensure password matched confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "firstapp/register.html", {
                "message": "Passwords must match."
            })

        # attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "firstapp/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("firstapp:index"))
    else:
        return render(request, "firstapp/register.html")
    

# displays info on all markets saved by user
def saved_markets(request):

    # get saved markets
    saved_markets = SavedMarkets.objects.filter(user=request.user)
    print("saved_markets", saved_markets)
    # get main releases
    main_releases_reference = list(saved_markets.values_list("market", flat=True))
    print("main_releases_reference", main_releases_reference)
    master_release_ids = list(MainRelease.objects.filter(pk__in=main_releases_reference).values_list("master", flat=True))
    print(master_release_ids)
    artist_releases = MasterRelease.objects.filter(pk__in=master_release_ids)
    print(artist_releases)

    return render(request, "firstapp/saved_markets.html", {
        "saved_markets": saved_markets,
        "artist_releases": artist_releases
    })


# all releases by an arist
def artist_releases(request, artist):
    # cached, load from database
    artist_releases = MasterRelease.objects.filter(artist=artist).order_by("year")
    # pagination
    # instantiate Paginator, 10 records
    paginator = Paginator(artist_releases, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    # get page objects as list
    page_obj_list = page_obj.object_list
    
    # get master ids
    master_ids = list(page_obj_list.values_list("master_id", flat=True))
    
    # get master and main_release ids
    master_main_release_ids = asyncio.run(get_master_main_release_ids_async(master_ids=master_ids))
    # each tuple represents an original pressing.
    # the first item is the master_id, the second item is the main_id (original pressing id)

    for id in master_main_release_ids:
        if not MainRelease.objects.filter(main_id=id[1]).exists():
            print(f"Does Not Exist! Caching {id[1]}!")
            mr = MasterRelease.objects.get(master_id=id[0])
            print(mr)
            # add to cache
            print("Does not exist!")
            MainRelease.objects.create(master=mr, main_id=id[1])
        else:
            print("Exists!")

    main_release_ids = [x[1] for x in master_main_release_ids]
    # get release_statistics
    release_stats = asyncio.run(get_release_statistics_async(release_ids=main_release_ids))

    # print("master_ids", master_ids)
    # print("release_ids", main_release_ids)
    # print("release_stats", release_stats)

    # zip artist_releases data and release_stats for django templating support
    zipped_data = zip(page_obj_list, release_stats)

    return render(request, "firstapp/artist_releases.html", {
        "artist": artist,
        "artist_releases": artist_releases,
        "base_url": SITE_BASE_URL,
        "page_obj": page_obj,
        "paginator": paginator,
        "zipped_data": zipped_data
    })


# artist release statistics
def artist_release_statistics(request, artist):
    # get artist releases (From DB)
    # SHORTER LIST FOR TESTING (10)
    # artist_releases = MasterRelease.objects.filter(artist=artist).order_by("year")[:10]
    artist_releases = MasterRelease.objects.filter(artist=artist).order_by("year")
    # get master_ids (From DB)
    master_ids = list(artist_releases.values_list("master_id", flat=True))

    # get master_release and main_release ids
    # calculate optimal chunk size given list length and api limits...
        # Optimal Chunk Size = Total Number of Items / Maximum Requests per Minute
    # set chunk size
    chunk_size = math.ceil(len(master_ids) / 60)
    # initialize list
    master_main_release_ids = []
    # loop through in chunks
    for i in range(0, len(master_ids), chunk_size):
        chunk = master_ids[i:i+chunk_size]
        # get results from chunk
        results = asyncio.run(get_master_main_release_ids_async(master_ids=chunk))
        # append
        master_main_release_ids.append(results)
        
        # DISABLE SLEEP FOR TESTING
        print(f"{len(master_ids) - (len(master_main_release_ids)*chunk_size)} Remaining")
        print("Sleeping for 2.5 seconds")
        time.sleep(2.5)
    
    # master_main_release_ids is a list of tuples, each tuple represents an original pressing
    # Before Itertools [[(84360, 517197)], [(283549, 3922959)],...]
    master_main_release_ids = list(itertools.chain.from_iterable(master_main_release_ids))
    # After Itertools [(84360, 517197), (283549, 3922959),...]
    # the first item in the tuple is the master_id
    # the second item in the tuple is the main_id

    # !!! SHOULD DO SOME SORT OF CACHING HERE? OR JUST MOVE THE CACHING OF MAIN_RELEASE_ID ENTIRELY
    # !!! OUT OF THE ARTIST_RELEASE_STATISTICS AND ARTIST_RELEASE VIEWS... TBD
    
    # grab main_release_ids
    main_release_ids = [x[1] for x in master_main_release_ids]

    # get 'have' and 'want' main_release statistics
    # calculate optimal chunk size given list length and api limits...
        # Optimal Chunk Size = Total Number of Items / Maximum Requests per Minute
    # set chunk size
    chunk_size = math.ceil(len(main_release_ids) / 60)
    # initialize list
    wantlist_release_statistics = []
    # loop through in chunks
    for i in range(0, len(main_release_ids), chunk_size):
        chunk = main_release_ids[i:i+chunk_size]
        # get results from chunk
        results = asyncio.run(get_wantlist_release_statistics_async(release_ids=chunk))
        # append
        wantlist_release_statistics.append(results)

        # DISABLE SLEEP FOR TESTING
        print(f"{len(main_release_ids) - (len(wantlist_release_statistics)*chunk_size)} Remaining")
        print("Sleeping for 2.5 seconds")
        time.sleep(2.5)
        
    # wantlist_release_statistics is a list of tuples, each tuple represents an original pressing's wantlist statistics
    # Before Itertools [[(123, 1257)], [(48, 1289)],...]
    wantlist_release_statistics = list(itertools.chain.from_iterable(wantlist_release_statistics))
    # After Itertools [(123, 1257), (48, 1289),...]
    # the first item in the tuple is the community 'have'
    # the second item in the tuple is the community 'want'

    print("master_main_release_ids", master_main_release_ids)
    print("main_release_ids", main_release_ids)
    print("wantlist_release_statistics", wantlist_release_statistics)

    # zip artist_releases data and release_stats for django templating support
    zipped_data = zip(artist_releases, wantlist_release_statistics)

    return render(request, "firstapp/artist_release_statistics.html", {
        "artist": artist,
        "zipped_data": zipped_data
    })


# view original pressings of release available for sale
def release_market(request, artist, release_id):

    # master represents the album as an entity. fetch from db
    master_release = MasterRelease.objects.get(master_id=release_id)
    master_release_id = master_release.master_id
    
    # get main_release_id (original pressing)
    # if cached, load from db
    # this is a redundant cache check, should have already been cached on the artist_releases page load
    if MainRelease.objects.filter(master=master_release).exists():
        print(f"Exists!")
        main_release = MainRelease.objects.get(master=master_release)
        main_release_id = main_release.main_id
    else:
        # request data from discogs
        print(f"Does Not Exist! Caching {master_release}")
        main_release_id = get_main_release_id(master_release_id)
        # add to cache
        main_release = MainRelease(master=master_release, main_id=main_release_id)
        main_release.save()
    
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
    
    saved = SavedMarkets.objects.filter(user=request.user,
                                        market=main_release).exists()

    if request.method == "POST":
        saved_response = request.POST["savebtn"]
        if saved_response == "Unsave Market":
            # remove saved market from database
            SavedMarkets.objects.get(user=request.user,
                                     market=main_release).delete()
            saved = False
        elif saved_response == "Save Market":
            # add saved market to database
            SavedMarkets.objects.create(user=request.user,
                                        market=main_release)
            saved = True
        
        return render(request, "firstapp/release_market.html", {
        "artist": artist,
        "master_release": master_release,
        "master_release_id": master_release_id,
        "main_release_id": main_release_id,
        "marketplace_listings": marketplace_listings,
        "saved": saved
        })
    else:
        return render(request, "firstapp/release_market.html", {
            "artist": artist,
            "master_release": master_release,
            "master_release_id": master_release_id,
            "main_release_id": main_release_id,
            "marketplace_listings": marketplace_listings,
            "saved": saved
        })


