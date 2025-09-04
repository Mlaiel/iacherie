# Dashboard Temps Réel

Ce module fournit une interface de dashboard temps réel pour la plateforme Ainflue.

## Structure

```
frontend/app/realtime/
├── page.tsx                 # Page principale du dashboard temps réel
├── layout.tsx               # Layout spécifique pour le dashboard
└── components/
    ├── LiveMetricsGrid.tsx  # Grille de métriques en temps réel
    ├── ActivityStream.tsx   # Flux d'activité live
    └── PerformanceChart.tsx # Graphiques de performance temps réel
```

## Fonctionnalités

- **Métriques en temps réel** : Affichage des KPIs actualisés toutes les 3 secondes
- **Flux d'activité** : Stream d'événements en temps réel
- **Graphiques interactifs** : Visualisations avec Recharts
- **Indicateurs de connexion** : Statut de connexion WebSocket
- **Interface responsive** : Optimisée pour mobile et desktop

## Utilisation

Accédez au dashboard via `/realtime` ou intégrez le composant `RealTimeAnalytics` dans d'autres pages.

## Intégration

Le dashboard utilise le composant existant `RealTimeAnalytics` et s'intègre avec l'infrastructure backend analytics existante via WebSocket.

## Configuration

Les métriques sont mises à jour automatiquement via WebSocket. La configuration se fait dans les variables d'environnement du backend.