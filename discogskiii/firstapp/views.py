# imports
from django.shortcuts import render
from firstapp.config import *
from firstapp.utils import *

# statically declare supported markets
artist_markets = [
    "Sun Ra",
    "John Coltrane",
    "Miles Davis",
    "Alice Coltrane"
]

# index
def index(request):
    return render(request, "firstapp/index.html", {
        "artist_markets": artist_markets
    })


# artist markets
def amarkets(request, artist):

    # first get number of pages:
    num_pages = json.loads(requests.get(f"{API_BASE_URL}/database/search",
                                        headers=AUTHENTICATION_HEADER,
                                        params = {
                                            "artist": f"{artist}",
                                            "type": "master",
                                            "format": "vinyl"
                                            }).text)["pagination"]["pages"]
    # initialize empty list for vinyls
    vinyls = []

    # iterate through number of pages, get data, add to list of vinyls
    for page in range(1, num_pages + 1):
        # get data
        response = requests.get(f"{API_BASE_URL}/database/search",
                         headers=AUTHENTICATION_HEADER,
                         params = {
                            "artist": f"{artist}",
                            "type": "master",
                            "format": "vinyl",
                            "page": f"{page}"
                         }).text

        # turn string into json
        response_json = json.loads(response)

        # get album title, uri, year, and thumbnail
        for result in response_json["results"]:
            try:
                info = {
                "artist": f"{artist}",
                "master_id": result["master_id"],
                "title": result["title"],
                "uri": result["uri"],
                "year": result["year"],
                "thumb": result["thumb"],
                }
                vinyls.append(info)
            except:
                pass

    # sort by year
    sorted_vinyls = sorted(vinyls, key=lambda d: d["year"])
    
    print(sorted_vinyls)
    print(type(sorted_vinyls))
    
    # remove duplicate values (is not working 100%)
    seen = set()
    new_l = []
    for d in sorted_vinyls:
        t = tuple(d.items())
        if t not in seen:
            seen.add(t)
            new_l.append(d)

    # get random master id
    # master_id = get_master_id(artist)
    # print(master_id)
    # print("-------------------------------")
    # # get the main release id (original pressing id) from that random master
    # print(f"get_main_release_id({master_id})")
    # main_release_id = get_main_release_id(master_id)
    # print(main_release_id)
    # print("-------------------------------")
    # # get the listing_ids (the original pressings available for sale) based on that random master
    # print(f"get_listing_ids({main_release_id})")
    # listing_ids = get_listing_ids(main_release_id)
    # print(listing_ids)
    # print("-------------------------------")
    # print(f"get_marketplace_listing{listing_ids[0]}")
    # marketplace_listing = get_marketplace_listing(listing_ids[0])
    # print(marketplace_listing)

    return render(request, "firstapp/artist_markets.html", {
        "artist": artist,
        "sorted_vinyls": new_l,
        "base_url": SITE_BASE_URL
    })