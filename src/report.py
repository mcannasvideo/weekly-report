import os
import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import urllib.parse

# ── Configurazione ──────────────────────────────────────────────
GMAIL_USER     = os.environ["GMAIL_USER"]      # es. tuo@gmail.com
GMAIL_PASSWORD = os.environ["GMAIL_APP_PW"]    # App Password Gmail
EMAIL_TO       = os.environ["EMAIL_TO"]        # destinatario

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

# ── Helpers ─────────────────────────────────────────────────────
def get(url, timeout=10):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"Errore fetch {url}: {e}")
        return None

def indeed_search(query, location="Verona", max_results=8):
    q = urllib.parse.quote_plus(query)
    l = urllib.parse.quote_plus(location)
    url = f"https://it.indeed.com/jobs?q={q}&l={l}&sort=date&fromage=7"
    soup = get(url)
    results = []
    if not soup:
        return results
    cards = soup.select("div.job_seen_beacon")[:max_results]
    for card in cards:
        title_el = card.select_one("h2.jobTitle span")
        company_el = card.select_one("span.companyName")
        link_el = card.select_one("h2.jobTitle a")
        title = title_el.get_text(strip=True) if title_el else "—"
        company = company_el.get_text(strip=True) if company_el else "—"
        href = "https://it.indeed.com" + link_el["href"] if link_el else url
        results.append({"title": title, "company": company, "url": href})
    return results

def infojobs_search(query, location="Verona", max_results=8):
    q = urllib.parse.quote_plus(query)
    l = urllib.parse.quote_plus(location)
    url = f"https://www.infojobs.it/offerte-lavoro/{l}/q-{q}.aspx?sortby=date"
    soup = get(url)
    results = []
    if not soup:
        return results
    cards = soup.select("li.ij-OfferCardItem")[:max_results]
    for card in cards:
        title_el = card.select_one("h2 a, h3 a")
        company_el = card.select_one("span.ij-OfferCardItem-company")
        title = title_el.get_text(strip=True) if title_el else "—"
        company = company_el.get_text(strip=True) if company_el else "—"
        href = title_el["href"] if title_el and title_el.has_attr("href") else url
        if href.startswith("/"):
            href = "https://www.infojobs.it" + href
        results.append({"title": title, "company": company, "url": href})
    return results

def cerca_bandi_google(query, max_results=6):
    """Ricerca bandi via SerpAPI-free alternative: scrape Google News RSS"""
    q = urllib.parse.quote_plus(query)
    url = f"https://news.google.com/rss/search?q={q}&hl=it&gl=IT&ceid=IT:it"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.content, "xml")
        items = soup.find_all("item")[:max_results]
        results = []
        for item in items:
            title = item.find("title").get_text(strip=True) if item.find("title") else "—"
            link  = item.find("link").get_text(strip=True) if item.find("link") else "#"
            pub   = item.find("pubDate")
            pub_str = pub.get_text(strip=True)[:16] if pub else ""
            results.append({"title": title, "url": link, "date": pub_str})
        return results
    except Exception as e:
        print(f"Errore Google News RSS: {e}")
        return []

# ── Sezioni del report ───────────────────────────────────────────
def build_section_jobs(titolo, query_indeed, query_infojobs, location="Verona"):
    risultati = []
    r1 = indeed_search(query_indeed, location, max_results=5)
    r2 = infojobs_search(query_infojobs, location, max_results=5)
    # deduplicazione grossolana per titolo
    visti = set()
    for r in r1 + r2:
        k = r["title"].lower()[:40]
        if k not in visti:
            visti.add(k)
            risultati.append(r)
    risultati = risultati[:8]

    rows = ""
    if risultati:
        for r in risultati:
            rows += f"""
            <tr>
              <td style="padding:6px 8px;border-bottom:1px solid #eee;">
                <a href="{r['url']}" style="color:#1a73e8;text-decoration:none;font-weight:500;">{r['title']}</a>
              </td>
              <td style="padding:6px 8px;border-bottom:1px solid #eee;color:#555;font-size:13px;">{r.get('company','')}</td>
            </tr>"""
    else:
        rows = '<tr><td colspan="2" style="padding:8px;color:#999;">Nessun risultato questa settimana</td></tr>'

    return f"""
    <div style="margin-bottom:28px;">
      <h2 style="font-size:16px;color:#333;border-left:4px solid #1a73e8;padding-left:10px;margin-bottom:8px;">{titolo}</h2>
      <table style="width:100%;border-collapse:collapse;font-size:14px;">{rows}</table>
      <p style="font-size:12px;color:#aaa;margin-top:4px;">
        Cerca tu stesso: 
        <a href="https://it.indeed.com/jobs?q={urllib.parse.quote_plus(query_indeed)}&l=Verona&sort=date" style="color:#aaa;">Indeed</a> · 
        <a href="https://www.infojobs.it/offerte-lavoro/verona/q-{urllib.parse.quote_plus(query_infojobs)}.aspx" style="color:#aaa;">InfoJobs</a>
      </p>
    </div>"""

