# settings for RESTful API
#
import os
from api.schemas import users_schema, issues_schema
from api.resources import DOMAIN

# It's useful for webapp, because RESTful not make uses this configuration due
# all request are authenticated without cookies or sessions. But I using to
# generate hashs.
SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = True

# Database setup
MONGO_HOST = "localhost"
MONGO_POST = "27017"
# MONGO_DBNAME is temporally added hard but place it app's global settings.
MONGO_DBNAME = "dev_scdb"

# Versioning
URL_PREFIX = "api"
API_VERSION = "v2"

# Feature to expand embedded documents from reference fields
#QUERY_EMBEDDED = "expanded" # Changed from embedded to expanded. Default: embedded
EMBEDDING = True

# Scope from models. Custom properties.
DATE_CREATED = "created_at"
LAST_UPDATED = "updated_at"

# SOFT_DELETE = True # NOT WORKING see more: http://python-eve.org/features.html#soft-delete
XML = False
IF_MATCH = False # CAUTION: temporally disabled. This keeps versions correclty updated.
# PUBLIC_METHODS = ['GET'] # This override auth_field behavior
# PUBLIC_ITEM_METHODS = ['GET'] # This override auth_field behavior
# ALLOWED_ROLES = ['users'] # minimal role required.
X_DOMAINS = '*' # You can to specify a list of domains.
