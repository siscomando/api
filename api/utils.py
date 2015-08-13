# -*- coding: utf-8 -*-

"""
 Utils.py
"""

import re
import json
import hashlib
import hmac
import base64
import settings
import datetime
import jwt
import settings
from bson import ObjectId


def generate_token(user_id):
    secret_key = settings.SECRET_KEY

    if not secret_key:
        raise TypeError(u'Environment variable SECRET_KEY is not defined.')

    payload = {
        'sub': str(user_id),
        'iat': datetime.datetime.now()
    }
    encoded = jwt.encode(payload, secret_key, algorithm='HS256')
    return base64.b64encode(encoded + ':') #

def to_link_hashtag(hashtag):
    return '<sc-link class="hashLink" eventname="hashtag-to-search" ' \
                'colorlink="#47CACC" href="/hashtag/{value}">{value}' \
                '</sc-link>'.format(value=hashtag)

def wrap_pattern_by_link(pattern, content):
    """ Wrap a pattern by a link.

    :param pattern: regex pattern to filter
    :param content: content for parse
    """
    filter = re.compile(pattern)

    def wrapper(matchobj):
        if matchobj.group(0):
            return to_link_hashtag(matchobj.group(0))

    return re.sub(filter, wrapper, content)

class JSONEncoder(json.JSONEncoder):
    """ Class helper to convert ObjectId to str. This is a
    wrapper to solve this error `ObjectId('') is not JSON serializable...``
    """

    def default(self, o):
        if isinstance(o, ObjectId) or isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)
