from django import forms
from django.core import validators
from django.contrib.auth.models import User


class RegistrationForm(forms.Form):
  username = forms.CharField(max_length=20)
  password = forms.PasswordField(max_length=30)
  password_again = forms.PasswordField(max_length=30)
  
  def clean_username(self):
    username = self.cleaned_data['username']
    
    if User.objects.get(username=username).exists():
      return forms.ValidationError('Username is taken')
    
    if not username.isalnum():
      return forms.ValidationError('Invalid username')
    
    return username
  
  def clean(self):
    cleaned_data = self.cleaned_data
    password = cleaned_data['password']
    password_again = cleaned_data['password_again']
    
    if password != password_again:
      return forms.ValidationError('Passwords dont match')
    
    return cleaned_data