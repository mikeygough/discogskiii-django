# helper functions
from config import *
import requests
import json


# base variables
base_url = "https://api.discogs.com"
headers = {
    "Authorization": f"Discogs key={CONSUMER_KEY}, secret={CONSUMER_SECRET}",
}


def get_marketplace_listing(listing_id):
    ''' REQUIRES AUTHENTICATION
        return marketplace listing json '''
    
    response = requests.get(f"{base_url}/marketplace/listings/{listing_id}",
                    headers=headers).text

    # turn string into pretty json
    response_json = json.loads(response)
    response_json = json.dumps(response_json, indent=4)

    return response_json

def main():
    print("get_marketplace_listing")
    listing = get_marketplace_listing('2047141883')
    print(listing)
    
if __name__ == '__main__':
    main()