def build_section_bandi(titolo, query, colore="#e67e22"):
    risultati = cerca_bandi_google(query)
    rows = ""
    if risultati:
        for r in risultati:
            rows += f"""
            <tr>
              <td style="padding:6px 8px;border-bottom:1px solid #eee;">
                <a href="{r['url']}" style="color:#1a73e8;text-decoration:none;font-weight:500;">{r['title']}</a>
              </td>
              <td style="padding:6px 8px;border-bottom:1px solid #eee;color:#888;font-size:12px;white-space:nowrap;">{r.get('date','')}</td>
            </tr>"""
    else:
        rows = '<tr><td colspan="2" style="padding:8px;color:#999;">Nessun risultato questa settimana</td></tr>'

    return f"""
    <div style="margin-bottom:28px;">
      <h2 style="font-size:16px;color:#333;border-left:4px solid {colore};padding-left:10px;margin-bottom:8px;">{titolo}</h2>
      <table style="width:100%;border-collapse:collapse;font-size:14px;">{rows}</table>
    </div>"""

# ── Costruisci l'email ───────────────────────────────────────────
def build_email():
    oggi = datetime.now().strftime("%d %B %Y")

    s1 = build_section_jobs(
        "🍺 Bar, birrerie e locali serali — Verona",
        "barista cameriere locale serale", "barista cameriere"
    )
    s2 = build_section_jobs(
        "🌾 Aziende agricole e agriturismi — Verona",
        "agriturismo azienda agricola operaio", "agriturismo agricoltura"
    )
    s3 = build_section_jobs(
        "🎬 Videomaker",
        "videomaker video editor", "videomaker",
        location="Verona"
    )
    s4 = build_section_bandi(
        "📋 Bandi per progetti artistici (video, foto) — nazionali e regionali",
        "bando concorso progetto artistico video fotografia 2026 regione veneto nazionale",
        colore="#8e44ad"
    )
    s5 = build_section_bandi(
        "🇪🇺 Bandi europei e internazionali — arte visiva",
        "bando europeo internazionale arte visiva video fotografia 2026 Creative Europe",
        colore="#27ae60"
    )

    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:640px;margin:0 auto;padding:20px;color:#222;">
      <div style="background:#1a73e8;color:white;padding:20px 24px;border-radius:10px;margin-bottom:24px;">
        <h1 style="margin:0;font-size:20px;">📬 Report settimanale</h1>
        <p style="margin:4px 0 0;opacity:0.85;font-size:14px;">{oggi}</p>
      </div>
      {s1}
      {s2}
      {s3}
      {s4}
      {s5}
      <hr style="border:none;border-top:1px solid #eee;margin:24px 0;">
      <p style="font-size:12px;color:#aaa;text-align:center;">
        Report automatico generato via GitHub Actions.<br>
        I risultati provengono da Indeed, InfoJobs e Google News.
      </p>
    </body>
    </html>
    """
    return html

# ── Invia email ──────────────────────────────────────────────────
def send_email(html_body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📬 Report lavoro & bandi — {datetime.now().strftime('%d/%m/%Y')}"
    msg["From"]    = GMAIL_USER
    msg["To"]      = EMAIL_TO
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, EMAIL_TO, msg.as_string())
    print(f"✅ Email inviata a {EMAIL_TO}")

if __name__ == "__main__":
    print("🔍 Raccolta dati in corso...")
    html = build_email()
    send_email(html)
