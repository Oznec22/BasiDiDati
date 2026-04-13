# FIRMACOPIE - PORTALE GESTIONE EVENTI COMICON 2026

**Firmacopie** è una piattaforma web progettata per la gestione integrata delle sessioni di autografi e incontri durante il Comicon 2026. Il sistema permette agli utenti di prenotare ticket per i firma-copie, agli autori di gestire le proprie disponibilità e alle case editrici di coordinare i propri artisti e prodotti.

---

## COME USARE IL SITO

### 1. HOME
Pagina principale che accoglie l'utente con una panoramica dell'evento. Da qui è possibile accedere alle sezioni di login e registrazione. Dopo l'accesso, il sistema reindirizza l'utente alla dashboard specifica in base al suo ruolo.

### 2. REGISTRAZIONE
Inserisci username, email e password. È fondamentale scegliere il **ruolo** corretto:
* **Utente:** Per chi vuole partecipare e ricevere autografi.
* **Autore:** Per gli artisti che devono gestire i propri orari.
* **Editore:** Per le case editrici che coordinano stand e prodotti.

### 3. LOGIN
Inserisci le tue credenziali per accedere alle funzionalità riservate. Il sistema riconosce automaticamente se sei un utente, un autore o un editore.

### 4. PRENOTAZIONE TICKET (Utenti)
Vedi la lista dei firma-copie disponibili filtrati per autore o casa editrice. 
* Puoi vedere i posti rimasti per ogni stand.
* Cliccando su "Prenota", riceverai un ticket virtuale unico salvato nel database.

### 5. GESTIONE AUTORE (Autori)
Gli autori possono impostare il proprio fumetto di punta e dichiarare i giorni e le fasce orarie in cui saranno presenti agli stand.

### 6. GESTIONE CATALOGO (Editori)
Le case editrici possono visualizzare i propri autori associati, aggiungere nuovi prodotti al catalogo e monitorare l'andamento delle prenotazioni per i propri eventi.

### 7. RECENSIONI
Dopo aver partecipato a un evento, l'utente può lasciare una recensione con un commento testuale e un voto da 1 a 5 stelle. È possibile vedere le recensioni medie per ogni autore.

### 8. ADMIN
Accesso riservato agli amministratori per la gestione dei padiglioni, degli stand e della manutenzione generale del database.

---
---

## ACCOUNT DI PROVA

Per testare le diverse funzionalità del portale in base ai permessi di accesso, è possibile utilizzare i seguenti account preconfigurati:

### UTENTE PRIVATO (Fan)
* **Username:** `mario`
* **Password:** `comicon!`

### AUTORE
* **Username:** `Oda`
* **Password:** `comicon!`

### CASA EDITRICE
* **Username:** `mondadori`
* **Password:** `comicon!`

---
---

## STRUTTURA DEL PROGETTO

### MODELLI (`models.py`)

* **Utente**: `username`, `password`, `email`, `ruolo`, `casa_editrice`
* **Autore**: `utente`, `opera_principale`, `giorni_disponibili`, `orari_disponibili`
* **Fumetto**: `titolo`, `prezzo`, `genere`, `casa_editrice`
* **Stand**: `padiglione`, `stallo`, `totale_persone`, `disponibilita`
* **FirmaCopie**: `autore`, `disponibilita`, `stand`, `posti_disponibili`
* **Prenotazione**: `utente`, `firmacopie`, `timestamp`
* **Recensione**: `utente`, `firmacopie`, `testo`, `voto`, `data`

### VISTE (`views.py`)

* `login_view` / `registrazione_view`
* `home_redirect_view` (smistamento ruoli)
* `home_utente_view` / `home_autore_view` / `home_editore_view`
* `prenota_annulla_evento`
* `ajax_casa_editrice_autore`

---

## ISTRUZIONI DI AVVIO

1. **Crea l'ambiente virtuale:**
   `python -m venv .venv`

2. **Attivalo:**
   `.venv\Scripts\activate` (Windows) o `source .venv/bin/activate` (Mac/Linux)

3. **Installa i pacchetti:**
   `pip install django django-extensions`

4. **Esegui le migrazioni:**
   `python manage.py makemigrations`
   `python manage.py migrate`

5. **Avvia il server:**
   `python manage.py runserver`

---

**Autore:** Mataluna Vincenzo  
**Corso:** Basi di Dati  
**Università:** Università degli Studi di Napoli Parthenope
