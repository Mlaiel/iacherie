# Widget Embarquable

Système de widgets embarquables pour intégrer Ainflue sur des sites externes.

## Structure

```
frontend/widget/
├── index.tsx                    # Point d'entrée principal et styles CSS
├── components/
│   ├── AnalyticsWidget.tsx      # Widget analytics embarquable
│   ├── ProtectionWidget.tsx     # Widget statut de protection
│   └── ContentWidget.tsx        # Widget aperçu de contenu
├── builder/
│   └── WidgetBuilder.tsx        # Constructeur visuel de widgets
└── config/
    └── WidgetConfig.tsx         # Configuration et gestion API
```

## Types de Widgets

### Analytics Widget
Affiche des métriques clés (vues, croissance, revenus) dans un format compact.

### Protection Widget
Montre le statut de protection du contenu avec niveau de sécurité et alertes.

### Content Widget
Présente un aperçu de contenu avec thumbnail, statistiques et call-to-action.

## Constructeur de Widget

Le `WidgetBuilder` permet de :
- Configurer le type et l'apparence du widget
- Prévisualiser en temps réel
- Générer le code d'intégration
- Personnaliser les couleurs et thèmes

## Configuration

### Utilisation basique
```tsx
import { EmbeddableWidget } from '@/widget';

<EmbeddableWidget 
  type="analytics"
  config={{
    apiKey: "your-api-key",
    userId: "user-id",
    theme: "light",
    size: "medium"
  }}
/>
```

### Code d'intégration HTML
```html
<div id="ainflue-widget"></div>
<script>
  AinfluceWidget.render('ainflue-widget', {
    type: 'analytics',
    apiKey: 'your-key',
    // ... config
  });
</script>
```

## Thèmes et Personnalisation

- **Thèmes** : light, dark, auto
- **Tailles** : small (200px), medium (400px), large (600px)
- **Couleurs** : Personnalisation complète via CSS variables
- **Responsive** : Adaptation automatique à la taille du conteneur

## Sécurité

- Domaines autorisés configurables
- Limite de requêtes API
- Validation des clés API
- CORS et CSP compatibles

## Déploiement

Les widgets peuvent être déployés via CDN ou intégrés directement dans l'application Next.js.