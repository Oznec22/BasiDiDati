from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Autore, FumettoPunta, Prodotto, Firmacopie, CasaEditrice, Stand, Profile

class RegistrazioneForm(UserCreationForm):
    email = forms.EmailField(required=True)
    ruolo = forms.ChoiceField(choices=[
        ('utente', 'Utente'),
        ('autore', 'Autore'),
        ('casa_editrice', 'Casa Editrice'),
    ])

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'ruolo']



class AutoreForm(forms.ModelForm):
    class Meta:
        model = Autore
        fields = ['bio']

class FumettoPuntaForm(forms.ModelForm):
    class Meta:
        model = FumettoPunta
        fields = ['autore', 'fumetto']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Popola solo i fumetti dell'autore selezionato (se presente)
        if 'autore' in self.initial and self.initial['autore']:
            autore_id = self.initial['autore']
            self.fields['fumetto'].queryset = Fumetto.objects.filter(autore_id=autore_id)
        else:
            self.fields['fumetto'].queryset = Fumetto.objects.none()


class ProdottoForm(forms.ModelForm):
    class Meta:
        model = Prodotto
        fields = ['titolo', 'prezzo']





class EventoForm(forms.ModelForm):
    class Meta:
        model = Firmacopie
        fields = ['fumetto', 'autore', 'stand', 'data', 'ora', 'descrizione']

    def __init__(self, *args, **kwargs):
        autori = kwargs.pop('autori', None)
        prodotti = kwargs.pop('prodotti', None)
        stands = kwargs.pop('stands', None)
        super().__init__(*args, **kwargs)

        if autori:
            self.fields['autore'].queryset = autori
        if prodotti:
            self.fields['fumetto'].queryset = prodotti
        if stands:
            self.fields['stand'].queryset = stands


class CasaEditriceForm(forms.ModelForm):
    class Meta:
        model = CasaEditrice
        fields = ['nome', 'manager']


class CasaEditriceAutoriForm(forms.ModelForm):
    autori = forms.ModelMultipleChoiceField(
        queryset=Autore.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = CasaEditrice
        fields = ['autori']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['user', 'ruolo']  # use the actual fields in Profile


class StandForm(forms.ModelForm):
    class Meta:
        model = Stand
        fields = ['nome', 'padiglione', 'disponibile']