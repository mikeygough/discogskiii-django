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