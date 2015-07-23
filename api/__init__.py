# API's specifications
#
# Schema
# =====================
# All API access is over HTTP[S] and accessed from the siscomando.example/api/v2/.
# All data is sent and received as JSON.
#
# Date and Time
# =====================
# All timestamps are returned in ISO 8601 format:
# YYYY-MM-DDTHH:MM:SSZ
#
# Parameters
# =====================
# For GET requests, any parameters not specified as a path in the URL can be
# passed as an HTTP query string parameter:
# $ curl -i "https://siscomando.example/api/v2/issues/supgs?closed=true"
# In this example, the `supgs` is provided for the `Organization Unit while
# `closed` is passed in the query string.
#
# For POST, PATCH, PUT and DELETE requests parameters not represented in path in
# the URL should be encoded as JSON with "Content-Type of application/json".
# $ curl -i -u username
#    -d '{"comment": {"body":"This simples message"}}'
#    https://siscomando.example/api/v2/comments
#
# Root Endpoint
# =====================
# A GET request to the root endpoint get all the resources that the API supports.
# $ curl https://siscomando.example
#
# Client Errors
# =====================
#
import os
from eve.auth import BasicAuth
from eve import Eve
from werkzeug.security import check_password_hash
from eve_mongoengine import EveMongoengine
from flask import abort
from siscomando import models
from api.hooks import users_hooks
import settings


class ApiBasicAuth(BasicAuth):
	def check_auth(self, username, password, allowed_roles, resources, method):
		accounts = app.data.driver.db['user']
		lookup = {'email': username}

		if allowed_roles:
			# only retrieve a user if his roles match
			# DEBUG purpose

			lookup['roles'] = {'$in': allowed_roles}

		print "===== allowed_roles ===== "
		roles_is = allowed_roles if allowed_roles else "VAZIO"
		print allowed_roles, roles_is
		account = accounts.find_one(lookup) # Query here
		print account

		# workaround to block empty [] roles. Temporally implementation.
		# teorically this not needs.
		if account and 'roles' in account and len(account['roles']) == 0:
			abort(401, description="The action's user not have roles defined.")

		# set 'auth_field' value to owners documents.
		if account and '_id' in account:
			self.set_request_auth_value(account['_id'])
		return account and check_password_hash(account['password'], password)

# to export EVE_SETTING with path
# In the terminal:
# $ export EVE_SETTINGS=/path/to/settings/from/api/settings.py
EVE_SETTINGS = os.environ.get('EVE_SETTINGS')
app = Eve(auth=ApiBasicAuth, settings=EVE_SETTINGS)

# Adding hooks
app.on_pre_POST += users_hooks['username']


if __name__ == '__main__':
	app.run(threaded=True)
