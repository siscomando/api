# This file contains the hooks that fires when `on_pre` or `on_post` Events
# are raised by API.
# See: http://python-eve.org/features.html#eventhooks

import json

def pre_post_users(request):
    """Adds at the body data that was send by user's API the `username`
    field. The username is the localpart from email address."""
    if not request.json:
        abort(401, "The body data isn't a JSON format.")

    json_data = json.loads(request.json)
    username = json_data['email'].split('@')[0]
    json_data['username'] = username
    request.json = json.dumps(json_data)



users_hooks = {}
users_hooks['username'] = pre_post_users
