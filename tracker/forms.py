from django import forms
from models import Peer

class PeerForm(forms.ModelForm):
  class Meta:
    model = Peer
  
  def clean_port(self):
    port = self.cleaned_data['port']
    
    if port < 1 or port > 65535:
      raise forms.ValidationError('Port not in the correct range')
    
    return port