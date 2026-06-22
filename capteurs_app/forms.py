from django import forms
from .models import Capteur


class CapteurEditForm(forms.ModelForm):
    class Meta:
        model = Capteur
        fields = ['nom', 'emplacement']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-input'}),
            'emplacement': forms.TextInput(attrs={'class': 'form-input'}),
        }
        labels = {
            'nom': 'Nom',
            'emplacement': 'Emplacement',
        }
