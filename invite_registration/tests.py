from django.test import TestCase
from django.contrib.auth.models import User
from models import Invite

class RegistrationTest(TestCase):
  fixtures = ['users.json', 'invites.json']
  urls = 'invite_registration.urls'
  
  def test_invalid_hash_code(self):
    response = self.client.get('/register?code=invalid_code')
    self.assertContains(response, 'invalid hash code', status_code=200)

  def test_valid_hash_code(self):
    response = self.client.get('/register?code=147037894a14f44e671ed54943ff09976a4c17f5')
    self.assertNotContains(response, 'invalid hash code', status_code=200)
    
    response = self.client.get('/register?code=ba130a1044f5691ff161df941db99fe796460438')
    self.assertNotContains(response, 'invalid hash code', status_code=200)
  
  def test_inactive_hash_code(self):
    response = self.client.get('/register?code=a024097620dad62218b7b8351c0e659618f57189')
    self.assertContains(response, 'invalid hash code', status_code=200)
  
  def test_user_created(self):
    response = self.client.post('/register?code=ba130a1044f5691ff161df941db99fe796460438',
                                data={'username':'newuser', 'password':'lol', 'password_again':'lol'})
    
    try:
      obj = User.objects.get(username='newuser')
    except User.DoesNotExist:
      raise self.failureException('User not created')
    
    self.assertRedirects(response, obj.get_absolute_url(), target_status_code=200)
    
    invite = Invite.objects.get(hash_code='ba130a1044f5691ff161df941db99fe796460438')
    
    self.assertEquals(invite.active, False)
    self.assertEquals(invite.child, obj)
    
    response = self.client.get('/register?code=ba130a1044f5691ff161df941db99fe796460438')
    self.assertContains(response, 'invalid hash code', status_code=200)
  
  def test_passwords_match(self):
    response = self.client.post('/register?code=ba130a1044f5691ff161df941db99fe796460438',
                                data={'username':'newuser', 'password':'lol', 'password_again':'lol2'})
    
    self.assertContains(response, 'Passwords dont match', status_code=200)
  
  def test_username_taken(self):
    response = self.client.post('/register?code=ba130a1044f5691ff161df941db99fe796460438',
                                data={'username':'zeebo', 'password':'lol', 'password_again':'lol'})
    
    self.assertContains(response, 'Username is taken', status_code=200)

