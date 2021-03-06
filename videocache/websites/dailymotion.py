#!/usr/bin/env python
#
# (C) Copyright Kulbir Saini <saini@saini.co.in>
# Product Website : http://cachevideos.com/
#

__author__ = """Kulbir Saini <saini@saini.co.in>"""
__docformat__ = 'plaintext'

import os
import re
import urllib
import urlparse

VALIDATE_DAILYMOTION_DOMAIN_REGEX1 = re.compile('.*\..*\.dmcdn\.net')
VALIDATE_DAILYMOTION_DOMAIN_REGEX2 = re.compile('proxy[a-z0-9\-]?[a-z0-9]?[a-z0-9]?[a-z0-9]?\.dailymotion\.com')
VALIDATE_DAILYMOTION_FRAGMENT_REGEX = re.compile('.*\/frag\([0-9]+\)\/.*')
VALIDATE_DAILYMOTION_VIDEO_EXT_REGEX = re.compile('\.(flv|mp4|avi|mkv|mp3|rm|rmvb|m4v|mov|wmv|3gp|mpg|mpeg|on2)')
DAILYMOTION_FRAGMENT_EXTRACT_REGEX = re.compile('.*frag\(([0-9]+)\).*')

def get_dailymotion_filename(o, video_id, format):
    if format:
        return '.'.join([video_id, format])
    return video_id

def dailymotion_cached_url(o, video_id, website_id, format, params = {}):
    found, dir, size, index, cached_url = False, '', '-', '', ''
    filenames = list(set([video_id, get_dailymotion_filename(o, video_id, format)]))

    for dir in o.base_dirs[website_id]:
        for filename in filenames:
            try:
                video_path = os.path.join(dir, filename)
                if os.path.isfile(video_path):
                    size = os.path.getsize(video_path)
                    os.utime(video_path, None)
                    if len(o.base_dirs[website_id]) > 1: index = str(o.base_dirs[website_id].index(dir))
                    cached_url = o.redirect_code + ':' + os.path.join(o.cache_url, o.cache_alias, index, o.website_cache_dir[website_id], filename)
                    return (True, filename, dir.rstrip(o.website_cache_dir[website_id]), size, index, cached_url)
            except Exception, e:
                continue
    return (False, filenames[0], '', '-', '', '')

def check_dailymotion_video(o, url, host = None, path = None, query = None):
    matched, website_id, video_id, format, search, queue, report_hit = True, 'dailymotion', None, '', True, True, True

    if not (host and path and query):
        fragments = urlparse.urlsplit(url)
        [host, path, query] = [fragments[1], fragments[2], fragments[3]]

    if (VALIDATE_DAILYMOTION_DOMAIN_REGEX1.search(host) or host.find('vid.akm.dailymotion.com') > -1 or VALIDATE_DAILYMOTION_DOMAIN_REGEX2.search(host)) and VALIDATE_DAILYMOTION_FRAGMENT_REGEX.search(path) and VALIDATE_DAILYMOTION_VIDEO_EXT_REGEX.search(path):
        queue = False
        fragment = []
        match = DAILYMOTION_FRAGMENT_EXTRACT_REGEX.search(path)
        if match:
            fragment = [match.group(1)]
        parts = urllib.quote(path.strip('/').split('/')[-1]).split('.')
        if len(parts) < 2:
            video_id = '_'.join((parts + fragment))
        else:
            video_id = '_'.join(parts[:-1] + fragment)
            format = parts[-1]
    else:
        matched = False

    return (matched, website_id, video_id, format, search, queue, report_hit)
