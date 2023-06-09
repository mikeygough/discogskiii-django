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
        helpful for obtaining a release's master_id'''

    # get data, return as json
    response_json = json.loads(requests.get(f"{API_BASE_URL}/database/search",
                            headers=AUTHENTICATION_HEADER,
                            params={
                                "artist": f"{artist}",
                                "type": "master",
                                "format": "vinyl",
                                "page": f"{page}",
                                "per_page": f"{per_page}"}).text)
    
    return response_json



def get_main_release_id(master_id):
    ''' REQUIRES AUTHENTICATION
        returns release_id of the master release'''
    
    response = requests.get(f"{API_BASE_URL}/masters/{master_id}",
                            headers=AUTHENTICATION_HEADER).text
    # turn string into json
    response_json = json.loads(response)
    # get release_id of master release
    main_release_id = response_json["main_release"]
    return main_release_id


def get_listing_ids(release_id):
    ''' returns list of listing_ids for a given release_id '''
    
    # create UserAgent
    ua = UserAgent()
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
    listing_ids = []
    for link in links:
        # '?' removes additional query parameters (currency)
        if filter in str(link) and '?' not in str(link):
            # regex the id
            listing_ids.append(re.findall(r'-?\d+\.?\d*', str(link)))
    # flatten the list
    listing_ids = [item for sublist in listing_ids for item in sublist]
    return listing_ids
    
    # add to unit_test
    # print(page.status_code)

    # looks like we can get a sell history: /sell/history/7068875
    # full link: https://www.discogs.com/sell/history/7068875


def get_marketplace_listing(listing_id):
    ''' REQUIRES AUTHENTICATION
        return marketplace listing json '''
    
    response = requests.get(f"{API_BASE_URL}/marketplace/listings/{listing_id}",
                    headers=AUTHENTICATION_HEADER).text

    # turn string into pretty json
    response_json = json.loads(response)
    # response_json = json.dumps(response_json, indent=4)

    return response_json


def get_artist_markets(artist):
    ''' REQUIRES AUTHENTICATION
        return list of dictionary objects representing all an artists' master releases '''
    
    # first get number of pages:
    # num_pages = json.loads(requests.get(f"{API_BASE_URL}/database/search",
    #                                     headers=AUTHENTICATION_HEADER,
    #                                     params={
    #                                         "artist": f"{artist}",
    #                                         "type": "master",
    #                                         "format": "vinyl"
    #                                         }).text)["pagination"]["pages"]
    
    num_pages = search_artist_database(artist, page=1, per_page=100)["pagination"]["pages"]
    # initialize empty list for vinyls
    vinyls = []

    # iterate through number of pages, get data, add to list of vinyls
    for page in range(1, num_pages + 1):
        # get data
        response_json = search_artist_database(artist, page=page)

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
    
    # remove duplicate values (is not working 100%)
    seen = set()
    new_l = []
    for d in sorted_vinyls:
        t = tuple(d.items())
        if t not in seen:
            seen.add(t)
            new_l.append(d)

    # add records to database:
    for vinyl in new_l:
        MainRelease(artist=vinyl["artist"],
                    master_id=vinyl["master_id"],
                    title=vinyl["title"],
                    uri=vinyl["uri"],
                    year=vinyl["year"],
                    thumb=vinyl["thumb"]).save()
    return new_l


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