# helper functions
from firstapp.config import *
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json
import re
import requests
from datetime import datetime

# async libs
import asyncio
import aiohttp

# import models
from firstapp.models import MasterRelease


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


async def get_master_main_release_ids_async(master_ids):
    ''' REQUIRES AUTHENTICATION
        given a list of master_ids, return list of tuples. each tuple represents an original pressing.
        the first item is the master_id, the second item is the main_id (original pressing id) '''

    # initialize results list
    main_release_id_results = []

    async with aiohttp.ClientSession() as session:
        # initialize list of tasks
        tasks = []
        for master_id in master_ids:
            # create and append tasks (API requests)
            tasks.append(session.get(f"{API_BASE_URL}/masters/{master_id}",
                                    headers=AUTHENTICATION_HEADER,
                                    ssl=False))
        
        # request
        responses = await asyncio.gather(*tasks)

        # append results
        for response in responses:
            result = await response.json()
            main_release_id_results.append(result)

                # this one only grabs the main_release_ids
        # main_release_id_results = [d["main_release"] for d in main_release_id_results]
                # this one grabs the main_release_id and the master_id
        main_release_id_results = [(d["id"], d["main_release"]) for d in main_release_id_results]
        # return list of main_release ids
        return main_release_id_results


async def get_main_release_data_async(release_ids):
    ''' REQUIRES AUTHENTICATION
        given a list of release_ids, return a list of ____ with all the data needed to construct
        a new MainRelease model: artist, title, uri, main_id, num_for_sale, lowest_price, master. 
        and ideally [community][want] and [community][have]'''

    # initialize results list
    main_release_results = []

    async with aiohttp.ClientSession() as session:
        # initialize list of tasks
        tasks = []
        for release_id in release_ids:
            # create and append tasks (API requests)
            tasks.append(session.get(f"{API_BASE_URL}/releases/{release_id}",
                         headers=AUTHENTICATION_HEADER,
                         ssl=False))
            
        # request
        responses = await asyncio.gather(*tasks)

        # append results
        for response in responses:
            result = await response.json()
            main_release_results.append(result)

        # loop through response dict and grab certain keys/values (some are nested)
        keys_to_keep = ["id", "uri", "community.have", "community.want",
                        "num_for_sale", "lowest_price", "master_id", "title", "released", "thumb"]
        
        list_of_dicts = []
        # loop through the list of dictionaries
        for item in main_release_results:
            # initialize an empty dictionary to store the extracted key-value pairs
            extracted_data = {}

            # loop through the keys
            for key in keys_to_keep:
                # split the key into nested levels
                nested_keys = key.split(".")

                # Traverse the nested keys to access the corresponding value in the dictionary
                value = item
                for nested_key in nested_keys:
                    if isinstance(value, dict) and nested_key in value:
                        value = value[nested_key]
                    else:
                        # If any nested key is not found, break the loop
                        value = None
                        break

                # Add the extracted key-value pair to the extracted_data dictionary
                extracted_data[key] = value

            list_of_dicts.append(extracted_data)
            
        # drop records with master_id: None which is an anomoly case that does occur
        list_of_dicts = [d for d in list_of_dicts if d.get("master_id") != None]

        # format, replace keys that have '.' with '_'
        list_of_dicts = [
            {key.replace(".", "_"): value for key, value in dictionary.items()}
            for dictionary in list_of_dicts]
        
        # return list of release statistics
        return list_of_dicts


def get_release_statistics(release_id):
    ''' REQUIRES AUTHENTICATION
        given a release_id, retun the number of releases
        available for sale and the lowest price as a tuple. '''

    # get data as json
    response_json = json.loads(requests.get(f"{API_BASE_URL}/marketplace/stats/{release_id}",
                            headers=AUTHENTICATION_HEADER,
                            params={
                                "curr_abbr": "USD"}).text)
    
    number_for_sale = response_json["num_for_sale"]
    lowest_price = response_json["lowest_price"]["value"]

    return number_for_sale


