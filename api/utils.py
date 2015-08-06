import re

def to_link_hashtag(hashtag):
    return '<a class="hashLink" eventname="hashtag-to-search" ' \
                'colorlink="#47CACC" href="/hashtag/{value}">{value}' \
                '</a>'.format(value=hashtag)

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
