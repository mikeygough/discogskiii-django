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
    "Alice Coltrane"
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
    if artist not in artist_markets:
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

        # add records to database:
        for vinyl in sorted_vinyls:
            MainRelease(artist=vinyl["artist"],
                        master_id=vinyl["master_id"],
                        title=vinyl["title"],
                        uri=vinyl["uri"],
                        year=vinyl["year"],
                        thumb=vinyl["thumb"]).save()
        
        # remove duplicate values (is not working 100%)
        seen = set()
        new_l = []
        for d in sorted_vinyls:
            t = tuple(d.items())
            if t not in seen:
                seen.add(t)
                new_l.append(d)
    else:
        new_l = MainRelease.objects.all().filter(artist=artist)


    return render(request, "firstapp/artist_markets.html", {
        "artist": artist,
        "sorted_vinyls": new_l,
        "base_url": SITE_BASE_URL
    })