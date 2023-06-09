# helper functions
from firstapp.config import *
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json
import re
import requests

# import models
from firstapp.models import MainRelease


def search_artist_database(artist, page=1, per_page=100):
    ''' REQUIRES AUTHENTICATION
        returns json response from page n of a discogs database artist search
        where type=master and format=vinyl.
        helpful for obtaining a release's master_id (record meta object). '''

    # get data, return as json
    response_json = json.loads(requests.get(f"{API_BASE_URL}/database/search",
                            headers=AUTHENTICATION_HEADER,
                            params={
                                "artist": f"{artist}",
                                "type": "master",
                                "format": "vinyl",
                                "page": f"{page}",
                                "per_page": f"{per_page}"}).text)
    
    # return data
    return response_json


def get_main_release_id(master_id):
    ''' REQUIRES AUTHENTICATION
        given a master_id (record meta object), retun the release_id
        of the original pressing. you can think of 'main_release' as the same
        as 'original_pressing'. '''
    
    # get data as json
    response_json = json.loads(requests.get(f"{API_BASE_URL}/masters/{master_id}",
                            headers=AUTHENTICATION_HEADER).text)
    
    # get release_id of master release
    main_release_id = response_json["main_release"]
    
    # return main_release_id (original_pressing_id)
    return main_release_id


def get_listing_ids(release_id):
    ''' given a release_id, returns a list of listings of that release_id for sale.
        listings are records which are available for sale.
        helpful for obtaining original pressings which are listed for sale. '''

    # **** ----- would like to improve performance here ----- **** #
    
    # create UserAgent
    ua = UserAgent()
    
    # get data
    response = requests.get(f"{SITE_BASE_URL}/sell/release/{release_id}",
                            headers={"User-Agent": ua.chrome})

    # extract html
    soup = BeautifulSoup(response.content, "html.parser")
    
    # extract links
    links = []
    for link in soup.find_all('a'):
        links.append(link.get('href'))
    # filter for listing_ids
    filter = "/sell/item/"
    
    # initialize list for listing_ids (original pressings of this release for sale)
    listing_ids = []
    # extract listing_ids
    for link in links:
        # '?' removes additional query parameters (currency)
        if filter in str(link) and '?' not in str(link):
            # regex the id
            listing_ids.append(re.findall(r'-?\d+\.?\d*', str(link)))
    # flatten the list
    listing_ids = [item for sublist in listing_ids for item in sublist]
    
    # return list of listing_ids
    return listing_ids


def get_marketplace_listing(listing_id):
    ''' REQUIRES AUTHENTICATION
        given a listing_id, returns marketplace listing json '''
    
    # get data as json
    response_json = json.loads(requests.get(f"{API_BASE_URL}/marketplace/listings/{listing_id}",
                    headers=AUTHENTICATION_HEADER).text)

    # return marketplace listing data
    return response_json


def get_artist_markets(artist):
    ''' REQUIRES AUTHENTICATION
        return list of dictionary objects representing all an artists' master releases '''
    
    # get number of pages for looping
    num_pages = search_artist_database(artist, page=1, per_page=100)["pagination"]["pages"]
    
    # initialize empty list for vinyls
    vinyls = []

    # iterate through number of pages, get data, add to list of vinyls
    for page in range(1, num_pages + 1):
        
        # get data
        response_json = search_artist_database(artist, page=page, per_page=100)

        # **** ----- I WONDER IF IT'D BE FASTER JUST TO STORE THE ENTIRE RESPONSE, RATHER THAN GRAB ATTRIBUTES ----- **** #
        # **** ----- I'D JUST NEED TO REMEMBER TO CREATE A DICT FOR EACH RESPONSE, OR REMOVE THE OUTER RESULTS DICT/LIST THING ----- **** #

        # store artist, master_id, title, uri, year and thumbnail
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
            except: # if error just skip this release
                pass
    
    # remove duplicate dictionaries
    # convert each dictionary to a frozenset and create a set
    unique_set = {frozenset(d.items()) for d in vinyls}

    # convert the unique frozensets back to dictionaries
    unique_vinyls = [dict(t) for t in unique_set]

    # **** ----- I MIGHT BE BETTER OFF SORTING FROM THE DB REQUEST ----- **** #
    # sort
    sorted_unique_vinyls = sorted(vinyls, key=lambda x: x['year'])

    # add records to database:
    for vinyl in sorted_unique_vinyls:
        MainRelease(artist=vinyl["artist"],
                    master_id=vinyl["master_id"],
                    title=vinyl["title"],
                    uri=vinyl["uri"],
                    year=vinyl["year"],
                    thumb=vinyl["thumb"]).save()
    
    # return 
    return sorted_unique_vinyls


def main():
    master_id = "143592"
    # get the main release id (original pressing id) from that random master
    print(f"get_main_release_id({master_id})")
    main_release_id = get_main_release_id(master_id)
    print(main_release_id) # 7054180
    print("-------------------------------")
    # get the listing_ids (the original pressings available for sale) based on that random master
    print(f"get_listing_ids({main_release_id})")
    listing_ids = get_listing_ids(main_release_id)
    print(listing_ids) # ['1267047972']... for now, this could change if this record sells (6/3/2023)
    print("-------------------------------")
    print(f"get_marketplace_listing{listing_ids[0]}")
    marketplace_listing = get_marketplace_listing(listing_ids[0])
    print(marketplace_listing)

    
if __name__ == '__main__':
    main()