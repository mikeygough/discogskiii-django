# helper functions
from config import *
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json
import re
import requests


# base variables
site_base_url = "https://www.discogs.com"
api_base_url = "https://api.discogs.com"
authentication_header = {
    "Authorization": f"Discogs key={CONSUMER_KEY}, secret={CONSUMER_SECRET}",
}
ua = UserAgent()


def get_master_id(artist):
    ''' REQUIRES AUTHENTICATION
        returns master_id of first result from
        discogs database artist search with specific query parameters'''
    
    # set query parameters
    params = {
    "artist": f"{artist}",
    "type": "master",
    "format": "vinyl",
    "page": "1"
    }
    
    response = requests.get(f"{api_base_url}/database/search",
                            headers=authentication_header,
                            params=params).text
    # turn string into json
    response_json = json.loads(response)
    # get master_id of first result arbitrarily
    master_id = response_json["results"][0]["id"]
    
    return master_id


def get_main_release_id(master_id):
    ''' REQUIRES AUTHENTICATION
        returns release_id of the master release'''
    
    response = requests.get(f"{api_base_url}/masters/{master_id}",
                            headers=authentication_header).text
    # turn string into json
    response_json = json.loads(response)
    # get release_id of master release
    main_release_id = response_json["main_release"]
    return main_release_id


def get_listing_ids(release_id):
    ''' returns list of listing_ids for a given release_id '''
    
    response = requests.get(f"{site_base_url}/sell/release/{release_id}",
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
    
    response = requests.get(f"{api_base_url}/marketplace/listings/{listing_id}",
                    headers=authentication_header).text

    # turn string into pretty json
    response_json = json.loads(response)
    response_json = json.dumps(response_json, indent=4)

    return response_json


def main():
    # get random master from search 'sun ra'
    print("get_master_id('sun ra')")
    master_id = get_master_id("sun ra")
    print(master_id) # 143592
    print("-------------------------------")
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