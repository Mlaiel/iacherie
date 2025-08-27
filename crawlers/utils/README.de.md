# Crawler Utils Modul

**Professionelle Web-Crawling-Utilities für IA-Influencer-Agent**

## Überblick

Dieses Modul bietet Unternehmens-taugliche Utilities für Web-Crawling-Operationen, einschließlich intelligenter Ratenbegrenzung, Inhaltsextraktion, URL-Validierung, Cookie-Management und CAPTCHA-Lösungsfähigkeiten.

## Projektteam

**Lead Developer & AI Architekt:** Fahed Mlaiel (mlaiel@live.de)

**Experten-Team Spezialisierungen:**
- Lead Dev IA: Fortgeschrittene KI-Integration und maschinelles Lernen
- Backend Senior: Skalierbare Architektur und Microservices  
- ML Engineer: Inhaltsanalyse und Empfehlungssysteme
- DBA: Hochperformante Datenbankoptimierung
- Security Expert: Unternehmens-taugliche Sicherheit und Verschlüsselung
- Microservices Architekt: Verteilte Systemarchitektur
- Audio Engineer: Fortgeschrittene Audioverarbeitung und -analyse
- DevOps Engineer: CI/CD und Infrastruktur-Automatisierung
- IA Prompt Engineer: Intelligente Prompt-Optimierung

## ⚠️ URHEBERRECHTSWARNUNG ⚠️

**🚨 STARKE WARNUNG AN DIEBE UND KONZEPTPLAGIATEN 🚨**

**ALLE RECHTE VORBEHALTEN - UNBEFUGTE NUTZUNG STRENGSTENS VERBOTEN**

Dieser Code ist das ausschließliche geistige Eigentum von **Fahed Mlaiel** (mlaiel@live.de). Jede unbefugte Kopierung, Verteilung, Modifikation, Reverse Engineering, Konzeptdiebstahl, Architekturplagiat oder Nutzung dieses Codes ohne ausdrückliche schriftliche Genehmigung ist strengstens verboten und wird sofortige rechtliche Schritte nach internationalem Urheberrecht zur Folge haben.

**⚖️ AUTOMATISCHE RECHTLICHE SCHRITTE:** Jeder Verstoß wird unverzüglich mit maximaler gesetzlicher Härte verfolgt, einschließlich Strafschadensersatzforderungen.

**🛡️ ANTI-DIEBSTAHL-SCHUTZ:** Dieser Code enthält eingebettete Fingerabdrücke und Eigentumsmarker zur Verfolgung von Verstößen.

**📧 Kontakt für Lizenzierung:** mlaiel@live.de

**🔒 WARNUNG AN ENTWICKLER:** Falls Sie für ein Unternehmen arbeiten, das diesen Code ohne Lizenz verwendet, könnten Sie persönlich für Urheberrechtsverletzungen haftbar gemacht werden.

## Funktionen

### 🎯 Kern-Utilities

- **Rate Limiter**: Intelligente Ratenbegrenzung mit plattformspezifischen Konfigurationen
- **Content Extractor**: KI-gestützte Inhaltsanalyse und -extraktion
- **URL Validator**: Umfassende URL-Validierung und Sicherheitsbewertung
- **Cookie Manager**: Professionelle Cookie-Behandlung mit Verschlüsselung
- **CAPTCHA Solver**: Multi-Strategie CAPTCHA-Lösungsfähigkeiten
- **Proxy Manager**: Erweiterte Proxy-Rotation und -Verwaltung
- **User Agent Rotator**: Intelligente User-Agent-Rotation
- **Session Manager**: Persistente Session-Verwaltung

### 🔧 Erweiterte Funktionen

