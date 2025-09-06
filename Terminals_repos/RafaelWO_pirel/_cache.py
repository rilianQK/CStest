# proj_clean/pirel/_cache.py

import os
import json
import glob
import pathlib
from datetime import datetime, timedelta

CACHE_DIR = pathlib.Path.home() / ".pirel_cache"
CACHE_FILE_GLOB = "pirel_cache_*.json"

def filename():
    """The name of today's cache file."""
    return CACHE_DIR / f"pirel_cache_{datetime.now().strftime('%Y%m%d')}.json"

def calc_cache_age_days(cache_file):
    """Returns the age of the cache in days."""
    cache_date = datetime.strptime(cache_file.stem.split('_')[-1], '%Y%m%d')
    return (datetime.now() - cache_date).days

def clear(clear_all=False):
    """Delete old or all cache files."""
    if clear_all:
        files = glob.glob(str(CACHE_DIR / CACHE_FILE_GLOB))
    else:
        files = [str(f) for f in CACHE_DIR.glob(CACHE_FILE_GLOB) if calc_cache_age_days(f) > 7]
    
    for file in files:
        os.remove(file)

def get_latest_cache_file():
    """Returns the path to the latest cache file `None` if no cache exists."""
    files = list(CACHE_DIR.glob(CACHE_FILE_GLOB))
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def load(cache_file):
    """Loads the data from a cache file path."""
    with open(cache_file, 'r') as f:
        return json.load(f)

def save(data):
    """Save data to new cache file."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(filename(), 'w') as f:
        json.dump(data, f)