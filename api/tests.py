
import unittest
import requests
import json
import md5
from siscomando import models


MAX_RESULTS = 25

class ApiTests(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		# Creating superuser
		superuser = models.User()
		superuser.email = 'superuser@tests.com'
		superuser.password = '123'
		superuser.roles.append('superusers')
		superuser.save()
		cls.superuser = superuser
		# Creating ordinary user
		user = models.User()
		user.email = 'user@tests.com'
		user.password = '123'
		user.roles.append('users')
		user.save()
		cls.user = user

	@classmethod
	def tearDownClass(cls):
		cls.superuser.delete();
		cls.user.delete()


class UserTestCase(ApiTests):

	def setUp(self):
		self.host = 'http://localhost:9014'
		self.concat = lambda pr: "{}{}".format(self.host, pr)
		self.payload = {'email': 'mariolago@mm.com', 'password': '123'}

	def tearDown(self):
		try:
			u = models.User.objects.get(email=self.payload['email'])
			u.delete()
		except:
			pass # the user already deleted in someone test_method

	def test_get_users(self):
		# tests if returned lists is less than 25 items.
		r = requests.get('http://localhost:9014/api/v2/users')
		json_data = json.loads(r.text)
		data = json_data['_items']
		account = data[0]
		self.assertNotIn('password', account)
		self.assertLessEqual(len(data), 25)

	def test_get_item_users(self):
		""" tests gets item by HATEOAS (forward links) for users results."""
		r = requests.get('http://localhost:9014/api/v2/users')
		json_data = json.loads(r.text)
		data = json_data['_items']
		account = data[0]
		hateoas_link = account['_links']['self']['href']
		r = requests.get(self.concat(hateoas_link))
		json_data = json.loads(r.text)
		strip_url = hateoas_link.split('/')
		self.assertEqual(json_data['_id'], strip_url[-1])

	def test_get_users_next_page(self):
		# tests if exists more pages.
		r = requests.get('http://localhost:9014/api/v2/users')
		json_data = json.loads(r.text)
		links = json_data['_links']
		next_link = links['next']['href']
		r = requests.get(self.concat(next_link))
		json_data = json.loads(r.text)
		data = json_data['_items']
		self.assertGreaterEqual(len(data), 1)

	def test_get_users_last_page(self):
		# tests if exists more pages.
		r = requests.get('http://localhost:9014/api/v2/users')
		json_data = json.loads(r.text)
		links = json_data['_links']
		total = json_data['_meta']['total']
		next_link = links['last']['href']
		last_page = next_link.split('?')
		last_page = last_page[-1]
		last_page = int(last_page.split('=')[1])
		r = requests.get(self.concat(next_link))
		json_data = json.loads(r.text)
		data = json_data['_items']
		qtd_last_page = total - ((last_page - 1) * MAX_RESULTS)
		self.assertEqual(len(data), qtd_last_page)
	# POST tests
	def test_post_users_by_users(self):
		""" tests if user without superusers roles can to delete """
		payload = {'email': 'nobertogomes@mm.com', 'password': '123'}
		r = requests.post('http://localhost:9014/api/v2/users', data=payload)
		self.assertEqual(r.status_code, 401)

	def test_post_users_by_admins(self):
		""" to add admin user """
		pass

	def test_post_users_by_superusers(self):
		""" tests adds an user with roles of the superusers """
		# Adding the user
		r = requests.post('http://localhost:9014/api/v2/users',
			data=self.payload,
			auth=(self.superuser.email, '123'))
		self.assertEqual(r.status_code, 201)
	# DELETE tests
	def test_delete_users_by_users(self):
		""" trying delete an user as ordinary user """
		# Adding an user
		r = requests.post('http://localhost:9014/api/v2/users',
			data=self.payload,
			auth=(self.superuser.email, '123'))
		self.assertEqual(r.status_code, 201)
		# following links...
		json_data = json.loads(r.text)
		new_user_follow_url = json_data['_links']['self']['href']
		# deleting the user...
		r = requests.delete(self.concat(new_user_follow_url),
			auth=(self.user.email, '123'))
		print "=================="
		print r.text
		print "=================="
		self.assertEqual(r.status_code, 401)
		#r = requests.get(self.concat(new_user_follow_url))

	def test_delete_users_by_superusers(self):
		""" to delete by superuser with SOFT_DELETE=True"""

		# Adding an user
		r = requests.post('http://localhost:9014/api/v2/users',
			data=self.payload,
			auth=(self.superuser.email, '123'))
		json_data = json.loads(r.text)
		new_user_follow_url = json_data['_links']['self']['href']
		# Deleting the user
		r = requests.delete(self.concat(new_user_follow_url),
			auth=(self.superuser.email, '123'))
		self.assertEqual(r.status_code, 200)

	@unittest.skip(u'SOFT_DELETE not workint')
	def test_delete_SOFT_DELETE_users_by_superusers(self):
		""" to delete by superuser with SOFT_DELETE=True"""

		# Adding an user
		r = requests.post('http://localhost:9014/api/v2/users',
			data={'email':'mmmm@mm.com', 'password': '123'},
			auth=(self.superuser.email, '123'))
		json_data = json.loads(r.text)
		new_user_follow_url = json_data['_links']['self']['href']
		# Deleting the user
		r = requests.delete(self.concat(new_user_follow_url),
			auth=(self.superuser.email, '123'))
		# Check soft delete
		u = models.User.objects.get(email=self.payload['email'])
		print u
		self.assertEqual(r.status_code, 200)

	# PUT tests HERE
	def test_put_users_by_users(self):
		""" tests updates for users """
		# addding new user
		r = requests.post('http://localhost:9014/api/v2/users',
				data=self.payload, auth=(self.superuser.email, '123'))
		# editing user by other user, e.g: self.user
		print r.text
		json_data = json.loads(r.text)
		new_user_follow_url = json_data['_links']['self']['href']
		self.payload['first_name'] = "Mario"
		print "URL is:", self.concat(new_user_follow_url)
 		r = requests.patch(self.concat(new_user_follow_url),
 			data=self.payload, auth=(self.superuser.email, '123')) # the owner
 		print r.text

	# hooks tests
	def test_validate_email_is_not_valid(self):
		""" tests if email is not valid """
		# trying to add an user
		r = requests.post('http://localhost:9014/api/v2/users',
			data={'email':'mmmm-mmm.com', 'password': '123'},
			auth=(self.superuser.email, '123'))
		self.assertEqual(r.status_code, 500)

	def test_set_shortname(self):
		""" tests if shortname was created correctly """
		# trying to add an user
		r = requests.post('http://localhost:9014/api/v2/users',
			data=self.payload,
			auth=(self.superuser.email, '123'))
		# checking data
		json_data = json.loads(r.text)
		new_user_follow_url = json_data['_links']['self']['href']
		r = requests.get(self.concat(new_user_follow_url))
		shortname_save = json.loads(r.text)['shortname']
		shortname = self.payload['email'].split('@')[0]
		self.assertEqual(shortname, shortname_save)

	def test_set_password_is_not_plain_text(self):
		""" tests if password is not plain text """
		# trying to add an user
		r = requests.post('http://localhost:9014/api/v2/users',
			data=self.payload,
			auth=(self.superuser.email, '123'))
		json_data = json.loads(r.text)
		pk = json_data['_id']
		u = models.User.objects.get(pk=pk)
		self.assertNotEqual('123', u.password)

	def test_md5_email(self):
		""" tests if md5_email was created """
		# trying to add an user
		r = requests.post('http://localhost:9014/api/v2/users',
			data=self.payload,
			auth=(self.superuser.email, '123'))
		json_data = json.loads(r.text)
		new_user_follow_url = json_data['_links']['self']['href']
		r = requests.get(self.concat(new_user_follow_url))
		json_data = json.loads(r.text)
		md5_email = json_data['md5_email']
		self.assertEqual(md5_email, md5.md5(self.payload['email']).hexdigest())

	@unittest.skip(u"this isn't implemented")
	def test_token_generated(self):
		pass


class IssueTestCase(unittest.TestCase):

	# tests of the mongoengine hooks in models
	def test_register_normalized(self):
		pass

	def test_slugfy(self):
		pass

	def test_post_save(self):
		pass


class CommentTestCase(unittest.TestCase):

	# tests of the mongoengine hooks in models
	def test_set_shottime(self):
		pass

	def test_set_hashtags(self):
		pass

	def test_set_users_mentioned(self):
		pass

	def test_set_title(self):
		pass

	def test_post_save(self):
		pass

	def test_to_link_hashtag(self):
		pass

	def test_to_link_mention(self):
		pass

	@unittest.skip(u"This test is usefeul to webapp. The flow of the Eve skip it.")
	def test_to_json(self):
		pass

class InviteTestCase(unittest.TestCase):
	""" Invite is `yet` a case for `only` webapp. """
	pass


if __name__ == "__main__":
	unittest.main()
