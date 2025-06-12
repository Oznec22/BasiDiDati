from django.contrib.auth.models import User
from django.db import models

RUOLO_CHOICES = [
    ('utente', 'Utente'),
    ('autore', 'Autore'),
    ('casa_editrice', 'Casa Editrice'),
]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ruolo = models.CharField(max_length=20, choices=RUOLO_CHOICES, default='utente')

    def __str__(self):
        return f"{self.user.username} - {self.ruolo}"

class CasaEditrice(models.Model):
    nome = models.CharField(max_length=255)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='casa_editrice_gestita')
    autori = models.ManyToManyField('Autore', blank=True, related_name='case_editrici')

    def __str__(self):
        return self.nome

class Autore(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    casa_editrice = models.ForeignKey(CasaEditrice, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username

class Prodotto(models.Model):
    titolo = models.CharField(max_length=255)
    prezzo = models.DecimalField(max_digits=6, decimal_places=2)
    casa_editrice = models.ForeignKey(CasaEditrice, on_delete=models.CASCADE)

    def __str__(self):
        return self.titolo

class Fumetto(Prodotto):
    autore = models.ForeignKey(Autore, on_delete=models.CASCADE)
    genere = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.titolo} di {self.autore}"

class FumettoPunta(models.Model):
    autore = models.OneToOneField(Autore, on_delete=models.CASCADE)
    fumetto = models.OneToOneField(Fumetto, on_delete=models.CASCADE)

    def __str__(self):
        return f"Fumetto punta: {self.fumetto.titolo} (autore: {self.autore.user.username})"

class Stand(models.Model):
    PADIGLIONE_CHOICES = [(str(i), str(i)) for i in range(1, 7)]

    nome = models.CharField(max_length=100)
    padiglione = models.CharField(max_length=1, choices=PADIGLIONE_CHOICES, default='1')
    disponibile = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} (Padiglione {self.padiglione})"

class Firmacopie(models.Model):
    fumetto = models.ForeignKey(Fumetto, on_delete=models.CASCADE)
    autore = models.ForeignKey(Autore, on_delete=models.CASCADE)
    stand = models.ForeignKey(Stand, on_delete=models.CASCADE)
    data = models.DateField(default="2025-01-01")
    ora = models.TimeField(default="12:00")
    organizzatore = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eventi_organizzati')
    descrizione = models.TextField(default="Evento firmacopie ufficiale")
    casa_editrice = models.ForeignKey(CasaEditrice, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Firmacopie di {self.autore} per {self.fumetto} il {self.data} alle {self.ora}"

class PrenotazioneFirmacopie(models.Model):
    utente = models.ForeignKey(User, on_delete=models.CASCADE)
    firmacopie = models.ForeignKey(Firmacopie, on_delete=models.CASCADE)
    data_prenotazione = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.utente} - {self.firmacopie}"

class DisponibilitaAutore(models.Model):
    autore = models.ForeignKey(Autore, on_delete=models.CASCADE)
    data_evento = models.DateField()
    numero_posti = models.PositiveIntegerField()

    def __str__(self):
        return f'Disponibilità per {self.autore.user.username} il {self.data_evento}'

class Evento(models.Model):
    titolo = models.CharField(max_length=200)
    orario_inizio = models.DateTimeField()
    orario_fine = models.DateTimeField()
    stand = models.ForeignKey(Stand, on_delete=models.CASCADE)
    autore = models.ForeignKey(Autore, on_delete=models.CASCADE)
    casa_editrice = models.ForeignKey(CasaEditrice, on_delete=models.CASCADE)

    def __str__(self):
        return self.titolo
