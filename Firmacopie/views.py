from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.http import HttpResponseRedirect
from .forms import ProfileForm



from .forms import (
    RegistrazioneForm,
    AutoreForm,
    FumettoPuntaForm,
    ProdottoForm,
    CasaEditriceForm,
    CasaEditriceAutoriForm,
    StandForm,
)
from .models import (
    Profile, Firmacopie, Prodotto, Autore,
    FumettoPunta, PrenotazioneFirmacopie,
    CasaEditrice, Stand, Fumetto,
)

# ================ AUTHENTICATION VIEWS ================
def index(request):
    return render(request, 'Firmacopie/index.html')

def login_view(request):
    next_url = request.GET.get('next', '/')  # URL dove tornare dopo login

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        next_url = request.POST.get('next', '/')

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Recupera il profilo e ruolo
            try:
                ruolo = user.profile.ruolo
            except Profile.DoesNotExist:
                ruolo = 'utente'  # fallback

            # Redirect in base al ruolo
            if ruolo == 'autore':
                return redirect('home_autore')
            elif ruolo == 'casa_editrice':
                return redirect('dashboard_casa_editrice')
            else:
                # Ruolo 'utente' o default
                return redirect('home')

        else:
            return render(request, 'Firmacopie/login.html', {
                'form': form,
                'error': 'Username o password errati',
                'next': next_url,
            })

    else:
        form = AuthenticationForm()

    return render(request, 'Firmacopie/login.html', {
        'form': form,
        'next': next_url,
    })

