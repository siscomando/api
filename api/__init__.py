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
# Features
# =========
# This application supports stream, messages, etc
# TODO: 1) Entender documents
# TODO: 2) DOCUMENTAR install, etc...
# TODO: 3) Documentar API like iugu.com
# TODO: 4) Document iugu-python

# -*- coding: utf-8 -*-
import os
from eve.auth import BasicAuth
from eve import Eve
from werkzeug.security import check_password_hash
from flask import abort
from pymongo import MongoClient
from bson import ObjectId
# app
from api.hooks import users_hooks
import settings

conn = MongoClient()
database = conn[settings.MONGO_DBNAME]

class ApiBasicAuth(BasicAuth):
	def check_auth(self, username, password, allowed_roles, resources, method):
		accounts = app.data.driver.db['user']
		lookup = {'email': username}

		if allowed_roles:
			# only retrieve a user if his roles match
			lookup['roles'] = {'$in': allowed_roles}

		print "===== allowed_roles ===== "
		roles_is = allowed_roles if allowed_roles else "VAZIO"
		print roles_is
		account = accounts.find_one(lookup) # Query here
		print account

		# workaround to block empty [] roles. Temporally implementation.
		# teorically this not needs.
		if account and 'roles' in account and len(account['roles']) == 0:
			abort(401, description="The action's user not have roles defined.")

		# set 'auth_field' value to owners documents.
		if account and '_id' in account:
			self.set_request_auth_value(account['_id'])

		if account:
			if check_password_hash(account['password'], password):
				return True
			else:
				abort(401,
				description="Please provide proper credentials (authentication)")
		else:
			# This will to raise: 'Please provide proper credentials'. That can
			# to be i. user not exists, ii. roles not macth or
			# iii. password invalid.
			return False

# to export EVE_SETTING with path
# In the terminal:
# $ export EVE_SETTINGS=/path/to/settings/from/api/settings.py
EVE_SETTINGS = os.environ.get('EVE_SETTINGS')
if EVE_SETTINGS is None:
	raise TypeError(u'Environment variable EVE_SETTINGS is not defined.' \
						'Please to define it.')
app = Eve(auth=ApiBasicAuth, settings=EVE_SETTINGS)

# Adding hooks
app.on_pre_POST_users += users_hooks['set_username']
app.on_post_POST_users += users_hooks['set_owner']

if __name__ == '__main__':
	app.run(threaded=True)
