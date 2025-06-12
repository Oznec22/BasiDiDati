from django.urls import path
from . import views

app_name = 'comicon'  # nome app esempio

urlpatterns = [
    # Autenticazione e pagina iniziale
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('scegli_ruolo/', views.scegli_ruolo_view, name='scegli_ruolo'),
    path('logout/', views.logout_view, name='logout'),

    # Home per i vari ruoli
    path('home/', views.home_view, name='home'),
    path('home/autore/', views.home_autore_view, name='home_autore'),
    path('home/casaeditrice/', views.home_casaeditrice_view, name='home_casaeditrice'),

    # Eventi e prenotazioni
    path('eventi/', views.lista_firmacopie_view, name='lista_firmacopie'),
    path('prenotazioni/', views.prenota_evento_view, name='prenotazioni'),
    path('prenota_evento/', views.prenota_evento_view, name='prenota_evento'),
    path('stampa-ticket/<int:id>/', views.stampa_ticket_view, name='stampa_ticket'),
    path('annulla-prenotazione/<int:id>/', views.annulla_prenotazione_view, name='annulla_prenotazione'),

    # Cataloghi
    path('autori/', views.catalogo_autori_view, name='catalogo_autori'),
    path('prodotti/', views.catalogo_prodotti_view, name='catalogo_prodotti'),

    # Profilo utente
    path('modifica-profilo/', views.modifica_profilo_view, name='modifica_profilo'),

    # Casa Editrice - Dashboard e gestione
    path('casa-editrice/dashboard/', views.dashboard_casa_editrice_view, name='dashboard_casa_editrice'),
    path('casa-editrice/prodotti/', views.lista_prodotti_casaeditrice, name='lista_prodotti_casaeditrice'),
    path('casa-editrice/prodotti/aggiungi/', views.aggiungi_prodotto_casaeditrice, name='aggiungi_prodotto_casaeditrice'),
    path('casa-editrice/eventi/', views.calendario_eventi_casaeditrice, name='calendario_eventi_casaeditrice'),
    path('casa-editrice/prenotazioni/', views.visualizza_prenotazioni_casaeditrice, name='visualizza_prenotazioni_casaeditrice'),
    path('casa-editrice/profilo/', views.profilo_casa_editrice_view, name='profilo_casa_editrice'),
    path('casa-editrice/profilo/modifica/', views.modifica_profilo_casa_editrice, name='modifica_profilo_casa_editrice'),
    path('casa-editrice/autori/gestione/', views.gestione_autori_casa_editrice, name='gestione_autori_casa_editrice'),

    # Autore - gestione date preferite e home
    path('autore/salva_date_preferite/', views.salva_date_preferite, name='salva_date_preferite'),
    path('autore/', views.autore, name='autore'),
]
