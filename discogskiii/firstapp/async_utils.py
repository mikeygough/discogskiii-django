# trying to convert utils.py into async functions

# imports
from config import *
from bs4 import BeautifulSoup
from datetime import datetime
from fake_useragent import UserAgent
import json
import os
import re
import requests
import time

# async libs
import asyncio
import aiohttp

# X get_main_release_id
# X get_release_statistics
# get_listing_ids
# # get_marketplace_listing

# -
# get_main_release_ids_async
# - 

# sample master_ids list
master_ids = ["143593", "84391", "143592", "1456111", "842283"]

# ---- SYNC WAY ----
print("GET_MAIN_RELEASE_IDS SYNC RESULTS")
main_release_id_sync_results = []

start = time.time()
for master_id in master_ids:
    # get
    response = requests.get(f"{API_BASE_URL}/masters/{master_id}",
                            headers=AUTHENTICATION_HEADER)
    # append
    main_release_id_sync_results.append(response.json()["main_release"])

end = time.time()
total_time = end - start
print("SYNC RESULTS", main_release_id_sync_results)
print(f"It took {total_time} seconds synchronously", '\n')

# ---- ASYNC WAY ----
async def get_main_release_ids_async(master_ids=master_ids):
    ''' REQUIRES AUTHENTICATION
        given a list of master_ids, return list of main_release_ids (original pressing ids) '''

    # initialize results list
    main_release_id_results = []

    async with aiohttp.ClientSession() as session:
        # initialize list of tasks
        tasks = []
        for master_id in master_ids:
            # create and append tasks (API request)
            tasks.append(session.get(f"{API_BASE_URL}/masters/{master_id}",
                                    headers=AUTHENTICATION_HEADER,
                                    ssl=False))
        
        # request
        responses = await asyncio.gather(*tasks)

        # append results
        for response in responses:
            result = await response.json()
            main_release_id_results.append(result["main_release"])

        # return list of main_release ids
        return main_release_id_results

print("GET_MAIN_RELEASE_IDS ASYNC RESULTS")
start = time.time()
main_release_ids = asyncio.run(get_main_release_ids_async(master_ids=master_ids))
end = time.time()
total_time = end - start
print("ASYNC RESULTS", main_release_ids)
print(f"It took {total_time} seconds asynchronously (with tasks combined)", '\n')


# - 
# get_release_stats_async
# -

# sample release_ids list
release_ids = ["1885283", "2173436", "1034602", "385862", "498022", "549847", "3794919", "872608", "533862"]

# ---- SYNC WAY ----
print("GET_RELEASE_STATISTICS SYNC RESULTS")
release_stats_sync_results = []

start = time.time()
for release_id in release_ids:    
    # get
    response = requests.get(f"{API_BASE_URL}/marketplace/stats/{release_id}",
                            headers=AUTHENTICATION_HEADER,
                            params={
                                "curr_abbr": "USD"})
    # append
    release_stats_sync_results.append(response.json()["num_for_sale"])

end = time.time()
total_time = end - start
print("SYNC RESULTS", release_stats_sync_results)
print(f"It took {total_time} seconds synchronously", '\n')

# ---- ASYNC WAY ----
release_stats_results_async = []

async def get_release_statistics_async(release_ids=release_ids):
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
            release_statistic_results.append(result["num_for_sale"])

        # return list of release statistics
        return release_statistic_results

print("GET_RELEASE_STATISTICS ASYNC RESULTS")
start = time.time()
release_statistics = asyncio.run(get_release_statistics_async(release_ids=release_ids))
end = time.time()
total_time = end - start
print("ASYNC RESULTS", release_statistics)
print(f"It took {total_time} seconds asynchronously (with tasks combined)", '\n')


# -
# get_release_stats_async
# -


# sample marketplace_listing_ids list
marketplace_listing_ids = ["2512127975", "2147701925", "2144595464", "2523264396", "2494120061", "2494326032"]


# ---- SYNC WAY ----
print("GET_MARKETPLACE_LISTINGS SYNC RESULTS")
marketplace_sync_results = []

start = time.time()
for marketplace_listing in marketplace_listing_ids:
    # get
    response = requests.get(f"{API_BASE_URL}/marketplace/listings/{marketplace_listing}",
                    headers=AUTHENTICATION_HEADER)
    
    # append
    marketplace_sync_results.append(response.json())

end = time.time()
total_time = end - start
print(f"It took {total_time} seconds synchronously", '\n')

# ---- ASYNC WAY (tasks) ---- 
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

print("GET_MARKETPLACE_LISTING_ASYNC RESULTS")
start = time.time()
marketplace_listings = asyncio.run(get_marketplace_listings_async(marketplace_listing_ids=marketplace_listing_ids))
end = time.time()
total_time = end - start
print(f"It took {total_time} seconds asynchronously (with tasks combined)")