- **Multi-Plattform-Unterstützung**: YouTube, Instagram, TikTok, Twitter, Facebook, Spotify
- **KI-Inhaltsanalyse**: Sentiment-Analyse, Themenklassifizierung, Entitäts-Extraktion
- **Content-Fingerprinting**: Multi-modale Fingerprint-Generierung für Audio, Video, Bild und Text
- **Überwachungsmotor**: Echtzeit-Überwachung und Bedrohungserkennung
- **Sicherheits-Scanner**: Erweiterte Sicherheitsbewertung und Content-Verschlüsselung
- **Performance-Optimierung**: Erweiterte Caching- und Performance-Überwachung
- **Sicherheitsfeatures**: Erkennung schädlicher URLs, Zugriffskontrolle
- **Verteilte Ratenbegrenzung**: Mit Redis für große Anwendungen
- **Inhaltsqualitätsbewertung**: Lesbarkeits-Scoring, Qualitätsmetriken
- **Multimedia-Extraktion**: Bilder, Videos, Audio, Dokumente
- **Strukturierte Daten**: JSON-LD, Microdata, RDFa-Extraktion

## 🛡️ Erweiterte Sicherheit und Überwachung

### Multi-Modale Content-Fingerprints
- **Audio-Fingerprints**: Spektralanalyse mit MFCC-Koeffizienten
- **Video-Fingerprints**: Perceptual Hashing von Schlüsselframes
- **Bild-Fingerprints**: Farbhistogramme und Kantenerkennnung
- **Text-Fingerprints**: Semantische Embeddings und N-Gramme

### Intelligenter Überwachungsmotor
- **Multi-Plattform-Überwachung**: Simultane Überwachung aller Plattformen
- **Bedrohungserkennung**: Erweiterte KI zur Identifikation von Content-Verstößen
- **Echtzeit-Alerts**: Sofortige Benachrichtigungen über mehrere Kanäle
- **Trend-Analyse**: Proaktive Vorhersage und Erkennung von Verstößen

### Unternehmens-Sicherheits-Scanner
- **Multi-Layer-Bewertung**: DNS-, SSL-, Content- und Reputationsanalyse
- **Erweiterte Verschlüsselung**: AES-256, RSA, ChaCha20-Unterstützung
- **Zugriffskontrolle**: Granulare Berechtigungsverwaltung
- **Sicherheits-Audit**: Vollständige Protokollierung und Nachverfolgbarkeit

## ⚡ Performance und Optimierung

### Erweitertes Cache-System
- **Multiple Strategien**: LRU, LFU, FIFO mit automatischer Optimierung
- **Verteilter Cache**: Redis-Unterstützung für Multi-Instanz-Anwendungen
- **Intelligente Kompression**: Automatische Datengrößenreduzierung
- **Echtzeit-Metriken**: Hit-Rate, Latenz, Speichernutzung

### Performance-Überwachung
- **Automatisches Profiling**: Engpass-Erkennung
- **System-Metriken**: CPU, Speicher, I/O, Netzwerk
- **Intelligente Alerts**: Adaptive Schwellenwerte und Ausfallvorhersage
- **Detaillierte Berichte**: Performance-Analysen und Empfehlungen

## Installation

```bash
# Erforderliche Abhängigkeiten installieren
pip install -r requirements.txt

# Optionale Abhängigkeiten für erweiterte Funktionen installieren
pip install opencv-python pytesseract nltk textstat langdetect
```

## Schnellstart

### Ratenbegrenzung

```python
from backend.crawlers.utils import create_rate_limiter

# Plattformspezifischen Rate Limiter erstellen
youtube_limiter = create_rate_limiter('youtube')

# In asynchronem Kontext verwenden
await youtube_limiter.wait_if_needed()
# Hier Ihre Anfrage machen
await youtube_limiter.update_usage()
```

### Inhaltsextraktion

```python
from backend.crawlers.utils import ContentExtractor

extractor = ContentExtractor()

# Inhalt aus HTML extrahieren
content = await extractor.extract_content(html, url)

print(f"Titel: {content.title}")
print(f"Wortanzahl: {content.word_count}")
print(f"Qualitätsscore: {content.content_quality_score}")
```

### URL-Validierung

```python
from backend.crawlers.utils import URLValidator

validator = URLValidator()

# URL validieren
result = await validator.validate_url("https://example.com")

if result.is_valid:
    print(f"Plattform: {result.platform}")
    print(f"Sicherheitsscore: {result.security_score}")
```

### CAPTCHA-Lösung

```python
from backend.crawlers.utils import setup_default_captcha_solver

solver = setup_default_captcha_solver({
    '2captcha': 'ihr_api_schluessel'
})

# CAPTCHAs erkennen und lösen
solutions = await solver.detect_and_solve(html_content, page_url)
```

