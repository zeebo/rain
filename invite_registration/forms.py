from django import forms
from django.contrib.auth.models import User


class RegistrationForm(forms.Form):
  username = forms.CharField(max_length=20)
  password = forms.CharField(max_length=30, widget=forms.PasswordInput)
  password_again = forms.CharField(max_length=30, widget=forms.PasswordInput)
  
  def clean_username(self):
    username = self.cleaned_data['username']
    
    if User.objects.filter(username=username).exists():
      raise forms.ValidationError('Username is taken')
    
    if not username.isalnum():
      raise forms.ValidationError('Invalid username')
    
    return username
  
  def clean(self):
    cleaned_data = self.cleaned_data
    password = cleaned_data.get('password', None)
    password_again = cleaned_data.get('password_again', None)
    
    if password != password_again:
      raise forms.ValidationError('Passwords dont match')
    
    return cleaned_data