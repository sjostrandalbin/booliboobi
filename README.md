# Booli Scraper

Ett Python-skript som automatiskt skrapar bostadsannonser från **Booli**, lagrar dem i en SQLite-databas och skickar ett e-postmeddelande med nya annonser var 30\:e minut via **GitHub Actions**.

## Funktioner

- Skrapar bostadsannonser från Booli.
- Sparar nya annonser i en SQLite-databas.
- Skickar e-postnotifieringar om nya bostadsannonser.
- Körs automatiskt var 30\:e minut med **GitHub Actions**.

## Installation

### 1. Klona detta repository

```bash
git clone https://github.com/ditt-anvandarnamn/booli-scraper.git
cd booli-scraper
```

### 2. Skapa och aktivera en virtuell miljö

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate    # Windows
```

### 3. Installera beroenden

```bash
pip install -r requirements.txt
```

### 4. Skapa en `.env`-fil

Skapa en **.env**-fil i projektmappen och fyll i dina e-postuppgifter:

```ini
SENDER_EMAIL=din-email@gmail.com
RECEIVER_EMAIL=mottagarens-email@gmail.com
EMAIL_PASSWORD=app-losenord
```

**Obs!** Om du använder Gmail behöver du skapa ett **App-lösenord** istället för ditt vanliga lösenord: [https://support.google.com/accounts/answer/185833?hl=sv](https://support.google.com/accounts/answer/185833?hl=sv)

### 5. Kör skriptet manuellt (för test)

```bash
python your_script.py
```

---

## Automatisering med GitHub Actions

### 1. Lägg till GitHub Secrets

För att lagra känsliga uppgifter säkert, gå till:

**GitHub Repo → Settings → Secrets and variables → Actions → New repository secret**

Lägg till följande:

- `SENDER_EMAIL`
- `RECEIVER_EMAIL`
- `EMAIL_PASSWORD`

### 2. Skapa en GitHub Actions Workflow

Lägg till följande fil i `.github/workflows/python-script.yml`:

```yaml
name: Run Python script every 30 minutes
on:
  schedule:
    - cron: '*/30 * * * *'  # Kör var 30:e minut
  workflow_dispatch:

jobs:
  run-script:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Set environment variables
        run: |
          echo "SENDER_EMAIL=${{ secrets.SENDER_EMAIL }}" >> $GITHUB_ENV
          echo "RECEIVER_EMAIL=${{ secrets.RECEIVER_EMAIL }}" >> $GITHUB_ENV
          echo "EMAIL_PASSWORD=${{ secrets.EMAIL_PASSWORD }}" >> $GITHUB_ENV
      - name: Run script
        run: python your_script.py
```

### 3. Push till GitHub

```bash
git add .
git commit -m "Lagt till GitHub Actions workflow"
git push
```

**Nu kommer skriptet att köras automatiskt var 30****:e**** minut!** 🚀

---

## Felsökning

**Vanliga problem och lösningar:**

- **Problem med e-postautentisering?**

  - Använd ett **app-lösenord** istället för ditt vanliga lösenord.
  - Kontrollera att du har aktiverat "Less Secure Apps" (för vissa e-postleverantörer).

- **Fel vid web scraping?**

  - Booli kan ha ändrat sin HTML-struktur, så inspektörverktyget i webbläsaren kan behövas för att uppdatera selektorerna i koden.

- **GitHub Actions körs inte?**

  - Kontrollera att `python-script.yml` finns i `.github/workflows/`.
  - Se till att ditt repository inte är **privat**, om du använder **GitHub Free** (privata repo har begränsad Actions-användning).

---

## Bidra

Har du förbättringar eller förslag? Öppna en **issue** eller skicka en **pull request**! 

---

## Licens

MIT License - Använd fritt och bidra gärna! 

