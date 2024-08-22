from django import forms
from .models import Ativo

class AtivoForm(forms.ModelForm):
    class Meta:
        model = Ativo
        fields = ['nome', 'parametro_tunel', 'periodicidade', 'email_investidor']
