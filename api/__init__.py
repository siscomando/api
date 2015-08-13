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

# -*- coding: utf-8 -*-
import os
from eve.auth import TokenAuth
from eve import Eve
from flask import abort
from pymongo import MongoClient
from bson import ObjectId
# app
from api.hooks import (users_hooks, before_returning_items_from_me,
		before_on_insert_issue, before_get_comments_hashtags,
		before_on_insert_comments, post_post_comments_new, before_on_insert_users,
		after_inserted_stars_user, on_post_get_issues_with_grouped,
		before_get_comments_search, before_get_users_search
	)
import settings

conn = MongoClient()
database = conn[settings.MONGO_DBNAME]

class ApiTokenAuth(TokenAuth):
	def check_auth(self, token, allowed_roles, resource, method):
		""" Token must be passed as base64
		Authorization: Basic token_base64_ended_common

		Example:
		token = 'message'
		signature = base64.b64encode(token + ':')
		"""
		accounts = app.data.driver.db['user']
		lookup = {'token': token}
		if allowed_roles:
			# only retrieve a user if his roles match
			lookup['roles'] = {'$in': allowed_roles}

		account = accounts.find_one(lookup) # Query here
		# workaround to block empty [] roles. Temporally implementation.
		# teorically this not needs.
		if account and 'roles' in account and len(account['roles']) == 0:
			abort(401, description="The action's user not have roles defined.")

		# set 'auth_field' value to owners documents.
		if account and '_id' in account:
			self.set_request_auth_value(account['_id'])

		if account:
			return True
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

app = Eve(auth=ApiTokenAuth, settings=EVE_SETTINGS)

#################### Adding hooks #####################
# hooks on_fetched_resource_me HTTP events
#app.on_pre_GET_me += users_hooks['get_authenticated']
app.on_pre_GET_comments += before_get_comments_hashtags
app.on_pre_GET_comments += before_get_comments_search
app.on_pre_GET_users += before_get_users_search
app.on_pre_POST_users += users_hooks['set_username']
app.on_post_POST_users += users_hooks['set_owner']
app.on_post_POST_comments_user += post_post_comments_new

# test this implementation:
app.on_post_GET_issues += on_post_get_issues_with_grouped

# hooks on database events
app.on_fetched_resource_me += before_returning_items_from_me
# app.on_fetched_resource_comments += after_fetched_comments
app.on_insert_issues += before_on_insert_issue
app.on_insert_comments_user += before_on_insert_comments # pre
app.on_insert_users += before_on_insert_users
app.on_inserted_stars_user += after_inserted_stars_user

if __name__ == '__main__':
	app.run(threaded=True)
