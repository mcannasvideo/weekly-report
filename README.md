# 📬 Report Settimanale — Lavoro & Bandi

Script Python che ogni lunedì mattina ti manda un'email con:
- Offerte di lavoro a Verona (bar, locali, agriturismi, videomaker)
- Bandi nazionali/regionali per progetti artistici
- Bandi europei e internazionali per arte visiva

Gira automaticamente su **GitHub Actions** — gratis, senza server.

---

## Setup (5 minuti)

### 1. Crea il repository su GitHub
- Vai su github.com → New repository → nome: `weekly-report`
- Carica tutti i file di questa cartella

### 2. Ottieni una App Password Gmail
Non usare la tua password normale — crea una password dedicata:
1. Vai su myaccount.google.com → Sicurezza
2. Attiva la **Verifica in due passaggi** (se non l'hai già)
3. Cerca "Password per le app" → crea una nuova app → copia la password di 16 caratteri

### 3. Aggiungi i Secrets su GitHub
Nel tuo repository GitHub:
- Settings → Secrets and variables → Actions → New repository secret

Aggiungi questi tre:

| Nome | Valore |
|------|--------|
| `GMAIL_USER` | la tua email Gmail (es. mario@gmail.com) |
| `GMAIL_APP_PW` | la App Password di 16 caratteri |
| `EMAIL_TO` | l'email dove vuoi ricevere il report |

### 4. Testa subito
- Vai su Actions → "Report settimanale" → Run workflow
- Controlla la tua email dopo circa 1 minuto

### 5. Automatico ogni lunedì
Da quel momento gira ogni lunedì alle 8:00 ora italiana senza fare niente.

---

## Personalizzazione
Modifica `src/report.py` per cambiare:
- Le parole chiave di ricerca
- Il giorno/orario (nel file `.github/workflows/report.yml`)
- I colori o il layout dell'email
