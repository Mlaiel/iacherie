# ✨ Module d'Amélioration IA Avancée

**Amélioration multimédia alimentée par IA avec mise à l'échelle par réseau neuronal pour la plateforme Ainflue**

## Aperçu

Le Module d'Amélioration IA fournit des capacités d'amélioration multimédia de pointe alimentées par l'intelligence artificielle et les réseaux neuronaux. Spécialisé dans la mise à l'échelle, la restauration, la réduction de bruit et l'amélioration de qualité.

## Fonctionnalités

### 🎵 Amélioration Audio
- **Réduction de Bruit**: Gating spectral avancé et filtrage de Wiener
- **Gamme Dynamique**: Compression et expansion intelligentes
- **Restauration**: Restauration audio vintage
- **Normalisation**: Optimisation des niveaux audio conforme LUFS

### 🎬 Amélioration Vidéo
- **Mise à l'Échelle IA**: Real-ESRGAN et ESRGAN pour 2x, 4x, 8x
- **Interpolation d'Images**: Interpolation de mouvement fluide basée sur RIFE
- **Débruitage**: Réduction de bruit temporelle et spatiale avancée
- **Amélioration Couleur**: Correction couleur par apprentissage profond

## Démarrage Rapide

```python
from multimedia.enhancement import AIUpscalingEngine

# Mise à l'échelle d'image IA
upscaling_engine = AIUpscalingEngine()
result = await upscaling_engine.upscale_image(
    "input.jpg",
    "output_4x.jpg", 
    UpscalingConfig(scale_factor=4)
)
```

## Copyright

**© 2025 Fahed Mlaiel - Tous Droits Réservés**  
Contact: mlaiel@live.de