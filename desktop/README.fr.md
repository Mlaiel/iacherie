# 🖥️ Ainflue Desktop - Application Electron

## Aperçu

L'application Ainflue Desktop est un studio professionnel de création de contenu alimenté par l'IA, développé avec Electron. Elle offre des capacités d'édition avancées, le support multi-moniteurs et des fonctionnalités complètes d'intégration système.

## 🚀 Fonctionnalités

### Capacités Principales
- **Traitement de Contenu IA Avancé**: Analyse et amélioration intelligentes audio/vidéo
- **Support Multi-Moniteurs**: Flux de travail de studio professionnel sur plusieurs écrans
- **Détection de Plateforme**: Interface utilisateur et fonctionnalités adaptatives basées sur le système d'exploitation
- **Opérations de Fichiers Sécurisées**: Accès protégé au système de fichiers avec permissions appropriées
- **Système de Menu Professionnel**: Menus d'application natifs pour toutes les plateformes
- **Mises à Jour Automatiques**: Mises à jour d'application transparentes via electron-updater

### Fonctionnalités Spécifiques aux Plateformes

#### macOS
- **Barre de Titre Native**: Intégrée avec les directives de design macOS
- **Effets de Transparence**: Effets de fenêtre translucides modernes
- **Signature de Code Prête**: Autorisations appropriées pour la distribution App Store
- **Installateur DMG**: Emballage d'image disque professionnel

#### Windows
- **Installateur NSIS**: Installateur Windows complet
- **Version Portable**: Exécutable portable sans installation
- **Intégration Auto-Start**: Intégration au démarrage Windows
- **Cadre Natif**: Décorations de fenêtre style Windows

#### Linux
- **AppImage**: Format d'application Linux universel
- **Paquet DEB**: Installation de paquet Debian/Ubuntu
- **Paquet RPM**: Installation de paquet Red Hat/SUSE
- **Archive TAR.GZ**: Option d'installation manuelle

## 📦 Configuration de Build

### Dépendances
- **Runtime**: Dépendances de production pour l'application en cours d'exécution
- **Développement**: Outils de build et utilitaires de développement correctement séparés

### Cibles de Build
```bash
# Développement
npm run dev              # Démarrer en mode développement
npm start               # Démarrer en mode production

# Empaquetage
npm run pack            # Créer un répertoire non empaquété (le plus rapide)
npm run build           # Build pour la plateforme actuelle
npm run build:win       # Build des installateurs Windows
npm run build:mac       # Build des paquets macOS
npm run build:linux     # Build des paquets Linux
```

### Formats de Sortie

#### Windows
- **Installateur NSIS** (`Setup.exe`): Installateur complet avec intégration registre
- **Portable** (`Portable.exe`): Exécutable autonome
- **Archive ZIP**: Archive compressée pour extraction manuelle

#### macOS
- **Image DMG**: Installateur glisser-déposer avec arrière-plan personnalisé
- **Archive ZIP**: Bundle d'application compressé

#### Linux
- **AppImage**: Exécutable Linux universel
- **Paquet DEB**: Paquet d'installation Debian/Ubuntu
- **Paquet RPM**: Paquet d'installation Red Hat/SUSE
- **Archive TAR.GZ**: Archive d'installation manuelle

## 🔧 Configuration

### Variables d'Environnement
- `NODE_ENV`: Environnement de développement/production
- `DEBUG`: Activer la journalisation de débogage

### Personnalisation du Build
La configuration de build dans `package.json` supporte:
- Icônes d'application personnalisées pour chaque plateforme
- Certificats de signature de code
- Configuration du serveur de mise à jour automatique
- Options d'installateur spécifiques à la plateforme

## 🛡️ Sécurité

### Signature de Code
- **macOS**: Prêt pour la signature Apple Developer Program
- **Windows**: Préparé pour la signature Authenticode
- **Autorisations**: Déclarations d'autorisation appropriées pour toutes les fonctionnalités