def register_view(request):
    if request.method == 'POST':
        form = RegistrazioneForm(request.POST)
        if form.is_valid():
            user = form.save()
            ruolo = form.cleaned_data['ruolo']
            Profile.objects.create(user=user, ruolo=ruolo)

            # Create related models based on role
            if ruolo == 'autore':
                Autore.objects.create(user=user)
            elif ruolo == 'casa_editrice':
                CasaEditrice.objects.create(manager=user, nome=f"Casa Editrice di {user.username}")

            messages.success(request, 'Registrazione completata! Effettua il login.')
            return redirect('login')
    else:
        form = RegistrazioneForm()
    return render(request, 'Firmacopie/register.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('index')

# ================ ROLE REDIRECTION VIEWS ================
@login_required
def scegli_ruolo_view(request):
    profile = Profile.objects.get(user=request.user)
    redirect_map = {
        'utente': 'home',
        'autore': 'home_autore',
        'casa_editrice': 'home_casaeditrice'
    }
    return redirect(redirect_map.get(profile.ruolo, 'index'))


@login_required
def home_view(request):
    profile = Profile.objects.get(user=request.user)

    if profile.ruolo == 'utente':
        # Renderizzo la home generica per utenti
        return render(request, 'Firmacopie/home.html')

    elif profile.ruolo == 'autore':
        # Redirect alla home autore
        return redirect('home_autore')

    elif profile.ruolo == 'casa_editrice':
        # Redirect alla home casa editrice
        return redirect('home_casaeditrice')

    else:
        # Ruolo non riconosciuto: mostro debug o redirect alla home
        return HttpResponse(f"Ruolo sconosciuto: {profile.ruolo}")
# ================ AUTORE VIEWS ================
@login_required
def home_autore_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.ruolo != 'autore':
        return redirect('home')

    # Recupera o crea l'autore
    autore, created = Autore.objects.get_or_create(user=request.user)

    # Recupera o crea il fumetto associato all'autore
    fumetto, created = Fumetto.objects.get_or_create(
        autore=autore,
        defaults={
            'titolo': 'Inserisci Titolo',
            'prezzo': 0.00,
            'genere': 'Inserisci Genere',
            'casa_editrice': CasaEditrice.objects.first()  # o logica appropriata
        }
    )

    # Recupera o crea il fumetto punta associato all'autore
    fumetto_punta, created = FumettoPunta.objects.get_or_create(
        autore=autore,
        defaults={'fumetto': fumetto}
    )

    # Assicura che fumetto_punta punti al fumetto corretto
    if fumetto_punta.fumetto != fumetto:
        fumetto_punta.fumetto = fumetto
        fumetto_punta.save()

    # Eventi futuri dell'autore
    oggi = timezone.now().date()
    eventi = Firmacopie.objects.filter(autore=autore, data__gte=oggi).order_by('data')

    # Prenotazioni future per l'autore
    prenotazioni = PrenotazioneFirmacopie.objects.filter(
        firmacopie__autore=autore,
        firmacopie__data__gte=oggi
    )

    # Gestione form invio
    if request.method == 'POST':
        form_autore = AutoreForm(request.POST, instance=autore)
        form_fumetto = FumettoPuntaForm(request.POST, instance=fumetto.fumettopunta if hasattr(fumetto, 'fumettopunta') else None)

        if form_autore.is_valid() and form_fumetto.is_valid():
            form_autore.save()
            form_fumetto.save()
            messages.success(request, 'Profilo aggiornato con successo!')
            return redirect('home_autore')
    else:
        form_autore = AutoreForm(instance=autore)
        form_fumetto = FumettoPuntaForm(instance=fumetto.fumettopunta if hasattr(fumetto, 'fumettopunta') else None)

    context = {
        'form_autore': form_autore,
        'form_fumetto': form_fumetto,
        'prenotazioni': prenotazioni,
        'eventi': eventi,
        'page_title': 'Dashboard Autore',
    }

    return render(request, 'Firmacopie/home_autore.html', context)

# ================ CASA EDITRICE VIEWS ================
@login_required
def home_casaeditrice_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.ruolo != 'casa_editrice':
        return redirect('home')

    casa_editrice = get_object_or_404(CasaEditrice, manager=request.user)
    autori_count = Autore.objects.filter(casa_editrice=casa_editrice).count()
    prodotti_count = Prodotto.objects.filter(casa_editrice=casa_editrice).count()
    eventi_count = Firmacopie.objects.filter(casa_editrice=casa_editrice).count()

    context = {
        'casa_editrice': casa_editrice,
        'autori_count': autori_count,
        'prodotti_count': prodotti_count,
        'eventi_count': eventi_count,
    }
    return render(request, 'Firmacopie/home_casaeditrice.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

@login_required(login_url='/login/')  # o il path della tua pagina di login
def lista_prodotti_casaeditrice(request):
    casa_editrice = CasaEditrice.objects.filter(manager=request.user).first()

    if not casa_editrice:
        # eventualmente gestisci il caso di manager senza casa editrice associata
        return redirect('home')  # o mostra una pagina di errore

    prodotti = Prodotto.objects.filter(casa_editrice=casa_editrice)

    context = {
        'prodotti': prodotti,
        'casa_editrice': casa_editrice,
    }

    return render(request, 'Firmacopie/lista_prodotti_casaeditrice.html', context)

def aggiungi_prodotto_casaeditrice(request):
    if not request.user.is_authenticated:
        return redirect('login')  # o la tua pagina di login

    casa_editrice = CasaEditrice.objects.filter(manager=request.user).first()

    if not casa_editrice:
        return redirect('dashboard_casa_editrice')

    if request.method == 'POST':
        form = ProdottoForm(request.POST)
        if form.is_valid():
            prodotto = form.save(commit=False)
            prodotto.casa_editrice = casa_editrice
            prodotto.save()
            return redirect('lista_prodotti_casaeditrice')
    else:
        form = ProdottoForm()

    return render(request, 'Firmacopie/aggiungi_prodotto.html', {'form': form})

@login_required
def calendario_eventi_casaeditrice(request):
    casa_editrice = CasaEditrice.objects.filter(manager=request.user).first()
    eventi = Firmacopie.objects.filter(casa_editrice=casa_editrice)

    context = {
        'casa_editrice': casa_editrice,
        'eventi': eventi,
    }
    return render(request, 'Firmacopie/calendario_eventi.html', context)

@login_required(login_url='/login/')
def visualizza_prenotazioni_casaeditrice(request):
    casa_editrice = CasaEditrice.objects.filter(manager=request.user).first()
    prenotazioni = PrenotazioneFirmacopie.objects.filter(firmacopie__casa_editrice=casa_editrice)

    context = {
        'casa_editrice': casa_editrice,
        'prenotazioni': prenotazioni,
    }
    return render(request, 'Firmacopie/prenotazioni_casa_editrice.html', context)

def profilo_casa_editrice_view(request):
    casa_editrice = CasaEditrice.objects.filter(manager=request.user).first()

    context = {
        'casa_editrice': casa_editrice
    }
    return render(request, 'Firmacopie/profilo_casa_editrice.html', context)

def modifica_profilo_casa_editrice(request):
    casa_editrice = CasaEditrice.objects.filter(manager=request.user).first()

    if not casa_editrice:
        return redirect('home_casaeditrice')

    if request.method == 'POST':
        form = CasaEditriceForm(request.POST, instance=casa_editrice)
        if form.is_valid():
            form.save()
            return redirect('profilo_casa_editrice')
    else:
        form = CasaEditriceForm(instance=casa_editrice)

    return render(request, 'Firmacopie/modifica_profilo_casa_editrice.html', {'form': form})

# ================ COMMON VIEWS ================
@login_required
def lista_firmacopie_view(request):
    eventi = Firmacopie.objects.filter(data__gte=timezone.now().date()).order_by('data', 'ora')
    return render(request, 'Firmacopie/lista_firmacopie.html', {'eventi': eventi})

@login_required
@require_http_methods(["GET", "POST"])
def prenota_evento_view(request, evento_id=None):
    if request.method == 'POST' and evento_id:
        evento = get_object_or_404(Firmacopie, id=evento_id)
        if evento.data < timezone.now().date():
            messages.error(request, 'Non puoi prenotare per un evento passato')
            return redirect('lista_firmacopie')

        if PrenotazioneFirmacopie.objects.filter(utente=request.user, firmacopie=evento).exists():
            messages.warning(request, 'Hai già prenotato questo evento!')
        else:
            PrenotazioneFirmacopie.objects.create(utente=request.user, firmacopie=evento)
            messages.success(request, 'Prenotazione effettuata con successo!')
        return redirect('lista_firmacopie')

    eventi = Firmacopie.objects.filter(data__gte=timezone.now().date()).order_by('data', 'ora')
    return render(request, 'Firmacopie/prenota_evento.html', {'eventi': eventi})

@login_required
def annulla_prenotazione_view(request, id):
    prenotazione = get_object_or_404(PrenotazioneFirmacopie, id=id, utente=request.user)
    if prenotazione.firmacopie.data < timezone.now().date():
        messages.error(request, 'Non puoi cancellare una prenotazione per un evento passato')
    else:
        prenotazione.delete()
        messages.success(request, 'Prenotazione cancellata con successo!')
    return redirect('home')

# ================ UTILITY VIEWS ================
def catalogo_autori_view(request):
    autori = Autore.objects.all().select_related('user', 'casa_editrice')
    return render(request, 'Firmacopie/catalogo_autori.html', {'autori': autori})

def catalogo_prodotti_view(request):
    prodotti = Prodotto.objects.all().select_related('casa_editrice')
    return render(request, 'Firmacopie/catalogo_prodotti.html', {'prodotti': prodotti})

@login_required
def modifica_profilo_view(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profilo aggiornato con successo!')
            return redirect('modifica_profilo')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'Firmacopie/modifica_profilo.html', {'form': form})

def stampa_ticket_view(request, id):
    return render(request, 'stampa_ticket.html', {'id': id})

def modifica_fumetto_punta(request):
    autore = get_object_or_404(Autore, user=request.user)
    fumetto_punta, _ = FumettoPunta.objects.get_or_create(autore=autore)

    if request.method == 'POST':
        form = FumettoPuntaForm(request.POST, instance=fumetto_punta)
        if form.is_valid():
            form.save()
            return redirect('home_autore')
    else:
        form = FumettoPuntaForm(instance=fumetto_punta)

    return render(request, 'management/fumetto_form.html', {'form': form})

from django.shortcuts import render

def dashboard_casa_editrice_view(request):
    cards = [
        {
            'title': 'Gestisci Prodotti',
            'text': 'Aggiungi, modifica o elimina i prodotti della tua casa editrice.',
            'url': 'lista_prodotti_casaeditrice',
            'btn': 'Vai ai Prodotti'
        },
        {
            'title': 'Eventi Firmacopie',
            'text': 'Consulta il calendario degli eventi e organizza le tue partecipazioni.',
            'url': 'calendario_eventi_casaeditrice',
            'btn': 'Vai agli Eventi'
        },
        {
            'title': 'Prenotazioni',
            'text': 'Visualizza e gestisci le prenotazioni effettuate dagli utenti.',
            'url': 'visualizza_prenotazioni_casaeditrice',
            'btn': 'Gestisci Prenotazioni'
        },
        {
            'title': 'Profilo Casa Editrice',
            'text': 'Visualizza e modifica le informazioni del profilo della casa editrice.',
            'url': 'profilo_casa_editrice',
            'btn': 'Modifica Profilo'
        },
        {
            'title': 'Gestione Autori',
            'text': 'Aggiungi o rimuovi autori associati alla tua casa editrice.',
            'url': 'gestione_autori_casa_editrice',
            'btn': 'Gestisci Autori'
        }
    ]

    context = {'cards': cards}
    return render(request, 'Firmacopie/dashboard_casa_editrice.html', context)

@login_required
def crea_fumetto_view(request):
    if request.method == "POST":
        form = FumettoPuntaForm(request.POST)
        if form.is_valid():
            fumetto = form.save(commit=False)
            fumetto.autore = request.user.autore
            fumetto.save()
            return redirect("dashboard_autore")
    else:
        form = FumettoPuntaForm()  # 🔹 Qui carica i valori iniziali!

    return render(request, "Firmacopie/crea_fumetto.html", {"form": form})

@login_required
def salva_date_preferite(request):
        if request.method == 'POST':
            date_selezionate = request.POST.getlist('date_preferite')

            # Per debug — stampa le date selezionate nel terminale
            print("Date selezionate:", date_selezionate)

            # Qui eventualmente puoi salvarle nel database collegandole all'autore
            # esempio:
            # for data in date_selezionate:
            #     PreferenzaData.objects.create(autore=request.user.autore, data=data)

            messages.success(request, 'Le date preferite sono state salvate con successo!')
            return redirect('autore')  # oppure dove vuoi tu

        return redirect('autore')


@login_required
def autore(request):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.ruolo != 'autore':
        return redirect('home')

    autore = get_object_or_404(Autore, user=request.user)
    # example data for the template
    eventi = Firmacopie.objects.filter(autore=autore, data__gte=timezone.now().date()).order_by('data')

    return render(request, 'Firmacopie/autore.html', {
        'autore': autore,
        'eventi': eventi,
        'page_title': 'Pagina Autore',
    })


@login_required
def gestione_autori_casa_editrice(request):
    casa_editrice = get_object_or_404(CasaEditrice, manager=request.user)

    if request.method == 'POST':
        form = CasaEditriceAutoriForm(request.POST, instance=casa_editrice)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lista autori aggiornata con successo!')
            return redirect('home_casaeditrice')
    else:
        form = CasaEditriceAutoriForm(instance=casa_editrice)

    return render(request, 'Firmacopie/gestione_autori_casa_editrice.html', {'form': form})

@login_required
def crea_stand_view(request):
    if request.method == "POST":
        form = StandForm(request.POST)
        if form.is_valid():
            stand = form.save()
            return redirect("lista_stand")  # oppure dove preferisci
    else:
        form = StandForm()

    return render(request, "Firmacopie/crea_stand.html", {"form": form})

def salva_disponibilita(request):
    if request.method == 'POST':
        # Salva la data o altra info
        data = request.POST.get('data')
        # Qui fai il salvataggio nel modello
        # es: tua_model.objects.create(data=data, altro=valore)

        messages.success(request, "La data è stata salvata con successo.")
        # Redirect a una pagina qualsiasi (es. la stessa pagina di inserimento o dashboard)
        return redirect('home_autore')
    else:
        return redirect('home_autore')
