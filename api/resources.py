# The `DOMAIN` is commonly put on settings but we preferences was to create
# domains.py file.

from api.schemas import users_schema


DOMAIN = {
    'users': {
        'url': 'users',
        'datasource': {
            'source': 'user',
                'projection': {'password': 0}
        },
        'cache_control': '', # account cache is not needs.
        'cache_expires': 0,
        'resource_methods': ['GET', 'POST'],
        'schema': users_schema, # EVEMongoengine?
        'allowed_write_roles': ['superusers'],
    },
}
