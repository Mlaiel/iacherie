# Interface Mobile

Module d'interface mobile optimisée pour la plateforme Ainflue.

## Structure

```
frontend/mobile/
├── index.tsx                    # Point d'entrée principal
├── components/
│   ├── MobileNavigation.tsx     # Navigation mobile (bottom nav)
│   ├── MobileHeader.tsx         # En-tête mobile avec statut
│   └── MobileDashboard.tsx      # Dashboard mobile adaptatif
└── hooks/
    └── useMobile.ts             # Hook pour détection mobile et PWA
```

## Fonctionnalités

- **Navigation mobile** : Bottom navigation avec 5 sections principales
- **Dashboard adaptatif** : Interface optimisée pour les écrans tactiles
- **Détection PWA** : Support des Progressive Web Apps
- **Responsive design** : Adaptatif selon l'orientation (portrait/landscape)
- **Pull-to-refresh** : Rafraîchissement par geste
- **Statut de connexion** : Indicateur online/offline

## Composants

### MobileInterface
Composant principal qui orchestre l'interface mobile complète.

### MobileNavigation
Navigation en bas d'écran avec indicateurs visuels pour l'état actif.

### MobileDashboard
Dashboard avec cartes métriques, actions rapides et activité récente.

### useMobile Hook
- Détection du type d'appareil
- Gestion de l'orientation
- Statut de connexion
- Installation PWA

## Utilisation

```tsx
import { MobileInterface } from '@/mobile';

// Dans votre app
<MobileInterface />
```

## Configuration

L'interface s'adapte automatiquement selon les capacités de l'appareil et les préférences utilisateur.