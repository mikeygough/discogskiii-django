# trying to convert utils.py into async functions
# helper functions
from config import *
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json
import re
from datetime import datetime

# async libs
import asyncio
import aiohttp


def async_get_main_release_id(master_id):
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