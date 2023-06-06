# helper functions
from config import *
import requests
import json


# base variables
base_url = "https://api.discogs.com"
authentication_header = {
    "Authorization": f"Discogs key={CONSUMER_KEY}, secret={CONSUMER_SECRET}",
}


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
    
    response = requests.get(f"{base_url}/database/search",
                            headers=authentication_header,
                            params=params).text
    # turn string into json
    response_json = json.loads(response)
    # get master_id
    master_id = response_json["results"][0]["id"]
    
    return master_id


def get_main_release_id(master_id):
    ''' REQUIRES AUTHENTICATION
        returns release_id of the master release'''
    
    response = requests.get(f"{base_url}/masters/{master_id}",
                            headers=authentication_header).text
    # turn string into json
    response_json = json.loads(response)
    # get release_id of master release
    main_release_id = response_json["main_release"]
    return main_release_id


def get_marketplace_listing(listing_id):
    ''' REQUIRES AUTHENTICATION
        return marketplace listing json '''
    
    response = requests.get(f"{base_url}/marketplace/listings/{listing_id}",
                    headers=authentication_header).text

    # turn string into pretty json
    response_json = json.loads(response)
    response_json = json.dumps(response_json, indent=4)

    return response_json

def main():
    print("get_master_id('sun ra')")
    master_id = get_master_id("sun ra")
    print(master_id) # 143592
    print("-------------------------------")
    print(f"get_main_release_id({master_id})")
    main_release_id = get_main_release_id(master_id)
    print(main_release_id) # 7054180
    print("-------------------------------")
    print("get_marketplace_listing")
    listing = get_marketplace_listing("2047141883")
    print(listing)
    
if __name__ == '__main__':
    main()