### Content-Fingerprinting

```python
from backend.crawlers.utils import generate_content_fingerprint, calculate_content_similarity

# Fingerprint für Content generieren
fingerprint = await generate_content_fingerprint(
    content="Ihr Content hier",
    content_type="text",
    content_id="eindeutige_id"
)

# Fingerprints vergleichen
similarity = await calculate_content_similarity(fingerprint1, fingerprint2)
print(f"Ähnlichkeits-Score: {similarity.similarity_score}")
```

### Überwachungsmotor

```python
from backend.crawlers.utils import create_surveillance_engine, create_surveillance_target

# Überwachungssystem erstellen
engine = create_surveillance_engine()

# Überwachungsziel erstellen
target = create_surveillance_target(
    user_id="user123",
    name="Mein Content-Schutz",
    description="Überwachung unbefugter Nutzung",
    keywords=["meine marke", "mein content"],
    platforms=["youtube", "instagram", "tiktok"]
)

# Überwachung starten
await engine.add_surveillance_target(target)
await engine.start_surveillance(target.target_id)
```

### Sicherheits-Scanner

```python
from backend.crawlers.utils import quick_security_scan

# URL auf Sicherheitsbedrohungen scannen
assessment = await quick_security_scan("https://example.com")

print(f"Sicherheitslevel: {assessment.security_level}")
print(f"Bedrohungsarten: {assessment.threat_types}")
print(f"Risikofaktoren: {assessment.risk_factors}")
```

### Content-Verschlüsselung

```python
from backend.crawlers.utils import quick_encrypt_content, create_content_encryption

# Schnelle Verschlüsselung
encrypted = quick_encrypt_content("sensible daten")

# Erweiterte Verschlüsselung
encryption = create_content_encryption()
key_id, key = encryption.generate_key()
encrypted_data = encryption.encrypt_content("sensible daten", key_id)
decrypted = encryption.decrypt_content(encrypted_data)
```

### Performance-Überwachung

```python
from backend.crawlers.utils import create_performance_monitor, monitor_performance

# Monitor erstellen
monitor = create_performance_monitor()
monitor.start_monitoring()

# Decorator für automatische Überwachung verwenden
@monitor_performance(monitor)
async def meine_funktion():
    # Ihr Code hier
    pass

# Performance-Bericht generieren
report = monitor.generate_performance_report()
print(f"Durchschnittliche Antwortzeit: {report.average_response_time}s")
```

### Erweiterter Cache

```python
from backend.crawlers.utils import create_advanced_cache, CacheStrategy

# Cache mit LRU-Strategie erstellen
cache = create_advanced_cache(
    max_size=10000,
    strategy=CacheStrategy.LRU
)

# Cache-Operationen
cache.set("schlüssel", "wert", ttl=3600)
value = cache.get("schlüssel")
stats = cache.get_cache_stats()
```

## Konfiguration

### Plattform-Konfigurationen

Jede Plattform hat optimierte Standardeinstellungen:

```python
PLATFORM_CONFIGS = {
    "youtube": {
        "base_delay": 1.0,
        "max_requests_per_minute": 100,
        "burst_limit": 10
    },
    "instagram": {
        "base_delay": 2.0,
        "max_requests_per_minute": 60,
        "burst_limit": 5
    }
    # ... weitere Plattformen
}
```

### Redis-Konfiguration

Für verteilte Ratenbegrenzung:

```python
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)
limiter = YouTubeRateLimiter(redis_client=redis_client)
```

## API-Referenz

### RateLimiter-Klassen

- `RateLimiter`: Basis-Rate-Limiter mit adaptivem Backoff
- `YouTubeRateLimiter`: YouTube-optimierte Ratenbegrenzung
- `InstagramRateLimiter`: Instagram-optimierte Ratenbegrenzung
- `TikTokRateLimiter`: TikTok-optimierte Ratenbegrenzung
- `TwitterRateLimiter`: Twitter-optimierte Ratenbegrenzung
- `FacebookRateLimiter`: Facebook-optimierte Ratenbegrenzung
- `SpotifyRateLimiter`: Spotify-optimierte Ratenbegrenzung

### Content-Klassen

