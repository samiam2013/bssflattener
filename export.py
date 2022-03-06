#!/usr/bin/python3

import base64
import cssutils
import os
import re
import time
import sys
import validators
from bs4 import BeautifulSoup
from os.path import basename
from os.path import basename
from os.path import splitext
from pathlib import Path
from posixpath import splitext
from urllib.parse import urlparse, parse_qs
from urllib.request import urlretrieve

'''
some notes:
returned paths have to be relative to the export location
filenames created for urls need to have a format for storing the key value pairs in the query string
source maps for .min.css files (and maybe js) can found (cheaply) with HEAD requests.
'''

EXT_DIR = sys.argv[1]

visited = []

def flatten(path):
    filename = basename(path)
    ext = splitext(filename)[1]
    # TODO add '.js' (To handle getting maps for  minified version if possible)
    if ext in ['.css', '.html']:
        for new_path in replace_links(path, ext):
            flatten(new_path)
    return None


def replace_links(path, ext):
    if ext == '.css':
        if path in visited:
            return []
        return cssutils_sanitize_dl(path)
    elif ext == '.html':
        if path in visited:
            return []
        #print('path for bs4', path)
        return bs4_sanitize_dl(path)
    # elif ext is '.js':
        # TODO handle this case
    else:
        raise Exception("file extension type ", ext, " not recognized/handled")

# sanitize the given html, return new paths


def bs4_sanitize_dl(path):
    fh = open(EXT_DIR + path, 'r+')
    content = fh.read()
    # the new paths to be returned
    new_paths = []

    soup = BeautifulSoup(content, 'html.parser')
    # find the <link> elements with attribute rel="stylesheet"
    stylesheets = soup.find_all('link', {'rel': 'stylesheet'})

    for sheet in stylesheets:
        if validators.url(sheet['href']):
            cached_path = cache_and_replace(sheet['href'])
            sheet['href'] = cached_path
            new_paths.append(cached_path)

    # find the <script> elements with any source attribute
    scripts = soup.find_all('script', {'src': True})
    for script in scripts:
        if validators.url(script['src']):
            cached_path = cache_and_replace(script['src'])
            script['src'] = cached_path
            new_paths.append(cached_path)

    fh.seek(0)
    fh.truncate()
    fh.write(soup.prettify())
    fh.close()
    visited.append(path)
    return new_paths


def cssutils_sanitize_dl(path):
    fh = open(EXT_DIR + path, 'r+')
    content = fh.read()
    parsed = cssutils.parseString(content.encode())

    new_paths = []
    for url in cssutils.getUrls(parsed):
        new_path = cache_and_replace(url)
        new_paths.append(new_path)
    cssutils.replaceUrls(parsed, cache_and_replace)

    # source map url in decoded file will always be on the last line
    lines = parsed.cssText.decode().split("\n")
    last_line = lines[-1:][0]
    source_map_link = re.search(r'sourceMappingURL=([^\s]+)', last_line)

    # cssutils.ser.prefs.useMinified()
    # can't remove comments or likely to be infringing on a FOSS license
    cssutils.ser.prefs.keepComments = True
    minified = parsed.cssText.decode()
    if source_map_link is not None:
        print('source map', source_map_link[1])
        minified = str(minified).replace(
            source_map_link[1], 'removed-for-GDPR:'+source_map_link[1])

    fh.seek(0)
    fh.truncate()
    fh.write(minified)
    fh.close()
    visited.append(path)
    # return a list of any new paths created
    return new_paths


def is_URL(url):
    try:
        parts = urlparse(url)
        if not str(parts[0]).lower().startswith('http'):
            return False
        return True
    except:  # Exception as e:
        return False


def parse_query(parts_qs):
    qs = parse_qs(parts_qs)
    buf = ''
    for key in qs:
        b64_val = base64.b64encode(str(qs[key]).encode()).decode()
        buf += key + '-' + b64_val
    return buf


def path_from_URL(url):
    parts = urlparse(url)
    domain = parts.netloc
    filename = basename(parts.path)
    split = splitext(filename)
    ext = split[1]
    query_fragment = parse_query(parts.query)
    if len(query_fragment) != 0:
        query_fragment = '.' + query_fragment
    new_path = '/ext/' + domain + '.' + split[0] + query_fragment + ext
    return new_path


# TODO how do you test this expiry code
def cache_and_replace(url):
    if not is_URL(url):
        return url
    cached_path = path_from_URL(url)
    full_cached_path = EXT_DIR + cached_path
    if os.path.exists(full_cached_path):
        open(full_cached_path)
        modified = os.path.getmtime(full_cached_path)
        if int(time.time()) < modified + (60 * 60 * 24 * 3):
            return cached_path
    if not os.path.exists(os.path.dirname(full_cached_path)):
        os.makedirs(os.path.dirname(full_cached_path))
    urlretrieve(url, full_cached_path)
    return cached_path


# call this with os.args[1] in prod

for (root, dirs, files) in os.walk(EXT_DIR):
    for file in files:
        if file.endswith(('.html', '.css')):
            print('flattening path: (root, dirs, file) ', root, dirs, file)
            if root != EXT_DIR:
                file = os.path.join(root, file).replace(EXT_DIR, '')
            if file not in visited:
                flatten(file)