async def get_release_statistics_async(release_ids):
    ''' REQUIRES AUTHENTICATION
        given a list of release_ids, retun a list of the number
        of each release available for sale. '''

    # initialize results list
    release_statistic_results = []

    async with aiohttp.ClientSession() as session:
        # initialize list of tasks
        tasks = []
        for release_id in release_ids:
            # create and append tasks (API request)
            tasks.append(session.get(f"{API_BASE_URL}/marketplace/stats/{release_id}",
                        headers=AUTHENTICATION_HEADER,
                        params={
                            "curr_abbr": "USD"},
                        ssl=False))

        # request
        responses = await asyncio.gather(*tasks)

        # append results
        for response in responses:
            result = await response.json()
            release_statistic_results.append(result)

        # print("RELEASE_STATISTIC_RESULTS", release_statistic_results)

        release_statistic_results = [d["num_for_sale"] for d in release_statistic_results]
        # return list of release statistics
        return release_statistic_results
    

async def get_wantlist_release_statistics_async(release_ids):
    ''' REQUIRES AUTHENTICATION
        given a list of release_ids, return a list of tuples. each tuple represents an originall pressing.
        the first item is the community 'have' count, the second item is the community 'want' count. '''
    
    # initialize results list
    release_wantlist_statistic_results = []

    async with aiohttp.ClientSession() as session:
        # initialize list of tasks
        tasks = []
        for release_id in release_ids:
            # create and append tasks (API request)
            tasks.append(session.get(f"{API_BASE_URL}/releases/{release_id}",
                         headers=AUTHENTICATION_HEADER,
                         ssl=False))
        
        # request
        responses = await asyncio.gather(*tasks)

        # append results
        for response in responses:
            result = await response.json()
            release_wantlist_statistic_results.append(result)

        release_wantlist_statistic_results = [(d["community"]["have"], d["community"]["want"]) for d in release_wantlist_statistic_results]
        # return list of release wantlist statistics
        return release_wantlist_statistic_results


def get_listing_ids(release_id):
    ''' given a release_id, returns a list of listings of that release_id for sale.
        listings are records which are available for sale.
        helpful for obtaining original pressings which are listed for sale.
        
        BEWARE this is only capable of returning the first page of results (25 listings) '''

    # **** ----- would like to improve performance here ----- **** #
    
    # create UserAgent
    ua = UserAgent()
    
    # get data
    response = requests.get(f"{SITE_BASE_URL}/sell/release/{release_id}",
                            headers={"User-Agent": ua.chrome},
                            params={
                            "limit": "100"},)

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


async def get_marketplace_listings_async(marketplace_listing_ids):
    ''' REQUIRES AUTHENTICATION
        given a list of listing_ids, return list of API responses (marketplace listing json) '''
    
    # initialize results list
    marketplace_listing_results = []

    async with aiohttp.ClientSession() as session:
        # initialize list of tasks
        tasks = []
        for marketplace_listing in marketplace_listing_ids:
            # create and append tasks (API requests)
            tasks.append(session.get(f"{API_BASE_URL}/marketplace/listings/{marketplace_listing}",
                                   headers=AUTHENTICATION_HEADER,
                                   ssl=False))
        
        # request
        responses = await asyncio.gather(*tasks)
        
        # append results
        for response in responses:
            results = await response.json()
            marketplace_listing_results.append(results)

        # return list of marketplace responses
        return marketplace_listing_results


def get_artist_releases(artist):
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
            if "Unofficial Release" not in result["format"]:
                try:
                    info = {
                    "artist": f"{artist}",
                    "master_id": result["master_id"],
                    "title": result["title"],
                    "uri": result["uri"],
                    "year": result["year"],
                    "thumb": result["thumb"],
                    }
                    print(f"Caching {result['title']}")
                    vinyls.append(info)
                except: # if error just skip this release
                    pass
            else:
                print(f"Skipping {result['title']}, Unofficial Release")
    
    # remove duplicate dictionaries
    # convert each dictionary to a frozenset and create a set
    unique_set = {frozenset(d.items()) for d in vinyls}

    # convert the unique frozensets back to dictionaries
    unique_vinyls = [dict(t) for t in unique_set]

    # **** ----- I MIGHT BE BETTER OFF SORTING FROM THE DB REQUEST ----- **** #
    # sort
    sorted_unique_vinyls = sorted(vinyls, key=lambda x: x['year'])

    # return a list of sorted, unique dictionaries where
    # each dict represents an artist's master release
    return sorted_unique_vinyls


def format_currency(value):
    ''' format value as USD currency '''
    return '${:,.2f}'.format(value)


def format_date(date_str):
    dt = datetime.fromisoformat(date_str)
    formatted_date = dt.strftime('%B %d, %Y')  # format according to your preference
    return formatted_date


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