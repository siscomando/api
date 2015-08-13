
import unittest
import requests
import json
import md5
import random
import base64
import datetime
import re
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash

# app

DATABASE = MongoClient()['dev_scdb']
MAX_RESULTS = 25

def generate_token(message):
	payload = {
		'u': message,
		'at': datetime.datetime.now(),
	}
	# simple for tests purpose.
	return base64.b64encode(md5.md5(bytes(payload)).hexdigest())

class ApiTests(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		conn = MongoClient()
		cls.database = conn['dev_scdb']
		# Add superuser
		cls.s = cls.database.user.insert({'email':'s@super.com',
		    'password': generate_password_hash('123'),
			'roles': ["superusers"],
			'token': generate_token('s@super.com')})
		# Add ordinary user
		cls.u = cls.database.user.insert({'email':'u@user.com',
					'password': generate_password_hash('123'),
					'roles': ["users"],
					'token': generate_token('u@user.com')})
		# simple join string to url
		host = 'http://localhost:9014/api/v2/'
		cls.concat = lambda cls, rp: "{}{}".format(host, rp) # rp = relative path
		cls.LOGIN_URL = "http://localhost:9010/login_api/"
		cls.get_token = lambda cls, token: base64.b64encode("{}:".format(token))
		# get token by POST in webapp (another host)
		def get_token_via_api(cls, identifier, password="123"):
			r = requests.post(cls.LOGIN_URL, json={"identifier": identifier,
				"password": password})
			token_64 = cls.get_token(json.loads(r.text)['message']['token'])
			return token_64
		cls.get_token_api = get_token_via_api

	@classmethod
	def tearDownClass(cls):
		cls.database.user.remove({'_id': cls.s});
		cls.database.user.remove({'_id': cls.u});


class UserTestCase(ApiTests):

	def setUp(self):
		number = random.randint(1, 10000)
		self.data = {'email': 'mariolago_{}@mm.com'.format(number),
						'password': '123', 'roles': ["users"]}

		def get_token_via_api(identifier, password="123"):
			r = requests.post(self.LOGIN_URL, json={"identifier": identifier,
				"password": password})
			token_64 = self.get_token(json.loads(r.text)['message']['token'])
			return token_64
		self.get_token_api = get_token_via_api

	def tearDown(self):
		# TODO: delete users created in the cases.
		pass

	def test_get_not_authenticated(self):
		""" tests to access API without is authenticated. """
		r = requests.get(self.concat('users'))
		self.assertEqual(r.status_code, 401)
		r = requests.post(self.concat('users'), json=self.data)
		self.assertEqual(r.status_code, 401)
		# adding simple user
		token = self.get_token_api('s@super.com', '123')
		r = requests.post(self.concat('users'), json=self.data,
			headers={"Authorization": "Basic {}".format(token)})
		self.assertEqual(r.status_code, 201)
		data = json.loads(r.text)
		# trying get item
		link = 'users/{}'.format(data['_id'])
		link_p = 'users/{}'.format(data['_id'])
		r = requests.get(self.concat(link))
		self.assertEqual(r.status_code, 401)
		link = 'me/{}'.format(data['_id'])
		r = requests.get(self.concat(link))
		self.assertEqual(r.status_code, 401)
		# patch on /me
		# r = requests.patch(self.concat(link), json={'first_name': 'Blue'})
		link = 'users/{}'.format(data['_id'])
		r = requests.get(self.concat(link),
			headers={"Authorization": "Basic {}".format(token)})
		data = json.loads(r.text)
		self.assertNotIn('first_name', data)
		# patch on /users
		r = requests.patch(self.concat(link_p), json={'first_name': 'Blue'})
		self.assertEqual(r.status_code, 405)

	def test_get_users(self):
		""" tests if returned lists is less than 25 items. Authentication is
		required.
		"""
		r = requests.get(self.concat('users'), auth=('u@user.com', '123'))
		self.assertEqual(r.status_code, 401)
		token = self.get_token_api('u@user.com', '123')
		r = requests.get(self.concat('users'),
				headers={"Authorization": "Basic {}".format(token)})
		json_data = json.loads(r.text)
		data = json_data['_items']
		account = data[0]
		self.assertNotIn('password', account)
		self.assertLessEqual(len(data), 25)

	def test_get_user_by_additional_lookup(self):
		# TODO: add an user before
		token = self.get_token_api('u@user.com', '123')
		r = requests.get(self.concat('users/horacioibrahim'),
				headers={"Authorization": "Basic {}".format(token)})
		self.assertEqual(r.status_code, 200)

	def test_get_item_users(self):
		""" tests to get item by HATEOAS (forward links) for users results."""
		token = self.get_token_api('u@user.com', '123')
		r = requests.get(self.concat('users'),
				headers={"Authorization": "Basic {}".format(token)})
		json_data = json.loads(r.text)
		data = json_data['_items']
		account = data[0]
		hateoas_link = account['_links']['self']['href']
		r = requests.get(self.concat(hateoas_link),
				headers={"Authorization": "Basic {}".format(token)})
		json_data = json.loads(r.text)
		strip_url = hateoas_link.split('/')
		self.assertEqual(json_data['_id'], strip_url[-1])

	def test_get_users_next_page(self):
		""" tests if exists next_link pages.
		"""
		token = self.get_token_api('u@user.com', '123')
		r = requests.get(self.concat('users'),
				headers={"Authorization": "Basic {}".format(token)})
		json_data = json.loads(r.text)
		links = json_data['_links']
		next_link = links['next']['href']
		r = requests.get(self.concat(next_link),
			headers={"Authorization": "Basic {}".format(token)})
		json_data = json.loads(r.text)
		data = json_data['_items']
		self.assertGreaterEqual(len(data), 1)

	def test_get_users_last_page(self):
		""" tests if exists last pages.
		NOTE: tests that need to check pagination require more than 25 items.
		"""
		go_this = True # skip or not this test.
		token = self.get_token_api('u@user.com', '123')
		r = requests.get(self.concat('users'),
			headers={"Authorization": "Basic {}".format(token)})
		json_data = json.loads(r.text)
		links = json_data['_links']
		total = json_data['_meta']['total']
		try:
			next_link = links['last']['href']
		except:
			# if has _links
			# if has _meta and total we can make it.
			go_this = False

		if go_this:
			last_page = next_link.split('?')
			last_page = last_page[-1]
			last_page = int(last_page.split('=')[1])
			r = requests.get(self.concat(next_link),
				headers={"Authorization": "Basic {}".format(token)})
			json_data = json.loads(r.text)
			data = json_data['_items']
			qtd_last_page = total - ((last_page - 1) * MAX_RESULTS)
			self.assertEqual(len(data), qtd_last_page)

	def test_get_me(self):
		""" Tests access in the /me """
		# adding user with users role
		token = self.get_token_api('s@super.com', '123')
		r = requests.post(self.concat('users'),
			headers={"Authorization": "Basic {}".format(token)},
			json=self.data)
		self.assertEqual(r.status_code, 201)
		# recently user go to access /me
		token = json.loads(r.text)['token']
		token_new = self.get_token(token)
		r = requests.get(self.concat('me'),
			headers={"Authorization": "Basic {}".format(token_new)})
		#print r.text
		data = json.loads(r.text)
		self.assertEqual(data['email'], self.data['email'])

	# PATCH tests
	def test_patch_me(self):
		""" tests changes in own user by /me.
		"""
		# adding user with users role
		token = self.get_token_api('s@super.com', '123')
		r = requests.post(self.concat('users'),
			headers={"Authorization": "Basic {}".format(token)},
			json=self.data)
		# recently user go to access /me
		user_id = json.loads(r.text)['_id']
		link = 'me/{}'.format(user_id)
		token = json.loads(r.text)['token']
		token_new = self.get_token(token)
		r = requests.patch(self.concat(link),
			headers={"Authorization": "Basic {}".format(token_new)},
			json={'first_name': 'Mario', 'last_name': 'Lago',
				'location': 'SUPGS/GSAUD/GSIAUI', 'avatar': 'http://uol.com.br/',
				})
		r = requests.get(self.concat('me'),
			headers={"Authorization": "Basic {}".format(token_new)})
		data = json.loads(r.text)
		self.assertEqual(data['first_name'], 'Mario')

	def test_patch_edit_another_user_by_me(self):
		""" tests changes in own user.
		"""
		seed = random.randint(1, 9993242)
		# adding user 1
		token = self.get_token_api('s@super.com', '123')
		r1 = requests.post(self.concat('users'),
			headers={"Authorization": "Basic {}".format(token)},
			json=self.data)
		# adding user 2
		r2 = requests.post(self.concat('users'),
			headers={"Authorization": "Basic {}".format(token)},
			json={'email': 'singleuser{}@user.com'.format(seed), 'password': '123',
				'roles':['users']})
		# recently user go to access /me
		user_id = json.loads(r1.text)['_id']
		link = 'me/{}'.format(user_id)
		# PATCH with id from r1 and accessing by r2 user.
		token = json.loads(r2.text)['token']
		token_new = self.get_token(token)
		r = requests.patch(self.concat(link),
			headers={"Authorization": "Basic {}".format(token_new)},
			json={'first_name': 'Mario'})
		# This must be 404 NOT FOUND
		self.assertEqual(r.status_code, 404)

	def test_patch_me_change_password(self):
		""" tests to change password. It's not allowed.
		TODO: put this in the webapp console.
		"""
		# addding new user
		token = self.get_token_api('s@super.com', '123')
		r = requests.post(self.concat('users'),
			headers={"Authorization": "Basic {}".format(token)},
			json=self.data)
		# editing user by other user, e.g: self.user
		json_data = json.loads(r.text)
		link = 'me/{}'.format(json_data['_id'])
		# changing
		token = json_data['token']
		token_new = self.get_token(token)
 		r = requests.patch(self.concat(link),
 			json={'password': '123'},
			headers={"Authorization": "Basic {}".format(token_new)}) # the owner
		self.assertEqual(r.status_code, 422)

	def test_patch_users_by_superusers(self):
		""" tests updates for users. Only own can change your data """
		# addding new user
		token = self.get_token_api('s@super.com', '123')
		r = requests.post(self.concat('users'),
			headers={"Authorization": "Basic {}".format(token)},
			json=self.data)
		# editing user by other user, e.g: self.user
		json_data = json.loads(r.text)
		object_id = json_data['_id']
		link = 'me/{}'.format(json_data['_id'])
		# Add/Editing first_name
		self.data['first_name'] = "Mario"
 		r = requests.patch(self.concat(link),
			json=self.data,
			headers={"Authorization": "Basic {}".format(token)})
		json_data = json.loads(r.text)
		self.assertEqual(r.status_code, 404)

	@unittest.skip("User cannot to edit own profile #monkeyFeature")
	def test_patch_owner(self):
		""" tests updates for users. Only by /me is possible change self data.
		"""
		# addding new user
		r = requests.post(self.concat('users'),
				json=self.data, auth=('s@super.com', '123'))
		# editing user by other user, e.g: self.user
		json_data = json.loads(r.text)
		new_user_follow_url = json_data['_links']['self']['href']
		# Add/Editing first_name
		self.data['first_name'] = "Myself Name"
		# Editing
 		r = requests.patch(self.concat(new_user_follow_url),
 			json=self.data, auth=(self.data['email'], '123'))
		# Get to check field first_name
 		r2 = requests.get(self.concat(new_user_follow_url),
 			auth=('u@user.com', '123'))
		json_data = json.loads(r2.text)
		self.assertEqual(r.status_code, 200)
		self.assertEqual(json_data['first_name'], self.data['first_name'])

	# POST tests
	def test_post_users_by_users(self):
		""" tests if user without superusers roles can to create new user """
		# without Auth
		r = requests.post(self.concat('users'), json=self.data)
		self.assertEqual(r.status_code, 401)
		# With auto
		token = self.get_token_api('u@user.com', '123')
		r = requests.post(self.concat('users'), json=self.data,
			headers={"Authorization": "Basic {}".format(token)})
		self.assertEqual(r.status_code, 401)

	@unittest.skip(u'not defined roles')
	def test_post_users_by_admins(self):
		""" to add admin user """
		pass

	def test_post_users_by_superusers(self):
		""" tests adds an user with roles of the superusers """
		# Adding the user
		token = self.get_token_api('s@super.com', '123')
		r = requests.post(self.concat('users'),
			headers={"Authorization": "Basic {}".format(token)},
			json=self.data)
		self.assertEqual(r.status_code, 201)
		json_data = json.loads(r.text)
		object_id = json_data['_id']
		new_user_follow_url = json_data['_links']['self']['href']
		# another test to check if isn't unique
		r = requests.post(self.concat('users'),
			json=self.data,
			headers={"Authorization": "Basic {}".format(token)})
		self.assertEqual(r.status_code, 422) # It's not unique
		# check if owner is updated
		token = self.get_token_api('u@user.com', '123')
		r = requests.get(self.concat(new_user_follow_url),
			headers={"Authorization": "Basic {}".format(token)})
		json_load = json.loads(r.text)
		self.assertEqual(json_load['owner'], object_id)

	# DELETE tests
	def test_delete_users_by_users(self):
		""" trying delete an user as ordinary user """
		# Adding an user
		token = self.get_token_api('s@super.com', '123')
		r = requests.post(self.concat('users'),
			headers={"Authorization": "Basic {}".format(token)},
			json=self.data)
		# following links...
		json_data = json.loads(r.text)
		new_user_follow_url = json_data['_links']['self']['href']
		# deleting the user as users...
		token = json_data['token']
		token = self.get_token(token)
		r = requests.delete(self.concat(new_user_follow_url),
			headers={"Authorization": "Basic {}".format(token)})
		self.assertEqual(r.status_code, 401)

	def test_delete_users_by_superusers(self):
		""" to delete by superuser with SOFT_DELETE=True"""
		# Adding an user
		token = self.get_token_api('s@super.com', '123')
		r = requests.post(self.concat('users'),
			headers={"Authorization": "Basic {}".format(token)},
			json=self.data)
		json_data = json.loads(r.text)
		new_user_follow_url = json_data['_links']['self']['href']
		# Deleting the user
		r = requests.delete(self.concat(new_user_follow_url),
			headers={"Authorization": "Basic {}".format(token)})
		r2 = requests.get(self.concat(new_user_follow_url),
			headers={"Authorization": "Basic {}".format(token)})
		self.assertEqual(r.status_code, 204)
		self.assertEqual(r2.status_code, 404)

	@unittest.skip(u'SOFT_DELETE not workint')
	def test_delete_SOFT_DELETE_users_by_superusers(self):
		""" to delete by superuser with SOFT_DELETE=True"""

		# Adding an user
		token = self.get_token_api('s@super.com', '123')
		r = requests.post(self.concat('users'),
			data={'email':'mmmm@mm.com', 'password': '123'},
			headers={"Authorization": "Basic {}".format(token)})
		json_data = json.loads(r.text)
		new_user_follow_url = json_data['_links']['self']['href']
		# Deleting the user
		r = requests.delete(self.concat(new_user_follow_url),
			headers={"Authorization": "Basic {}".format(token)})
		# Check soft delete
		u = models.User.objects.get(email=self.payload['email'])
		self.assertEqual(r.status_code, 200)

	# hooks tests
	def test_validate_email_is_not_valid(self):
		""" tests if email is not valid """
		# trying to add an user
		token = self.get_token_api('s@super.com', '123')
		r = requests.post(self.concat('users'),
			json={'email':'mmmm-mmm-m3.com', 'password': '123'},
			headers={"Authorization": "Basic {}".format(token)})
		self.assertEqual(r.status_code, 422)

	def test_set_username(self):
		""" tests if username was created correctly.
		`shortname` is deprecated. It's now `username`
		"""
		# trying to add an user
		token = self.get_token_api('s@super.com', '123')
		r = requests.post(self.concat('users'), json=self.data,
			headers={"Authorization": "Basic {}".format(token)})
		# checking data
		json_data = json.loads(r.text)
		new_user_follow_url = json_data['_links']['self']['href']
		token = self.get_token(json_data['token'])
		r = requests.get(self.concat(new_user_follow_url),
			headers={"Authorization": "Basic {}".format(token)})
		username_saved = json.loads(r.text)['username']
		username_sent = self.data['email'].split('@')[0].replace('.', '')
		self.assertEqual(username_sent, username_saved)

	def test_set_password_is_not_plain_text(self):
		""" tests if password is not plain text """
		# trying to add an user
		token = self.get_token_api('s@super.com', '123')
		r = requests.post(self.concat('users'), json=self.data,
			headers={"Authorization": "Basic {}".format(token)})
		json_data = json.loads(r.text)
		pk = json_data['_id']
		u = DATABASE.user.find_one({'_id': ObjectId(pk)})
		password = u['password']
		self.assertNotEqual('123', password)
		self.assertTrue(password.startswith('pbkdf2'))

	def test_md5_email(self):
		""" tests if md5_email was created """
		# trying to add an user
		token = self.get_token_api('s@super.com', '123')
		r = requests.post(self.concat('users'),
			json=self.data,
			headers={"Authorization": "Basic {}".format(token)})
		json_data = json.loads(r.text)
		new_user_follow_url = json_data['_links']['self']['href']
		token = self.get_token(json_data['token'])
		r = requests.get(self.concat(new_user_follow_url),
			headers={"Authorization": "Basic {}".format(token)})
		json_data = json.loads(r.text)
		md5_email = json_data['md5_email']
		self.assertEqual(md5_email, md5.md5(self.data['email']).hexdigest())

	@unittest.skip(u"this isn't implemented")
	def test_token_generated(self):
		pass


class IssueTestCase(ApiTests):

	def setUp(self):
		number = random.randint(1, 10000)
		self.data = {'email': 'marioissues_{}@mm.com'.format(number),
						'password': '123', 'roles': ["users"]}
		self.issue = {
			'title': 'SISCOMEX',
			'body': 'Lentidao no siscomex',
			'register': '2015RI/000{}'.format(number),
			'ugat': 'SUPOP',
			'ugser': 'SUNAF'
		}
		self.user_token = self.get_token_api('u@user.com', '123')
		self.super_token = self.get_token_api('s@super.com', '123')

	def test_get_issues_not_authenticated(self):
		r = requests.get(self.concat('issues'))
		self.assertEqual(r.status_code, 401)

	def test_get_issues(self):
		""" tests get issues and if is list """
		r = requests.get(self.concat('issues'),
			headers={"Authorization": "Basic {}".format(self.user_token)})

		data = json.loads(r.text)
		data = data['_items']
		self.assertEqual(r.status_code, 200)
		self.assertEqual(list, type(data))

	def test_get_more_issues(self):
		"""tests get issues and if there is next the first `_items` must contain
		25 items.
		"""
		r = requests.get(self.concat('issues'),
			headers={"Authorization": "Basic {}".format(self.user_token)})
		data = json.loads(r.text)
		items = data['_items']
		if 'next' in data['_links']:
			self.assertEqual(len(items), 25)
			# testing more pages
			link = data['_links']['next']['href']
			r = requests.get(self.concat(link),
				headers={"Authorization": "Basic {}".format(self.user_token)})
			data = json.loads(r.text)
			items = data['_items']
			meta = data['_meta']
			self.assertEqual(list, type(items))
			self.assertEqual(meta['page'], 2)
		else:
			# this tests is possible if there is data volume or more than
			# 25 items.
			pass

	# tests of the hooks
	def test_register_normalized(self):
		""" tests if resgisters will be normalized and copy data to
		register_orig.
		"""
		# adding register
		r = requests.post(self.concat('issues'),
			headers={"Authorization": "Basic {}".format(self.super_token)},
			json=self.issue)
		data = json.loads(r.text)
		link = 'issues/{}'.format(data['_id'])
		r = requests.get(self.concat(link),
			headers={"Authorization": "Basic {}".format(self.user_token)})

		data = json.loads(r.text)
		self.assertNotIn('/', data['register'])
		self.assertEqual(self.issue['register'], data['register_orig'])

	def test_register_create_bulk(self):
		""" tests to create multiple items (bulk).
		"""
		number = random.randint(1, 10000)
		reg_1 = '2015RI/000{}'.format(number + 1)
		reg_2 = '2015RI/000{}'.format(number + 2)
		reg_3 = '2015RI/000{}'.format(number + 3)
		# adding register
		issues = [self.issue,
				{'title': 'Sisc1', 'body':'Fora', 'register': reg_1,
						'ugat': 'SUPOP', 'ugser': 'SUNAF'},
				{'title': 'Sisc2', 'body':'Fora', 'register': reg_2,
						'ugat': 'SUPOP', 'ugser': 'SUNAF'},
				{'title': 'Sisc3', 'body':'Fora', 'register': reg_3,
						'ugat': 'SUPOP', 'ugser': 'SUNAF'}
		]
		r = requests.post(self.concat('issues'),
			headers={"Authorization": "Basic {}".format(self.super_token)},
			json=issues)
		data = json.loads(r.text)
		self.assertEqual(len(data['_items']), 4)

	def test_update_issue(self):
		""" tests to update issue
		"""
		# adding issue
		r = requests.post(self.concat('issues'),
			headers={"Authorization": "Basic {}".format(self.super_token)},
			json=self.issue)
		self.assertEqual(r.status_code, 201)
		data = json.loads(r.text)
		link = 'issues/{}'.format(data['_id'])

		r = requests.patch(self.concat(link),
			headers={"Authorization": "Basic {}".format(self.super_token)},
			json={'title': 'A new title'})
		self.assertEqual(r.status_code, 200)

		r = requests.get(self.concat(link),
			headers={"Authorization": "Basic {}".format(self.user_token)})
		self.assertEqual(r.status_code, 200)

		data = json.loads(r.text)
		self.assertEqual(data['title'], 'A new title')

	def test_get_with_grouped(self):
		r = requests.get(self.concat('issues?grouped=1&max_results=1'),
		    headers={"Authorization": "Basic {}".format(self.super_token)})
		self.assertEqual(200, r.status_code)
		data = json.loads(r.text)
		self.assertIsInstance(data['_grouped'], list)
		self.assertEqual(len(data['_grouped'][0].keys()), 2)

	def test_update_and_create_not_superusers(self):
		# TODO
		pass

	def test_slugfy(self):
		# TODO
		pass

	def test_post_save(self):
		""" tests events stream. """
		# TODO
		pass


class CommentTestCase(ApiTests):

	def setUp(self):
		number = random.randint(1, 10000)
		self.data = {'email': 'marioissues_{}@mm.com'.format(number),
						'password': '123', 'roles': ["users"]}
		self.minimal_comment = {
			'body': 'Any data for only sample. {}'.format(number),
			# hashtag or issue_id or title
			'title': '#SimulatedHashtag'
		}

		self.user_token = self.get_token_api('u@user.com', '123')
		self.super_token = self.get_token_api('s@super.com', '123')

	# tests for users (POST, PATCH)
	def test_post_comment(self):
		""" tests create a comment and minimal fields are correct.
		"""
		r = requests.post(self.concat('comments/new'),
			headers={"Authorization": "Basic {}".format(self.user_token)},
			json=self.minimal_comment)
		data = json.loads(r.text)
		self.assertEqual(r.status_code, 201)
		self.assertEqual(data['author']['_id'], str(self.u))
		self.assertEqual(data['body'], self.minimal_comment['body'])
		self.assertEqual(data['title'], 'no subject')
		self.assertIn('created_at', data)
		self.assertIn('updated_at', data)

	def test_post_with_hashtag(self):
		# add new comment
		self.minimal_comment['body'] += " #TagNew"
		r = requests.post(self.concat('comments/new'),
			headers={"Authorization": "Basic {}".format(self.user_token)},
			json=self.minimal_comment)
		data = json.loads(r.text)
		self.assertEqual(r.status_code, 201)
		self.assertIn('hashtags', data)
		self.assertEqual(len(data['hashtags']), 1)

	def test_post_with_multiple_hashtag(self):
		# add new comment
		self.minimal_comment['body'] += " #TagNew continue #Breve"
		r = requests.post(self.concat('comments/new'),
			headers={"Authorization": "Basic {}".format(self.user_token)},
			json=self.minimal_comment)
		data = json.loads(r.text)
		self.assertEqual(r.status_code, 201)
		self.assertIn('hashtags', data)
		self.assertEqual(len(data['hashtags']), 2)

	def test_embedded_or_expanded_reference(self):
		""" tests query comment with embedded parameter.
		"""
		# add a minimal comment
		r = requests.post(self.concat('comments/new'),
			headers={"Authorization": "Basic {}".format(self.user_token)},
			json=self.minimal_comment)
		# get with embedded
		link = 'comments?embedded={"author":1}'
		r = requests.get(self.concat(link),
			headers={"Authorization": "Basic {}".format(self.user_token)})
		# check if author is expanded
		data = json.loads(r.text)
		item = data['_items'][0]
		self.assertEqual(item['author']['email'], 'u@user.com')
		self.assertIn('roles', item['author'])
		self.assertNotIn('password', item['author'])

	def test_embedded_or_expanded_reference_with_issue(self):
		""" tests query comment with embedded parameter.
		"""
		number = random.randint(1, 10000)
		register = '2015RI/000{}'.format(number + 1)
		# adding register
		issue = {'title': 'Sisc1', 'body':'Fora', 'register': register,
					'ugat': 'SUPOP', 'ugser': 'SUNAF'}
		r = requests.post(self.concat('issues'),
			headers={"Authorization": "Basic {}".format(self.super_token)},
			json=issue)
		data = json.loads(r.text)
		self.assertEqual(r.status_code, 201)
		issue_id = data['_id']
		self.minimal_comment['issue'] = issue_id
		# add a minimal comment
		r = requests.post(self.concat('comments/new'),
			headers={"Authorization": "Basic {}".format(self.user_token)},
			json=self.minimal_comment)
		# get with embedded
		item_id = json.loads(r.text)['_id']
		link = 'comments/%s?embedded={"issue":1}' % item_id
		r = requests.get(self.concat(link),
			headers={"Authorization": "Basic {}".format(self.user_token)})
		# check if author is expanded
		#print r.text
		item = json.loads(r.text)
		self.assertEqual(item['issue']['_id'], issue_id)
		self.assertIn('body', item['issue'])
		self.assertIn('register', item['issue'])
		self.assertIn('ugat', item['issue'])
		self.assertIn('ugser', item['issue'])

	@unittest.skip('to run alone')
	def test_get_sorting(self):
		""" tests if comments are returned in DESC order.
		"""
		# add new comment
		r = requests.post(self.concat('comments/new'),
			headers={"Authorization": "Basic {}".format(self.user_token)},
			json=self.minimal_comment)
		self.assertEqual(r.status_code, 201)
		# get all comments
		r = requests.get(self.concat('comments'),
			headers={"Authorization": "Basic {}".format(self.user_token)})
		data = json.loads(r.text)
		item = data['_items'][0]
		self.assertEqual(item['body'], self.minimal_comment['body'])

	def test_get_comments_tags(self):
		""" tests resource comments_hashtag
		"""
		self.minimal_comment['body'] += ' #TestHash'
		# add comment
		r = requests.post(self.concat('comments/new'),
			headers={"Authorization": "Basic {}".format(self.user_token)},
			json=self.minimal_comment)
		# get comment
		r = requests.get(self.concat('comments?hashtag=TestHash'),
					headers={"Authorization": "Basic {}".format(self.user_token)})
		data = json.loads(r.text)
		self.assertGreaterEqual(len(data['_items']), 1)

	def test_edit_comments(self):
		""" tests edit a comment
		"""
		# adding to get _id
		new_edited_body = "Edited body lol. It's beautiful!"
		r = requests.post(self.concat('comments/new'),
			headers={"Authorization": "Basic {}".format(self.user_token)},
			json=self.minimal_comment)
		data = json.loads(r.text)
		link = 'comments/edit/{}'.format(data['_id'])
		self.minimal_comment['body'] = new_edited_body
		r = requests.patch(self.concat(link),
			headers={"Authorization": "Basic {}".format(self.user_token)},
			json=self.minimal_comment)
		# Get is better
		link = 'comments/{}'.format(data['_id'])
		r = requests.get(self.concat(link),
			headers={"Authorization": "Basic {}".format(self.user_token)})
		data = json.loads(r.text)
		self.assertEqual(new_edited_body, data['body'])

	def test_edit_comments_change_author(self):
		""" tests if not changed author
		"""
		# adding to get _id
		new_edited_body = "Edited body lol. It's beautiful!"
		r = requests.post(self.concat('comments/new'),
			headers={"Authorization": "Basic {}".format(self.user_token)},
			json=self.minimal_comment)
		data = json.loads(r.text)
		author = data['author']
		link = 'comments/edit/{}'.format(data['_id'])
		self.minimal_comment['body'] = new_edited_body
		self.minimal_comment['author'] = "maluco"
		r = requests.patch(self.concat(link),
			headers={"Authorization": "Basic {}".format(self.user_token)},
			json=self.minimal_comment)
		# author is not permitted to be edited
		self.assertEqual(r.status_code, 422)

	# tests hooks
	def test_set_shottime_without_issue_or_register(self):
		r = requests.post(self.concat('comments/new'),
			headers={"Authorization": "Basic {}".format(self.user_token)},
			json=self.minimal_comment)
		data = json.loads(r.text)
		hour = "".join([str(datetime.datetime.now().hour), 'h'])
		self.assertEqual(hour, data['shottime'])

	def test_set_shottime_with_issue_or_register(self):
		# add and issue
		number = random.randint(1, 10000)
		reg_1 = '2015RI/000{}'.format(number + 1)
		# adding register
		issue = {'title': 'Sisc1',
				'body':'Fora',
				'register': reg_1,
				'ugat': 'SUPOP',
				'ugser': 'SUNAF'
		}
		r = requests.post(self.concat('issues'),
			headers={"Authorization": "Basic {}".format(self.super_token)},
			json=issue)
		self.assertEqual(r.status_code, 201)
		issue = json.loads(r.text)
		# edit minimal_comment
		self.minimal_comment['issue'] = issue['_id']
		r = requests.post(self.concat('comments/new'),
			headers={"Authorization": "Basic {}".format(self.user_token)},
			json=self.minimal_comment)
		data = json.loads(r.text)
		shottime = int(data['shottime'])
		self.assertTrue(isinstance(shottime, int))
		self.assertLessEqual(shottime, 2)

	@unittest.skip("waiting define if a or sc-link")
	def test_set_hashtags_one_tag(self):
		# to prevent title definition
		del self.minimal_comment['title']
		self.minimal_comment['body'] += " #TagNew"
		# add new comment without title
		r = requests.post(self.concat('comments/new'),
			headers={"Authorization": "Basic {}".format(self.user_token)},
			json=self.minimal_comment)
		self.assertIn('<a', r.text) # sc-link
		self.assertIn('</a>', r.text)
		self.assertEqual(r.status_code, 201)

	@unittest.skip(u'waiting define if a or sc-link')
	def test_set_hashtags_multiple_tag(self):
		# to prevent title definition
		preg1 = re.compile(r'<a(.*)>#TagNew</a>')
		preg2 = re.compile(r'<a(.*)>#MoreTag</a>')
		preg3 = re.compile(r'<a(.*)>#EndTag</a>')
		del self.minimal_comment['title']
		self.minimal_comment['body'] += " #TagNew text and #MoreTag #EndTag"
		# add new comment without title
		r = requests.post(self.concat('comments/new'),
			headers={"Authorization": "Basic {}".format(self.user_token)},
			json=self.minimal_comment)
		data = json.loads(r.text)
		self.assertEqual(len(re.findall(preg1, data['body'])), 1)
		self.assertEqual(len(re.findall(preg2, data['body'])), 1)
		self.assertEqual(len(re.findall(preg3, data['body'])), 1)
		self.assertEqual(r.status_code, 201)

	# DELETE with auth_field is a feature of the Eve.

	def test_set_users_mentioned(self):
		pass

	def test_set_title_with_hashtag(self):
		""" when creating a comment with hashtag but without issue_id the
		first hashtag must be the title.
		"""
		# create an issue.
		number = random.randint(1, 10000)
		reg_1 = '2015RI/000{}'.format(number + 1)
		# adding register
		issue = {'title': 'Sisc1',
				'body':'Fora',
				'register': reg_1,
				'ugat': 'SUPOP',
				'ugser': 'SUNAF'
		}
		r = requests.post(self.concat('issues'),
			headers={"Authorization": "Basic {}".format(self.super_token)},
			json=issue)
		self.assertEqual(r.status_code, 201)
		# create an comment with hashtag in body but without issue or register.
		del self.minimal_comment['title'] # surely that title wasn't posted.
		self.minimal_comment['body'] += " #TestHashNew"
		r = requests.post(self.concat('comments/new'),
			headers={"Authorization": "Basic {}".format(self.user_token)},
			json=self.minimal_comment)
		data = json.loads(r.text)
		self.assertEqual(data['title'], "#TestHashNew")

	def test_set_title_with_register(self):
		""" tests if title of comment is equal from register.
		"""
		# create an issue.
		number = random.randint(1, 10000)
		reg_1 = '2015RI/000{}'.format(number + 1)

		# adding register
		issue = {'title': 'SISC ISSUE VALID',
				'body':'Fora',
				'register': reg_1,
				'ugat': 'SUPOP',
				'ugser': 'SUNAF'
		}

		# adding an valid issue
		r = requests.post(self.concat('issues'),
			headers={"Authorization": "Basic {}".format(self.super_token)},
			json=issue)
		self.assertEqual(r.status_code, 201)

		# surely that title wasn't posted.
		del self.minimal_comment['title']

		# adding issue `_id` for comment.
		self.minimal_comment['issue'] = json.loads(r.text)['_id']

		# creating the comment with issue.
		r = requests.post(self.concat('comments/new'),
			headers={"Authorization": "Basic {}".format(self.user_token)},
			json=self.minimal_comment)
		self.assertEqual(r.status_code, 201) # fail fast

		data = json.loads(r.text)
		register = issue['register'].replace('/', '')
		# title of comment must be equal from register.
		self.assertEqual(data['title'], issue['title'])

	def test_post_save(self):
		pass

	def test_to_link_hashtag(self):
		pass

	def test_to_link_mention(self):
		pass

	@unittest.skip(u"This test is useful for webapp. The flow of the Eve skip it.")
	def test_to_json(self):
		pass

class StarsTestCase(ApiTests):

	def setUp(self):
		number = random.randint(1, 10000)
		self.data = {'email': 'marioissues_{}@mm.com'.format(number),
						'password': '123', 'roles': ["users"]}

		self.user_token = self.get_token_api('u@user.com', '123')
		self.super_token = self.get_token_api('s@super.com', '123')

		self.minimal_comment = {
			'body': 'Any data for only sample. {}'.format(number),
			# hashtag or issue_id or title
			'title': '#SimulatedHashtag'
		}
		# create a comment
		r = requests.post(self.concat('comments/new'),
			headers={"Authorization": "Basic {}".format(self.user_token)},
			json=self.minimal_comment)
		self.comment_created = json.loads(r.text)


	def test_create_stars(self):
		"""
		tests if can to post/votes in stars
		"""
		data_stars = {
			'comment': self.comment_created['_id'],
			'score': 2
		}
		r = requests.post(self.concat('stars/new'),
		 	headers={"Authorization": "Basic {}".format(self.user_token)},
			json=data_stars
		)
		self.assertEqual(r.status_code, 201)


class InviteTestCase(unittest.TestCase):
	""" Invite is `yet` a case for `only` webapp. """
	pass


if __name__ == "__main__":
	unittest.main()
