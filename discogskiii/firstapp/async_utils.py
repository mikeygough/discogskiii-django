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
# get_marketplace_listing


'''

# ----- testing -----
# GET MAIN RELEASE ID
# ----- testing -----


# sample master_ids list
masters = ["143593", "84391", "143592", "1456111", "842283"]


# ---- SYNC WAY ----
sync_results = []

start = time.time()
for master_id in masters:
    print(f"Working on master{master_id}")
    
    # get
    response = requests.get(f"{API_BASE_URL}/masters/{master_id}",
                            headers=AUTHENTICATION_HEADER)
    # append
    sync_results.append(response.json()["main_release"])

end = time.time()
total_time = end - start
print("SYNC RESULTS", sync_results)
print(f"It took {total_time} seconds synchronously", '\n')


# ---- ASYNC WAY 1 ----
async_results_1 = []

async def get_main_releases_1():
    start = time.time()
    async with aiohttp.ClientSession() as session:
        for master_id in masters:
            print(f"Working on master{master_id}")
            
            # get
            response = await session.get(f"{API_BASE_URL}/masters/{master_id}",
                                    headers=AUTHENTICATION_HEADER,
                                    ssl=False)
            # append
            results = await response.json()

            async_results_1.append(results["main_release"])
    end = time.time()
    total_time = end - start
    print("ASYNC_1 RESULTS", async_results_1)
    print(f"It took {total_time} seconds asynchronously", '\n')

asyncio.run(get_main_releases_1())


# ---- ASYNC WAY 2 (tasks) ----
async_results_2 = []

def get_tasks(session):
    tasks = []
    for master_id in masters:
        tasks.append(session.get(f"{API_BASE_URL}/masters/{master_id}",
                                    headers=AUTHENTICATION_HEADER,
                                    ssl=False))
    return tasks

async def get_main_releases_2():
    start = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = get_tasks(session)
        responses = await asyncio.gather(*tasks)
        for response in responses:
            results = await response.json()
            async_results_2.append(results["main_release"])
    end = time.time()
    total_time = end - start
    print("ASYNC_2 RESULTS", async_results_2)
    print(f"It took {total_time} seconds asynchronously (with tasks)")

asyncio.run(get_main_releases_2())

# ---- RESULTS ----
# It took 1.3869702816009521 seconds synchronously
# It took 1.0460200309753418 seconds asynchronously
# It took 0.3535647392272949 seconds asynchronously

'''

'''

# ----- testing -----
# GET RELEASE STATS
# ----- testing -----


# sample release_ids list
release_ids = ["1885283", "2173436", "1034602", "385862", "498022", "549847", "3794919", "872608", "533862"]


# ---- SYNC WAY ----
release_stats_results = []

start = time.time()
for release_id in release_ids:    
    # get
    response = requests.get(f"{API_BASE_URL}/marketplace/stats/{release_id}",
                            headers=AUTHENTICATION_HEADER,
                            params={
                                "curr_abbr": "USD"})
    # append
    release_stats_results.append(response.json()["num_for_sale"])

end = time.time()
total_time = end - start
print("GET_RELEASE_STATISTICS SYNC RESULTS", release_stats_results)
print(f"It took {total_time} seconds synchronously", '\n')


# ---- ASYNC WAY (tasks) ----
release_stats_results_async = []

def get_release_statistic_tasks(session):
    tasks = []
    for release_id in release_ids:
        tasks.append(session.get(f"{API_BASE_URL}/marketplace/stats/{release_id}",
                            headers=AUTHENTICATION_HEADER,
                            params={
                                "curr_abbr": "USD"},
                            ssl=False))
    return tasks

async def get_release_statistics_async():
    start = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = get_release_statistic_tasks(session)
        responses = await asyncio.gather(*tasks)
        for response in responses:
            results = await response.json()
            release_stats_results_async.append(results["num_for_sale"])
        end = time.time()
        total_time = end - start
        print("GET_RELEASE_STATISTICS_ASYNC RESULTS", release_stats_results_async)
        print(f"It took {total_time} seconds asynchronously (with tasks)")

asyncio.run(get_release_statistics_async())

# ---- RESULTS ----
# It took 2.585681200027466 seconds synchronously
# It took 0.41822099685668945 seconds asynchronously (with tasks)

'''

# ----- testing -----
# GET MARKETPLACE LISTING
# ----- testing -----


# sample marketplace_listing_ids list
marketplace_listing_ids = ["2512127975", "2147701925", "2144595464", "2523264396", "2494120061", "2494326032"]


# ---- SYNC WAY ----
marketplace_results = []

print("GET_MARKETPLACE_LISTING SYNC RESULTS")

start = time.time()
for marketplace_listing in marketplace_listing_ids:
    # get
    response = requests.get(f"{API_BASE_URL}/marketplace/listings/{marketplace_listing}",
                    headers=AUTHENTICATION_HEADER)
    
    # append
    marketplace_results.append(response.json())

end = time.time()
total_time = end - start

# print("GET_MARKETPLACE_LISTING SYNC RESULTS", marketplace_results)
print(f"It took {total_time} seconds synchronously", '\n')


# ---- ASYNC WAY (tasks) ---- 
marketplace_results_async = []

def get_marketplace_listing_tasks(session):
    tasks = []
    for marketplace_listing in marketplace_listing_ids:
        tasks.append(session.get(f"{API_BASE_URL}/marketplace/listings/{marketplace_listing}",
                            headers=AUTHENTICATION_HEADER,
                            ssl=False))
    return tasks

async def get_marketplace_listings_async():
    start = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = get_marketplace_listing_tasks(session)
        responses = await asyncio.gather(*tasks)
        for response in responses:
            results = await response.json()
            marketplace_results_async.append(results)
        end = time.time()
        total_time = end - start
        # print("GET_MARKETPLACE_LISTING_ASYNC RESULTS", marketplace_results_async)
        print(f"It took {total_time} seconds asynchronously (with tasks)")

print("GET_MARKETPLACE_LISTING_ASYNC RESULTS")
asyncio.run(get_marketplace_listings_async())
