# imports
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Count
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
    # Identify duplicate master_id values
    duplicate_master_ids = MasterRelease.objects.values('master_id').annotate(count=Count('master_id')).filter(count__gt=1)

    # Loop through the duplicate master_ids
    for duplicate in duplicate_master_ids:
        # Get all instances with the duplicate master_id
        duplicates = MasterRelease.objects.filter(master_id=duplicate['master_id'])

        # Check if duplicates exist
        if duplicates.exists():
            # Keep the first instance and delete the rest
            master_release_to_keep = duplicates.first()
            duplicates.exclude(id=master_release_to_keep.id).delete()

    # cached, load from database
    artist_releases = MasterRelease.objects.filter(artist=artist).order_by("year")
    # get master_ids (From DB)
    master_ids = list(artist_releases.values_list("master_id", flat=True))

    # check if all MasterRelease objects exist in MainRelease
    if artist_releases.exists() and artist_releases.all().count() != MainRelease.objects.filter(master__in=artist_releases).count():
        print("Some MasterRelease objects are missing in MainRelease")
        print("Fetching from Discogs API. Note that this could take several minutes...")
        
        # 1, get master_release and main_release ids
            # calculate optimal chunk size given list length and api limits...
            # Optimal Chunk Size = Total Number of Items / Maximum Requests per Minute
            # set chunk size
        chunk_size = math.ceil(len(master_ids) / 60)
        # initialize list
        master_main_release_ids = []
        # loop through in chunks
        print("Getting Main Release IDs")
        for i in range(0, len(master_ids), chunk_size):
            chunk = master_ids[i:i+chunk_size]
            # get results from chunk
            results = asyncio.run(get_master_main_release_ids_async(master_ids=chunk))
            # append
            master_main_release_ids.append(results)
            print(f"{len(master_ids) - (len(master_main_release_ids)*chunk_size)} Remaining")
            print("Sleeping for 3 seconds")
            time.sleep(3)
        
        # format
        # the first item in the tuple is the master_id, the second item in the tuple is the main_id
        master_main_release_ids = list(itertools.chain.from_iterable(master_main_release_ids))

        # grab just main_release_ids
        main_release_ids = [x[1] for x in master_main_release_ids]

        # 2, get main release data
            # set chunk size
        chunk_size = math.ceil(len(main_release_ids) / 60)
        # initialize list
        main_release_data = []
        # loop through in chunks
        print("Getting Main Release Data")
        for i in range(0, len(main_release_ids), chunk_size):
            chunk = main_release_ids[i:i+chunk_size]
            # get results from chunk
            results = asyncio.run(get_main_release_data_async(release_ids=chunk))
            # append
            main_release_data.append(results)
            print(f"{len(main_release_ids) - (len(main_release_data)*chunk_size)} Remaining")
            print("Sleeping for 3 seconds")
            time.sleep(3)

        # ! I think I know how to stop getting errors here. Let me be clear about the problem I'm facing...
        # Step 1, I am running a search by artist and saving MasterReleases.
        # Step 2 I am looping through each MasterRelease hitting the masterrelease discogs API and getting the main release ID.
        # Step 3 I am hitting the Release endpoint to get data on that main release, and also storing the master_release_id from that request
        # The issue is that the master_release_id i'm saving in step 1 and 2 is not always the same with the master_release ID
        # I'm getting from the release endpoint in step 3.
        # What if instead of resaving the master_release in step 3, I just plug in the master_id from Step 1/2 when I save the MainRelease object in step 3?
        # This would create a more stable relationship between MasterRelease and MainRelease database records.
        
        # format
        # dictionary object with key, value pairs containing data on the main release object
        main_release_data = list(itertools.chain.from_iterable(main_release_data))

        # 3, write data to database
        for main_release in main_release_data:
            # check if exists. if doesn't pass
            # at this point I know of at least one record that gives me issues between my get_artist_release function
            # and my get_main_release_data_async function
            # discogs api returns different data for
            # https://www.discogs.com/master/606598-Alice-Coltrane-Turiyasangitananda-Divine-Songs
            # and
            # https://www.discogs.com/master/622821-Alice-Coltrane-Turiyasangitananda-Divine-Songs
            
            if MasterRelease.objects.filter(master_id=main_release["master_id"]).exists():
                print(f"Caching {main_release['title']}")
                print("Main_release", main_release)
                mr = MasterRelease.objects.get(master_id=main_release["master_id"])
                # add MainRelease
                
                # calculate demand score
                try:
                    main_release['community_demand_score'] = round(main_release['community_want'] / main_release['community_have'], 2)
                except:
                    main_release['community_demand_score'] = None
                # format currency
                try:
                    main_release['lowest_price'] = format_currency(main_release['lowest_price'])
                except:
                    pass
                # create
                MainRelease.objects.create(main_id=main_release["id"],
                                            uri=main_release["uri"],
                                            community_have=main_release["community_have"],
                                            community_want=main_release["community_want"],
                                            community_demand_score=main_release["community_demand_score"],
                                            num_for_sale=main_release["num_for_sale"],
                                            lowest_price=main_release["lowest_price"],
                                            title=main_release["title"],
                                            released=main_release["released"],
                                            thumb=main_release["thumb"],
                                            master=mr)
            else:
                pass
        
        print("Done Fetching & Caching Main Release Data!")
        print("Database Initialized, Enjoy!")
    else:
        print("Main Release Data Already Cached!, Enjoy!")

    # get main_release_data from database
    main_release_data = MainRelease.objects.filter(master__in=artist_releases)
    
    # pagination
    # instantiate Paginator, 10 records
    paginator = Paginator(main_release_data, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "firstapp/artist_releases.html", {
        "artist": artist,
        "artist_releases": artist_releases,
        "base_url": SITE_BASE_URL,
        "page_obj": page_obj,
        "paginator": paginator
    })


# artist release statistics
def artist_release_statistics(request, artist):
    # cached, load from database
    artist_releases = MasterRelease.objects.filter(artist=artist).order_by("year")
    
    print("Main Release Data Already Cached!, Enjoy!")
    
    # get main_release_data from database
    main_release_data = MainRelease.objects.filter(master__in=artist_releases)

    return render(request, "firstapp/artist_release_statistics.html", {
        "artist": artist,
        "main_release_data": main_release_data
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


