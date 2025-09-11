# Protection Docker Services

Professionelle Docker-Services für protection-Funktionalität in der Ainflue-Plattform.

## Überblick

Dieses Modul stellt containerisierte protection-Services bereit, die für Unternehmens-Deployments entwickelt wurden.

## Architektur

- **Multi-Stage-Builds**: Für Produktion optimiert
- **Sicherheit gehärtet**: Nicht-Root-Benutzer, minimale Angriffsfläche
- **Gesundheitschecks**: Umfassendes Monitoring
- **Ressourcen optimiert**: Effiziente Speicher- und CPU-Nutzung

## Verwendung

```bash
# Services erstellen
docker compose build

# Services starten
docker compose up -d

# Logs anzeigen
docker compose logs -f
```

## Services Included

Multiple specialized Docker services for protection operations.

## Requirements

- Docker 20.10+
- Docker Compose 2.0+
- Minimum 2GB RAM
- 10GB disk space

## Configuration

Configure environment variables in `.env` file:

```env
# PROTECTION_CONFIG
PROTECTION_LOG_LEVEL=INFO
PROTECTION_PORT=8080
```

## Health Monitoring

All services include comprehensive health checks:

- **Startup**: 30s initial delay
- **Interval**: 30s check frequency  
- **Timeout**: 10s response timeout
- **Retries**: 3 attempts before unhealthy

## Security

- Non-root container execution
- Minimal base images (distroless when possible)
- Regular security scanning
- Network isolation
- Secret management

## Performance

- Multi-stage builds for minimal image size
- Resource limits and reservations
- Horizontal scaling ready
- Optimized caching layers

## Support

For technical support, contact:
- **Author**: Fahed Mlaiel
- **Email**: mlaiel@live.de
- **Platform**: Ainflue Enterprise

## Urheberrecht

© 2025 Fahed Mlaiel (mlaiel@live.de). Alle Rechte vorbehalten.
