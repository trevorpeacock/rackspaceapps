import unittest
from base64 import b64encode
from datetime import datetime
from hashlib import sha1
from rackspaceapps import RackspaceApps


class TestRackspaceApps(unittest.TestCase):

    def setUp(self):
        self.test_user_key = 'test'
        self.test_secret_key = 'test'
        self.rsa = RackspaceApps(user_key=self.test_user_key,
                                 secret_key=self.test_secret_key)

    def test_credentials(self):
        self.assertEqual(self.rsa._user_key, self.test_user_key)
        self.assertEqual(self.rsa._secret_key, self.test_secret_key)

    def test_build_resource(self):
        resource = ('test',)
        expected = 'https://api.emailsrvr.com/v1/test'
        self.assertEqual(self.rsa._build_resource(resource), expected)

    def test_build_signature(self):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        test_data = self.rsa._user_key.encode()
        test_data += self.rsa.USER_AGENT.encode()
        test_data += timestamp.encode()
        test_data += self.rsa._secret_key.encode()
        signature = b64encode(sha1(test_data).digest()).decode()
        expected = '{}:{}:{}'.format(self.rsa._user_key, timestamp, signature)
        self.assertEqual(self.rsa._build_signature(), expected)

    def test_build_session(self):
        session = self.rsa._build_session()
        self.assertEqual(session.headers.get('User-Agent'),
                         self.rsa.USER_AGENT)
        self.assertEqual(session.headers.get('Accept'), 'application/json')
        self.assertTrue('X-Api-Signature' in session.headers)

    def test_request(self):
        resource = ('test',)
        request = self.rsa._request(resource)
        for method in ('get', 'put', 'post', 'delete'):
            self.assertTrue(getattr(request, method, False))
        self.assertFalse(getattr(request, 'patch', False))
