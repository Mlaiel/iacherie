# IA Influencer Agent - Kern-Infrastruktur Modul

## 🏗️ Unternehmensweite Kernsysteme

Dieses Modul stellt die grundlegende Infrastruktur für die IA Influencer Agent Plattform bereit und implementiert professionelle Systeme für Inhaltsschutz, KI-Verarbeitung und Influencer-Kollaboration.

### 🎯 Geschäftslogik Übersicht

**Multi-Creator Workflow:** Musiker, Blogger, Fotografen, Influencer, Komiker → Upload verschiedener Inhaltsformate → KI-Schutz & Rechtemanagement → Professionelles SEO → Kollaborations-Matching → Multi-Plattform Distribution

### 👥 Expertenteam

**Projektleiter & Architekt:** Fahed Mlaiel <mlaiel@live.de>
- **Spezialgebiete:** Lead KI-Entwickler, Senior Backend-Ingenieur, ML-Ingenieur, Datenbankadministrator, Sicherheitsexperte, Microservices-Architekt, Audio-Verarbeitungsspezialist, DevOps-Ingenieur, KI-Prompt-Ingenieur

---

## ⚠️ WARNUNG GEISTIGES EIGENTUM

**STRENGE URHEBERRECHTS-MITTEILUNG - UNBEFUGTE NUTZUNG VERBOTEN**

Diese Software, das Konzept und die Implementierung sind das ausschließliche geistige Eigentum von **Fahed Mlaiel** (mlaiel@live.de).

**WARNUNG AN ALLE PERSONEN UND UNTERNEHMEN:**
- **KEINE ERLAUBNIS** wird erteilt, diesen Code ohne ausdrückliche schriftliche Genehmigung von Fahed Mlaiel zu kopieren, zu modifizieren, zu verbreiten oder zu nutzen
- **RECHTLICHE SCHRITTE** werden gegen jede unbefugte Nutzung, das Kopieren oder den Diebstahl dieses geistigen Eigentums eingeleitet
- **SCHADENERSATZ** und einstweiliger Rechtsschutz werden bei Verstößen gefordert
- Dieser Code ist durch internationale Urheberrechtsgesetze und -verträge geschützt

**Kontakt für Lizenzierung:** mlaiel@live.de

---

## 🏭 Kern-Infrastruktur Komponenten

### 🔧 Konfigurationsmanagement (`config.py`)
- Umgebungsbasierte Konfiguration mit sicheren Standardwerten
- Multi-Umgebungsunterstützung (Entwicklung, Test, Produktion)
- Zentrale Einstellungen mit Typvalidierung mittels Pydantic

### 🗄️ Datenbankintegration (`db.py`)
- PostgreSQL Hauptdatenbank mit Connection Pooling
- Redis Caching-Schicht mit intelligenten Strategien
- Datenbanksitzungsmanagement mit ordnungsgemäßem Lebenszyklus

### 📊 Unternehmensweites Logging (`logging.py`)
- Strukturiertes JSON-Logging mit Korrelations-IDs
- Mehrere Ausgabeformate (Konsole, Datei, Remote)
- Performance-Monitoring und Fehlererfassung

### 🔐 Sicherheits-Framework (`security.py`)
- JWT-Authentifizierung mit Refresh-Tokens
- API-Schlüsselmanagement mit Rate-Limiting
- Multi-Mandanten Sicherheitsisolierung

### ⚡ Exception-Management (`exceptions.py`)
- Umfassende Fehlerhierarchie für Geschäftslogik
- Professionelle Fehlercodes und benutzerfreundliche Nachrichten
- HTTP-Statuscode-Mapping mit detailliertem Kontext

### 🏗️ Dependency Injection (`container.py`)
- Professioneller IoC-Container mit Lebenszyklusmanagement
- Service-Registrierung mit Singleton-, Transient- und Scoped-Lebensdauern
- Automatische Abhängigkeitsauflösung mit Typ-Hints

### 🚀 Event-System (`events.py`)
- Domain Event Sourcing mit umfassenden Metadaten
- Asynchroner Event-Bus mit Prioritätsbehandlung
- Geschäftsereignisse für Inhaltsschutz-Workflow

### 💾 Multi-Level Caching (`cache.py`)
- L1 (Speicher) + L2 (Redis) + L3 (Datenbank) Caching-Hierarchie
- Intelligente Cache-Invalidierungsstrategien (LRU, LFU, TTL)
- Cache-Promotion und geschäftsspezifische Schlüsselgeneratoren

### 🌐 Request-Kontext (`context.py`)
- Verteiltes Tracing mit Korrelations-IDs
- Benutzersitzung und Mandantenisolierung
- Geschäftsoperations-Kontextverfolgung

### 📈 Metriken & Überwachung (`metrics.py`)
- Geschäftsmetriken für Inhaltsschutz-Workflow
- System-Performance-Monitoring mit Timing und Zählern
- Professionelle Observability mit Prometheus-kompatiblem Format

### 🩺 Gesundheitsüberwachung (`health.py`)
- Umfassende Gesundheitschecks für alle Abhängigkeiten
- Datenbank-, Redis-, externe APIs- und Speicherüberwachung
- Graceful Degradation mit detaillierter Statusberichterstattung

### 🛡️ Rate-Limiting (`rate_limit.py`)
- Mehrere Algorithmen: Token Bucket, Sliding Window, Fixed Window
- Konfigurierbare Bereiche: Benutzer, IP, API-Schlüssel, Endpoint, Mandant
- Professionelles Rate-Limiting mit ordnungsgemäßen Headers

---

## 🚀 Schnellstart

```python
from app.core import (
    settings,
    get_db,
    get_cache_manager,
    get_event_bus,
    get_metrics_registry,
    check_system_health
)

# Kernsysteme initialisieren
cache = get_cache_manager()
metrics = get_metrics_registry()
event_bus = await get_event_bus()

# Systemgesundheit prüfen
health_status = await check_system_health()
print(f"Systemstatus: {health_status.overall_status.value}")
```

## 🎯 Geschäftsmetriken Integration

```python
from app.core import get_business_metrics

business_metrics = get_business_metrics()

# Inhalts-Upload erfassen
business_metrics.record_content_upload(
    content_type="audio",
    file_size_mb=25.5,
    user_id="user123"
)

# Fingerabdruck-Generierung erfassen
business_metrics.record_fingerprint_generation(
    content_type="audio",
    duration_ms=1250.0,
    accuracy_score=0.95
)
```

---

## 📋 Modul-Abhängigkeiten

- **FastAPI**: Modernes Web-Framework mit automatischer Dokumentation
- **Pydantic**: Datenvalidierung und Einstellungsmanagement
- **SQLAlchemy**: Datenbank-ORM mit Async-Unterstützung
- **Redis**: Hochleistungs-Caching und Sitzungsspeicherung
- **Prometheus Client**: Metrik-Sammlung und Überwachung

## 🔗 Integrationspunkte

Dieses Kernmodul integriert sich mit:
- **Inhaltsschutz-System** (`app.content_protection`)
- **KI-Verarbeitungspipeline** (`app.ai`)
- **Geschäftslogik-Schicht** (`app.business`)
- **API-Gateway** (`app.api`)
- **Sicherheits-Framework** (`app.security`)

---

## 📝 Lizenz & Kontakt

**Copyright © 2025 IA Influencer Agent - Fahed Mlaiel**
**Alle Rechte vorbehalten**

**Für Lizenzanfragen:** mlaiel@live.de
**Unbefugte Nutzung strikt untersagt**