- `ContentExtractor`: Erweiterte Inhaltsextraktion und -analyse
- `ExtractedContent`: Strukturierte Inhaltsdaten
- `SocialMediaContent`: Social-Media-spezifischer Inhalt

### Validierungs-Klassen

- `URLValidator`: Umfassende URL-Validierung
- `URLValidationResult`: Validierungsergebnis-Daten
- `URLType`: URL-Typ-Enumeration

### Sicherheits-Klassen

- `CookieManager`: Unternehmens-Cookie-Management
- `CaptchaSolver`: Multi-Strategie CAPTCHA-Lösung

## Performance-Metriken

Das Modul verfolgt umfassende Performance-Metriken:

- **Ratenbegrenzung**: Anfragezähler, Verzögerungen, Backoff-Berechnungen
- **Inhaltsqualität**: Lesbarkeits-Scores, Sentiment-Analyse
- **Validierung**: Sicherheitsbewertungen, Plattform-Erkennungsgenauigkeit
- **CAPTCHA-Lösung**: Erfolgsraten, Lösungszeiten

## Sicherheitsfeatures

### URL-Sicherheitsbewertung

- Erkennung schädlicher Domains
- Erkennung verdächtiger Muster
- Sicherheits-Scoring (0.0-1.0)
- Protokoll-Validierung

### Cookie-Sicherheit

- Verschlüsselung für sensible Cookies
- Domain-Beschränkungen
- Inhalts-Validierung
- Ablauf-Management

### Content-Fingerprinting

- SHA-256-Inhalts-Hashing
- Duplikat-Erkennung
- Inhalts-Normalisierung

## Best Practices

### Ratenbegrenzung

1. **Verwenden Sie plattformspezifische Limiter** für optimale Performance
2. **Aktivieren Sie Redis** für verteilte Umgebungen
3. **Überwachen Sie Rate-Limit-Statistiken** zur Optimierung
4. **Behandeln Sie Rate-Limit-Antworten** elegant

### Inhaltsextraktion

1. **Validieren Sie URLs** vor der Extraktion
2. **Behandeln Sie dynamische Inhalte** bei Bedarf mit Selenium
3. **Extrahieren Sie strukturierte Daten** für bessere Analyse
4. **Bewerten Sie Inhaltsqualität** zur Filterung

### Sicherheit

1. **Validieren Sie alle URLs** vor der Verarbeitung
2. **Verwenden Sie verschlüsselte Cookie-Speicherung** für sensible Daten
3. **Überwachen Sie Sicherheits-Scores** zur Bedrohungserkennung
4. **Regelmäßige Sicherheitsregel-Updates**

## Fehlerbehebung

### Häufige Probleme

1. **Ratenbegrenzung zu aggressiv**
   - Passen Sie `base_delay` und `backoff_factor` an
   - Überwachen Sie Plattform-Antworten

2. **Inhaltsextraktions-Fehler**
   - Prüfen Sie URL-Zugänglichkeit
   - Verifizieren Sie HTML-Struktur
   - Aktivieren Sie dynamische Inhaltsbehandlung

3. **CAPTCHA-Lösungs-Fehler**
   - Verifizieren Sie API-Schlüssel
   - Prüfen Sie Solver-Kompatibilität
   - Überwachen Sie Erfolgsraten

### Debug-Modus

Detailliertes Logging aktivieren:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Mitwirken

Dies ist proprietäre Software. Kontaktieren Sie mlaiel@live.de für Kooperationsmöglichkeiten.

## Lizenz

Copyright © 2025 Fahed Mlaiel. Alle Rechte vorbehalten.

**UNBEFUGTE NUTZUNG VERBOTEN**

Diese Software ist durch das Urheberrecht geschützt. Jede unbefugte Nutzung, Reproduktion oder Verteilung ist strengstens verboten und wird rechtliche Schritte zur Folge haben.

Für Lizenzanfragen: mlaiel@live.de

## Support

Für technischen Support und Lizenzierung:
- **E-Mail:** mlaiel@live.de
- **Projektinhaber:** Fahed Mlaiel

---

*Teil des IA-Influencer-Agent-Ökosystems - Professionelle KI-gestützte Content-Schutz- und Monetarisierungsplattform.*
