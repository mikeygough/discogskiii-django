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
import json
import time
import math
import itertools
import dateparser

from django.core.serializers import serialize
from decimal import Decimal
from datetime import date


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
    
    # Identify and remove duplicate master_id values
    duplicate_master_ids = MasterRelease.objects.values('master_id').annotate(count=Count('master_id')).filter(count__gt=1)

    print("Removing Duplicate Master Ids", duplicate_master_ids)
    # Loop through the duplicate master_ids
    for duplicate in duplicate_master_ids:
        # Get all instances with the duplicate master_id
        duplicates = MasterRelease.objects.filter(master_id=duplicate['master_id'])

        # Check if duplicates exist
        if duplicates.exists():
            # Keep the first instance and delete the rest
            master_release_to_keep = duplicates.first()
            duplicates.exclude(id=master_release_to_keep.id).delete()
    
    print("Database Initialized, Enjoy!")

    # hm... is this causing the page to load twice? it does all the work, checks if logged in, then tries to redirect?
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

    if request.method == "POST":
        market_id = request.POST.get('market_id')
        # remove saved market from database
        SavedMarkets.objects.get(id=market_id).delete()
        return HttpResponseRedirect(reverse("firstapp:saved_markets"))
    else:
        return render(request, "firstapp/saved_markets.html", {
            "saved_markets": saved_markets
        })


# all releases by an arist
def artist_releases(request, artist):
    # cached, load from database
    artist_releases = MasterRelease.objects.filter(artist=artist).order_by("year")
    # get master_ids
    master_ids = list(artist_releases.values_list("master_id", flat=True))

    # check if all MasterRelease objects exist in MainRelease (results aren't cached)
    if artist_releases.exists() and artist_releases.all().count() != MainRelease.objects.filter(master__in=artist_releases).count():
        print("Some MasterRelease objects are missing in MainRelease")
        print("Fetching from Discogs API. Note that this could take several minutes...")
        
        # 1, get master_release and main_release ids by chunking async requests
        # Optimal Chunk Size = Total Number of Items / Maximum Requests per Minute
        chunk_size = math.ceil(len(master_ids) / 60)
        # initialize list
        master_main_release_ids = []
        # loop through in chunks
        print("Getting Master & Main Release IDs")
        for i in range(0, len(master_ids), chunk_size):
            chunk = master_ids[i:i+chunk_size]
            # get results from chunk
            results = asyncio.run(get_master_main_release_ids_async(master_ids=chunk))
            # append
            master_main_release_ids.append(results)
            print(f"{len(master_ids) - (len(master_main_release_ids)*chunk_size)} Master & Main Release IDs Remaining")
            # sleep to not trigger request limit
            print("Sleeping for 5 seconds")
            time.sleep(5)
        
        # format (flatten list of lists to just be list of dicts)
        master_main_release_ids = list(itertools.chain.from_iterable(master_main_release_ids))

        # grab just main_release_ids
        main_release_ids = [x["main_release"] for x in master_main_release_ids]

        # 2, get main_release data by chunking async requests
        # initialize list
        main_release_data = []
        # loop through in chunks (same chunk size as above)
        print("Getting Main Release Data")
        for i in range(0, len(master_main_release_ids), chunk_size):
            chunk = main_release_ids[i:i+chunk_size]
            # get results from chunk
            results = asyncio.run(get_main_release_data_async(release_ids=chunk))
            # append
            main_release_data.append(results)
            print(f"{len(master_main_release_ids) - (len(main_release_data)*chunk_size)} Main Release Datum Remaining")
            # sleep to not trigger request limit
            print("Sleeping for 5 seconds")
            time.sleep(5)

        # format format (flatten list of lists to just be list of dicts)
        main_release_data = list(itertools.chain.from_iterable(main_release_data))
        # match master ids and main release data by linking main_release id
        for release in main_release_data:
            release_id = release["id"]
            matching_ids = [item["id"] for item in master_main_release_ids if item["main_release"] == release_id]
            if matching_ids:
                release["master_id"] = matching_ids[0]

        # 3, add to cache
        for main_release in main_release_data:    
            if MasterRelease.objects.filter(master_id=main_release["master_id"]).exists():
                print(f"Caching {main_release['title']}")
                mr = MasterRelease.objects.get(master_id=main_release["master_id"])
                # calculate demand score
                try:
                    main_release['community_demand_score'] = round(main_release['community_want'] / main_release['community_have'], 2)
                except:
                    main_release['community_demand_score'] = None
                try:
                    main_release['released'] = dateparser.parse(main_release['released'][:4])
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
                print(f"Unable to Cache {main_release}")
        
        print("Done Fetching & Caching Main Release Data!")
        print("Database Initialized, Enjoy!")
    else:
        print("Main Release Data Already Cached!, Enjoy!")

    # get main_release_data from database
    main_release_data = MainRelease.objects.filter(master__in=artist_releases)

    # I think that I need to run some checks here...
        # Right now it's possible that release markets change (for example, a new listing is added
        # at a new lower price) and my table won't properly reflect this since the cache check passes
        # and my app will just load everything from the Database.
        # I guess what I can do is check is the num_for_sale count differs.
        # Really I'd love to know if the page was updated (record sold, added, or price changed)
        # But I don't think this data is currently available via any Discogs API response.
    
    # check for stale data by comparing values
    # count = 0
    # update_count = 0
    # for release in main_release_data:
    #     if count % 5 == 0 and count != 0:
    #         print("sleeping for 5")
    #         time.sleep(5)
    #     print(f"Checking for stale data {release.title}")
    #     new_data = get_main_release_data(release.main_id)

    #     print(f"DB Num for Sale {release.num_for_sale}")
    #     print(f"DB Num for Sale Type {type(release.num_for_sale)}")
    #     print(f"DB Lowest Price {release.lowest_price}")
    #     print(f"DB Lowest Price Type {type(release.lowest_price)}")

    #     print(f"Response Num for Sale {new_data['num_for_sale']}")
    #     print(f"Response Num for Sale Type {type(new_data['num_for_sale'])}")
    #     print(f"Response Lowest Price {new_data['lowest_price']}")
    #     print(f"Response Lowest Price Tyepe {type(new_data['lowest_price'])}")

    #     # check for Nonetypes, do type conversion if not
    #     if (new_data["num_for_sale"] is None or release.num_for_sale is None or
    #         float(new_data["num_for_sale"]) == float(release.num_for_sale)) and \
    #         (new_data["lowest_price"] is None or release.lowest_price is None or
    #         float(new_data["lowest_price"]) == float(release.lowest_price)):
    #         print("Data not stale!")
    #     else:
    #         print("Data is stale, should be updated")
    #         print(f"Updating {release.title}")
    #         record = MainRelease.objects.get(main_id=release.main_id)
    #         record.num_for_sale=new_data["num_for_sale"]
    #         record.lowest_price=new_data["lowest_price"]
    #         record.save()
    #         update_count += 1
    #     count += 1

    # print(f"Updated {update_count} records")
    # get sort parameter
    sort_by = request.GET.get('sort_by')
    sort_direction = request.GET.get('sort_direction', 'asc')

    if sort_by:
        # get main_release_data from database
        if sort_direction == 'asc':
            main_release_data = main_release_data.order_by(sort_by)
        elif sort_direction == 'desc':
            main_release_data = main_release_data.order_by(f'-{sort_by}')

    return render(request, "firstapp/artist_releases.html", {
        "artist": artist,
        "main_release_data": main_release_data,
        "current_sort_by": sort_by,
        "current_sort_direction": sort_direction
    })


