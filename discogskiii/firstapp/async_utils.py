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


# ---- ASYNC WAY ----
async_results = []

async def get_main_releases():
    async with aiohttp.ClientSession() as session:
        for master_id in masters:
            print(f"Working on master{master_id}")
            
            # get
            response = await session.get(f"{API_BASE_URL}/masters/{master_id}",
                                    headers=AUTHENTICATION_HEADER,
                                    ssl=False)
            # append
            results = await response.json()

            async_results.append(results["main_release"])

start = time.time()

asyncio.run(get_main_releases())

end = time.time()
total_time = end - start
print("ASYNC RESULTS", async_results)
print(f"It took {total_time} seconds asynchronously")


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
print(f"It took {total_time} seconds synchronously")


# ---- RESULTS ----
# It took 1.3902409076690674 seconds asynchronously
# It took 1.6589751243591309 seconds synchronously