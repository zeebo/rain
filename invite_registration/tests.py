from django.test import TestCase

class RegistrationTest(TestCase):
  fixtures = ['users.json', 'invites.json']
  def test_invalid_reg_code(self):
    response = self.client.get('')