# view original pressings of release available for sale
def release_market(request, artist, release_id):
    # get main_release_id (original pressing)
    main_release = MainRelease.objects.get(main_id=release_id)
    main_release_id = main_release.main_id
    # get master_release
    master_release = main_release.master
    master_release_id = master_release.master_id
    # store original pressings market site
    market_site = f"{SITE_BASE_URL}/sell/release/{release_id}"

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
        
        return HttpResponseRedirect(reverse("firstapp:release_market", args=(artist, release_id,)))
    else:
        # get listing ids
        # marketplace_listing_ids represent the original pressings available for sale
        # we obtain this by webscraping discogs each time because markets change
        marketplace_listing_ids = get_listing_ids(release_id)
        
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
        
        return render(request, "firstapp/release_market.html", {
            "artist": artist,
            "master_release": master_release,
            "master_release_id": master_release_id,
            "main_release": main_release,
            "main_release_id": main_release_id,
            "marketplace_listings": marketplace_listings,
            "saved": saved,
            "market_site": market_site
        })

# Custom serializer for Decimal and date types
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)  # Convert Decimal to string
        elif isinstance(obj, date):
            return obj.isoformat()  # Convert date to ISO format
        return super().default(obj)


# artist release statistics - IN DEVELOPMENT
def artist_release_statistics(request, artist):
    # cached, load from database
    artist_releases = MasterRelease.objects.filter(artist=artist)
    main_release_data = list(MainRelease.objects.filter(master__in=artist_releases).values("released", "lowest_price", "title"))

    print("Main Release Data Already Cached!, Enjoy!")

    json_data = json.dumps(main_release_data, cls=CustomJSONEncoder)

    print(json_data)
    
    return render(request, "firstapp/artist_release_statistics.html", {
        "artist": artist,
        "main_release_data": main_release_data,
        "json_data": json_data
    })