### Sandboxing
- **Isolation de Contexte**: Les processus de rendu sont correctement isolés
- **Scripts de Préchargement**: Pont de communication IPC sécurisé
- **Aucune Intégration Node**: Les processus de rendu n'ont pas d'accès direct à Node.js

## 🔍 Validation

Exécutez le script de validation pour vous assurer que tout est correctement configuré:

```bash
../scripts/validate-build.sh
```

Ce script vérifie:
- ✅ Configuration Package.json
- ✅ Présence des fichiers d'assets
- ✅ Fonctionnalité du système de build
- ✅ Configurations spécifiques à la plateforme

## 📁 Structure du Projet

```
desktop/
├── main.js                 # Processus principal Electron
├── preload.js              # Pont IPC sécurisé
├── package.json            # Dépendances et configuration de build
├── assets/                 # Icônes d'application et ressources
│   ├── icon.png            # Icône Linux
│   ├── icon.ico            # Icône Windows
│   ├── icon.icns           # Icône macOS
│   └── dmg-background.png  # Arrière-plan DMG macOS
├── build/                  # Configuration de build
│   └── entitlements.mac.plist  # Autorisations macOS
├── renderer/               # Code UI et frontend
│   └── index.html          # Fenêtre principale de l'application
└── scripts/                # Scripts utilitaires
    └── validate-build.sh   # Validation de build
```

## 🚀 Déploiement

### Prérequis
- Node.js 18+
- npm ou yarn
- Outils de build spécifiques à la plateforme (Xcode pour macOS, etc.)

### Démarrage Rapide
```bash
# Installer les dépendances
npm install

# Valider la configuration
../scripts/validate-build.sh

# Développement
npm run dev

# Build de production
npm run build:linux    # ou build:win, build:mac
```

### Distribution
1. **Signature de Code**: Configurer les certificats pour chaque plateforme
2. **Build**: Exécuter les commandes de build spécifiques à la plateforme
3. **Test**: Vérifier les installateurs sur les plateformes cibles
4. **Déployer**: Distribuer via site web, app stores ou gestionnaires de paquets

## 📊 Résultats de Build

La validation récente montre des builds réussis:
- **Linux AppImage**: ~137MB (Exécutable universel)
- **Linux DEB**: ~95MB (Paquet Debian)
- **Linux TAR.GZ**: ~130MB (Archive)

Tous les builds incluent:
- Runtime Electron complet
- Code d'application et assets
- Dépendances natives (Sharp, FFmpeg)
- Métadonnées appropriées et intégration desktop

## 🛠️ Développement

### Ajouter des Fonctionnalités
1. Mettre à jour `main.js` pour les fonctionnalités du processus principal
2. Modifier `preload.js` pour l'IPC sécurisé
3. Améliorer `renderer/` pour les composants UI
4. Tester sur toutes les plateformes cibles

### Détection de Plateforme
L'application inclut une détection de plateforme complète:
```javascript
// Disponible dans le processus principal
this.platform.isMac     // Détection macOS
this.platform.isWindows // Détection Windows
this.platform.isLinux   // Détection Linux
this.platform.arch      // Architecture CPU

// Disponible dans le renderer via IPC
const platformInfo = await electronAPI.getPlatformInfo();
```

Cela permet une interface utilisateur adaptative et des fonctionnalités spécifiques à la plateforme dans toute l'application.

## ⚖️ AVIS JURIDIQUE

**Ce logiciel est la PROPRIÉTÉ EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).**

Tous les concepts, architectures, algorithmes et implémentations sont protégés par le droit d'auteur allemand et international. Toute utilisation, reproduction ou distribution non autorisée est strictement interdite et entraînera des poursuites judiciaires immédiates.

**Pour les demandes de licence**: mlaiel@live.de

**Copyright**: © 2025 Fahed Mlaiel. Tous droits réservés.

---

*Application Desktop Professionnelle pour la Création de Contenu IA de Niveau Entreprise*