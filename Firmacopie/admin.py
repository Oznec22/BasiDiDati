# admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django import forms
from .models import (
    Profile, CasaEditrice, Prodotto, Autore, Fumetto, Stand,
    Firmacopie, PrenotazioneFirmacopie, DisponibilitaAutore, FumettoPunta,
)

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profiles'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register([Prodotto, PrenotazioneFirmacopie, DisponibilitaAutore, FumettoPunta])

@admin.register(Stand)
class StandAdmin(admin.ModelAdmin):
    list_display = ('nome', 'padiglione', 'disponibile')
    list_filter = ('disponibile', 'padiglione')

@admin.register(CasaEditrice)
class CasaEditriceAdmin(admin.ModelAdmin):
    list_display = ('nome', 'manager')



class FumettoPuntaInline(admin.StackedInline):
    model = FumettoPunta
    extra = 0
    can_delete = False
    max_num = 1

@admin.register(Autore)
class AutoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'casa_editrice', 'fumetto_punta')

    inlines = [FumettoPuntaInline]

    def fumetto_punta(self, obj):
        try:
            punta = FumettoPunta.objects.get(autore=obj)
            return punta.fumetto.titolo
        except FumettoPunta.DoesNotExist:
            return "—"
        except FumettoPunta.MultipleObjectsReturned:
            return "Errore: più fumetti punta"


class FirmacopieForm(forms.ModelForm):
    class Meta:
        model = Firmacopie
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        autore = None
        if self.instance and self.instance.autore_id:
            autore = self.instance.autore_id
        elif 'autore' in self.initial:
            autore = self.initial.get('autore')

        if autore:
            self.fields['fumetto'].queryset = Fumetto.objects.filter(autore_id=autore)
            try:
                fumetto_punta = FumettoPunta.objects.get(autore_id=autore)
                self.fields['fumetto'].initial = fumetto_punta.fumetto
            except FumettoPunta.DoesNotExist:
                pass
            except FumettoPunta.MultipleObjectsReturned:
                # se ci sono più di uno, puoi scegliere il primo o non fare nulla
                fumetto_punta = FumettoPunta.objects.filter(autore_id=autore).first()
                if fumetto_punta:
                    self.fields['fumetto'].initial = fumetto_punta.fumetto
        else:
            self.fields['fumetto'].queryset = Fumetto.objects.none()

@admin.register(Firmacopie)
class FirmacopieAdmin(admin.ModelAdmin):
    form = FirmacopieForm
    list_display = ('fumetto', 'autore', 'stand', 'data', 'ora', 'organizzatore', 'casa_editrice')
    list_filter = ('stand', 'autore', 'casa_editrice', 'data')
    search_fields = ('descrizione',)



