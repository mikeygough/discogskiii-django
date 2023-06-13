# trying to convert utils.py into async functions
# helper functions
from config import *
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json
import re
from datetime import datetime
import requests

# async libs
import asyncio
import aiohttp

# testing imports
import os
import time

# ----- testing -----
# GET MAIN RELEASE ID
# ----- testing -----

# sample master_ids list
masters = ["143593", "84391", "143592", "1456111", "842283"]
results = []

for master_id in masters:

    print(f"Working on master{master_id}")
    
    # get data as json
    response = requests.get(f"{API_BASE_URL}/masters/{master_id}",
                            headers=AUTHENTICATION_HEADER)

    print(response.json()["main_release"])

# start = time.time()
# end = time.time()
# total_time = end - start
# print(f"It took {} seconds".format(total_time))