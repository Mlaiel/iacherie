# 🔑 GUIDE COMPLET - APIs GRATUITES ÉTAPE PAR ÉTAPE
## Ce que chaque API fait + Comment l'obtenir + Liens directs

**Auteur:** Fahed Mlaiel  
**Date:** 28 Septembre 2025  
**Projet:** Ainfluencer - 53 Agents IA + 680 Microservices

---

## 📋 **CE DONT VOUS AVEZ BESOIN EXACTEMENT**

Chaque API ci-dessous explique:
- 🎯 **À QUOI ÇA SERT** (fonction précise)
- 🔑 **CE QU'IL FAUT RÉCUPÉRER** (clés, tokens, IDs)
- 🌐 **LIEN DIRECT** pour s'inscrire
- ⚙️ **CONFIGURATION** dans votre `.env`

---

# 🤖 **1. INTELLIGENCE ARTIFICIELLE (12 APIs)**

## 🖼️ **Génération d'Images**

### **1. Hugging Face (IA Images)**
- **À QUOI ÇA SERT:** Générer des images avec des modèles IA gratuits
- **CE QU'IL FAUT:**
  - `HUGGINGFACE_API_KEY` = hf_xxxxxxxxxxxxx
- **LIEN:** https://huggingface.co/settings/tokens
- **ÉTAPES:**
  1. Créer compte gratuit
  2. Aller dans Settings > Access Tokens
  3. Créer un nouveau token
  4. Copier la clé `hf_xxxxx`

### **2. Pollinations AI (Images gratuites)**
- **À QUOI ÇA SERT:** API gratuite illimitée pour générer images
- **CE QU'IL FAUT:** Aucune clé nécessaire (100% gratuit)
- **LIEN:** https://pollinations.ai/
- **CONFIGURATION:** Déjà intégré dans votre backend

---

## 🎵 **Génération Audio**

### **3. Freesound API (Sons et musiques)**
- **À QUOI ÇA SERT:** Récupérer sons, musiques et effets audio gratuits
- **CE QU'IL FAUT:**
  - `FREESOUND_API_KEY` = votre_api_key
- **LIEN:** https://freesound.org/apiv2/apply/
- **ÉTAPES:**
  1. Créer compte gratuit
  2. Aller sur "Apply for API key"
  3. Remplir le formulaire (projet personnel)
  4. Récupérer votre API key

### **4. Mozilla TTS (Text-to-Speech)**
- **À QUOI ÇA SERT:** Convertir texte en parole (installation locale)
- **CE QU'IL FAUT:** Installation Python
- **LIEN:** https://github.com/mozilla/TTS
- **INSTALLATION:** `pip install TTS`

---

## 📝 **Traitement de Texte**

### **5. TextRazor (Analyse de texte)**
- **À QUOI ÇA SERT:** Analyser sentiments, extraire mots-clés, détecter entités
- **CE QU'IL FAUT:**
  - `TEXTRAZOR_API_KEY` = votre_api_key
- **LIEN:** https://www.textrazor.com/signup
- **LIMITE GRATUITE:** 500 requêtes/jour
- **ÉTAPES:**
  1. S'inscrire gratuitement
  2. Confirmer email
  3. Récupérer API key dans dashboard

### **6. LibreTranslate (Traduction)**
- **À QUOI ÇA SERT:** Traduire textes entre 30+ langues
- **CE QU'IL FAUT:**
  - `LIBRETRANSLATE_URL` = https://libretranslate.com
- **LIEN:** https://libretranslate.com/
- **LIMITE:** 20 requêtes/minute (gratuit)

---

# 🌐 **2. RÉSEAUX SOCIAUX (8 APIs)**

### **7. YouTube Data API v3**
- **À QUOI ÇA SERT:** Récupérer infos vidéos, statistiques, commentaires YouTube
- **CE QU'IL FAUT:**
  - `YOUTUBE_API_KEY` = AIzaSyxxxxxxxxxx
- **LIEN:** https://console.developers.google.com/
- **ÉTAPES:**
  1. Créer projet Google
  2. Activer YouTube Data API v3
  3. Créer une clé API
  4. Copier la clé `AIzaSyxxxxxx`

### **8. Reddit API**
- **À QUOI ÇA SERT:** Récupérer posts, commentaires Reddit
- **CE QU'IL FAUT:**
  - `REDDIT_CLIENT_ID` = votre_client_id
  - `REDDIT_CLIENT_SECRET` = votre_client_secret
- **LIEN:** https://www.reddit.com/prefs/apps
- **ÉTAPES:**
  1. Connexion Reddit
  2. Créer nouvelle app (script)
  3. Récupérer client_id et client_secret

### **9. Twitter API v2**
- **À QUOI ÇA SERT:** Récupérer tweets, tendances, profils
- **CE QU'IL FAUT:**
  - `TWITTER_BEARER_TOKEN` = AAAAAAAAAxxxxx
- **LIEN:** https://developer.twitter.com/en/portal/dashboard
- **ÉTAPES:**
  1. Créer compte développeur Twitter
  2. Créer nouveau projet
  3. Générer Bearer Token
  4. Copier le token

### **10. Instagram Basic Display**
- **À QUOI ÇA SERT:** Récupérer posts Instagram utilisateur
- **CE QU'IL FAUT:**
  - `INSTAGRAM_CLIENT_ID` = votre_client_id
  - `INSTAGRAM_CLIENT_SECRET` = votre_client_secret
- **LIEN:** https://developers.facebook.com/apps/
- **ÉTAPES:**
  1. Créer app Facebook
  2. Ajouter Instagram Basic Display
  3. Récupérer client ID et secret

### **11. TikTok Research API**
- **À QUOI ÇA SERT:** Récupérer données publiques TikTok
- **CE QU'IL FAUT:**
  - `TIKTOK_CLIENT_KEY` = votre_client_key
- **LIEN:** https://developers.tiktok.com/
- **ÉTAPES:**
  1. S'inscrire TikTok for Developers
  2. Créer nouvelle app
  3. Demander accès Research API

### **12. LinkedIn API**
- **À QUOI ÇA SERT:** Récupérer profils, posts LinkedIn
- **CE QU'IL FAUT:**
  - `LINKEDIN_CLIENT_ID` = votre_client_id
  - `LINKEDIN_CLIENT_SECRET` = votre_client_secret
- **LIEN:** https://www.linkedin.com/developers/apps
- **ÉTAPES:**
  1. Créer app LinkedIn
  2. Récupérer client credentials

### **13. Pinterest API**
- **À QUOI ÇA SERT:** Récupérer pins, boards Pinterest
- **CE QU'IL FAUT:**
  - `PINTEREST_APP_ID` = votre_app_id
  - `PINTEREST_APP_SECRET` = votre_app_secret
- **LIEN:** https://developers.pinterest.com/
- **ÉTAPES:**
  1. Créer app Pinterest
  2. Récupérer App ID et Secret

### **14. Discord API**
- **À QUOI ÇA SERT:** Créer bots Discord, webhooks
- **CE QU'IL FAUT:**
  - `DISCORD_BOT_TOKEN` = votre_bot_token
- **LIEN:** https://discord.com/developers/applications
- **ÉTAPES:**
  1. Créer nouvelle application
  2. Aller dans Bot
  3. Créer bot et récupérer token

---

# 💰 **3. FINANCE & CRYPTO (6 APIs)**

### **15. CoinGecko API**
- **À QUOI ÇA SERT:** Prix cryptomonnaies, données marché
- **CE QU'IL FAUT:**
  - `COINGECKO_API_KEY` = CG-xxxxxx (optionnel pour gratuit)
- **LIEN:** https://www.coingecko.com/en/api
- **LIMITE:** 10-50 calls/minute gratuit

### **16. Fixer.io (Taux de change)**
- **À QUOI ÇA SERT:** Convertir devises, taux de change
- **CE QU'IL FAUT:**
  - `FIXER_ACCESS_KEY` = votre_access_key
- **LIEN:** https://fixer.io/signup/free
- **LIMITE:** 100 requêtes/mois gratuit

### **17. Alpha Vantage**
- **À QUOI ÇA SERT:** Données financières, actions, forex
- **CE QU'IL FAUT:**
  - `ALPHA_VANTAGE_API_KEY` = votre_api_key
- **LIEN:** https://www.alphavantage.co/support/#api-key
- **LIMITE:** 5 calls/minute gratuit

### **18. Stripe (Paiements)**
- **À QUOI ÇA SERT:** Traiter paiements par carte
- **CE QU'IL FAUT:**
  - `STRIPE_PUBLISHABLE_KEY` = pk_test_xxxxx
  - `STRIPE_SECRET_KEY` = sk_test_xxxxx
- **LIEN:** https://stripe.com/
- **ÉTAPES:**
  1. Créer compte Stripe
  2. Mode test activé par défaut
  3. Récupérer clés test dans Dashboard > Developers

### **19. PayPal API**
- **À QUOI ÇA SERT:** Paiements PayPal
- **CE QU'IL FAUT:**
  - `PAYPAL_CLIENT_ID` = votre_client_id
  - `PAYPAL_CLIENT_SECRET` = votre_client_secret
- **LIEN:** https://developer.paypal.com/
- **ÉTAPES:**
  1. Créer app sandbox
  2. Récupérer client credentials

### **20. Infura (Blockchain Ethereum)**
- **À QUOI ÇA SERT:** Accès blockchain Ethereum sans nœud
- **CE QU'IL FAUT:**
  - `INFURA_PROJECT_ID` = votre_project_id
  - `INFURA_PROJECT_SECRET` = votre_project_secret
- **LIEN:** https://infura.io/register
- **LIMITE:** 100K requêtes/jour gratuit

---

# 📊 **4. ANALYTICS & MONITORING (5 APIs)**

### **21. Google Analytics 4**
- **À QUOI ÇA SERT:** Analyser trafic site web
- **CE QU'IL FAUT:**
  - `GA4_MEASUREMENT_ID` = G-XXXXXXXXXX
- **LIEN:** https://analytics.google.com/
- **ÉTAPES:**
  1. Créer propriété GA4
  2. Récupérer Measurement ID

### **22. Google Search Console**
- **À QUOI ÇA SERT:** Données SEO, performance recherche
- **CE QU'IL FAUT:**
  - Verification de propriété site
- **LIEN:** https://search.google.com/search-console
- **ÉTAPES:**
  1. Ajouter propriété
  2. Vérifier propriété site

### **23. UptimeRobot**
- **À QUOI ÇA SERT:** Surveiller uptime de vos services
- **CE QU'IL FAUT:**
  - `UPTIMEROBOT_API_KEY` = votre_api_key
- **LIEN:** https://uptimerobot.com/signUp
- **LIMITE:** 50 moniteurs gratuit

### **24. Sentry (Monitoring erreurs)**
- **À QUOI ÇA SERT:** Tracker erreurs applications
- **CE QU'IL FAUT:**
  - `SENTRY_DSN` = https://xxxxx@sentry.io/xxxxx
- **LIEN:** https://sentry.io/signup/
- **LIMITE:** 5K erreurs/mois gratuit

### **25. PageSpeed Insights**
- **À QUOI ÇA SERT:** Analyser performance pages web
- **CE QU'IL FAUT:**
  - `PAGESPEED_API_KEY` = AIzaSyxxxxx (Google API)
- **LIEN:** Même clé que Google/YouTube API
- **LIMITE:** 25K requêtes/jour

---

# 📧 **5. COMMUNICATION (4 APIs)**

### **26. Mailgun (Email)**
- **À QUOI ÇA SERT:** Envoyer emails transactionnels
- **CE QU'IL FAUT:**
  - `MAILGUN_API_KEY` = votre_api_key
  - `MAILGUN_DOMAIN` = votre_domaine
- **LIEN:** https://www.mailgun.com/
- **LIMITE:** 5K emails/mois gratuit

### **27. Firebase FCM (Push notifications)**
- **À QUOI ÇA SERT:** Notifications push mobile/web
- **CE QU'IL FAUT:**
  - `FIREBASE_SERVER_KEY` = votre_server_key
- **LIEN:** https://console.firebase.google.com/
- **ÉTAPES:**
  1. Créer projet Firebase
  2. Activer Cloud Messaging
  3. Récupérer Server Key

### **28. Telegram Bot API**
- **À QUOI ÇA SERT:** Créer bots Telegram
- **CE QU'IL FAUT:**
  - `TELEGRAM_BOT_TOKEN` = votre_bot_token
- **LIEN:** https://t.me/BotFather
- **ÉTAPES:**
  1. Parler à @BotFather
  2. Créer nouveau bot avec /newbot
  3. Récupérer token

### **29. Twilio (SMS)**
- **À QUOI ÇA SERT:** Envoyer SMS
- **CE QU'IL FAUT:**
  - `TWILIO_ACCOUNT_SID` = ACxxxxxxx
  - `TWILIO_AUTH_TOKEN` = votre_auth_token
- **LIEN:** https://www.twilio.com/try-twilio
- **CRÉDIT:** $15 gratuit au signup

---

# 🎨 **6. CONTENU CRÉATIF (4 APIs)**

### **30. Unsplash API**
- **À QUOI ÇA SERT:** Photos haute qualité gratuites
- **CE QU'IL FAUT:**
  - `UNSPLASH_ACCESS_KEY` = votre_access_key
- **LIEN:** https://unsplash.com/developers
- **LIMITE:** 50 téléchargements/heure

### **31. Flaticon API**
- **À QUOI ÇA SERT:** Icônes vectorielles
- **CE QU'IL FAUT:**
  - `FLATICON_API_KEY` = votre_api_key
- **LIEN:** https://www.flaticon.com/api
- **LIMITE:** 100 téléchargements/jour

### **32. Google Fonts API**
- **À QUOI ÇA SERT:** Polices web gratuites
- **CE QU'IL FAUT:** Aucune clé (public)
- **LIEN:** https://fonts.google.com/
- **UTILISATION:** CDN direct

### **33. QR Server API**
- **À QUOI ÇA SERT:** Générer QR codes
- **CE QU'IL FAUT:** Aucune clé (gratuit illimité)
- **LIEN:** http://goqr.me/api/
- **UTILISATION:** URL directe

---

# 🔗 **7. AUTRES SERVICES ESSENTIELS (5 APIs)**

### **34. IP Geolocation API**
- **À QUOI ÇA SERT:** Localiser visiteurs par IP
- **CE QU'IL FAUT:**
  - `IPGEOLOCATION_API_KEY` = votre_api_key
- **LIEN:** https://ipgeolocation.io/
- **LIMITE:** 1K requêtes/jour gratuit

### **35. Weather API**
- **À QUOI ÇA SERT:** Données météo
- **CE QU'IL FAUT:**
  - `OPENWEATHER_API_KEY` = votre_api_key
- **LIEN:** https://openweathermap.org/api
- **LIMITE:** 60 calls/minute gratuit

### **36. News API**
- **À QUOI ÇA SERT:** Articles de presse
- **CE QU'IL FAUT:**
  - `NEWS_API_KEY` = votre_api_key
- **LIEN:** https://newsapi.org/
- **LIMITE:** 1K requêtes/jour gratuit

### **37. URL Shortener (TinyURL)**
- **À QUOI ÇA SERT:** Raccourcir URLs
- **CE QU'IL FAUT:**
  - `TINYURL_API_TOKEN` = votre_token
- **LIEN:** https://tinyurl.com/app/dev
- **LIMITE:** 600 requêtes/mois gratuit

### **38. GitHub API**
- **À QUOI ÇA SERT:** Gérer repos, releases
- **CE QU'IL FAUT:**
  - `GITHUB_TOKEN` = ghp_xxxxxxxxxxxx
- **LIEN:** https://github.com/settings/tokens
- **LIMITE:** 5K requêtes/heure

---

# 📋 **FICHIER .env COMPLET À CRÉER**

Créez un fichier `.env` dans votre projet avec toutes ces clés:

```bash
# === INTELLIGENCE ARTIFICIELLE ===
HUGGINGFACE_API_KEY=hf_votre_cle_ici
TEXTRAZOR_API_KEY=votre_textrazor_key
LIBRETRANSLATE_URL=https://libretranslate.com
FREESOUND_API_KEY=votre_freesound_key

# === RÉSEAUX SOCIAUX ===
YOUTUBE_API_KEY=AIzaSy_votre_cle_youtube
REDDIT_CLIENT_ID=votre_reddit_client_id
REDDIT_CLIENT_SECRET=votre_reddit_secret
TWITTER_BEARER_TOKEN=AAAAAAAAAvotre_twitter_token
INSTAGRAM_CLIENT_ID=votre_instagram_id
INSTAGRAM_CLIENT_SECRET=votre_instagram_secret
TIKTOK_CLIENT_KEY=votre_tiktok_key
LINKEDIN_CLIENT_ID=votre_linkedin_id
LINKEDIN_CLIENT_SECRET=votre_linkedin_secret
PINTEREST_APP_ID=votre_pinterest_id
PINTEREST_APP_SECRET=votre_pinterest_secret
DISCORD_BOT_TOKEN=votre_discord_bot_token

# === FINANCE & CRYPTO ===
COINGECKO_API_KEY=CG-votre_coingecko_key
FIXER_ACCESS_KEY=votre_fixer_key
ALPHA_VANTAGE_API_KEY=votre_alphavantage_key
STRIPE_PUBLISHABLE_KEY=pk_test_votre_stripe_public
STRIPE_SECRET_KEY=sk_test_votre_stripe_secret
PAYPAL_CLIENT_ID=votre_paypal_client_id
PAYPAL_CLIENT_SECRET=votre_paypal_secret
INFURA_PROJECT_ID=votre_infura_project_id
INFURA_PROJECT_SECRET=votre_infura_secret

# === ANALYTICS & MONITORING ===
GA4_MEASUREMENT_ID=G-VOTRE_GA4_ID
UPTIMEROBOT_API_KEY=votre_uptimerobot_key
SENTRY_DSN=https://votre_sentry_dsn@sentry.io/projet
PAGESPEED_API_KEY=AIzaSy_meme_que_google_api

# === COMMUNICATION ===
MAILGUN_API_KEY=votre_mailgun_key
MAILGUN_DOMAIN=votre_domaine_mailgun
FIREBASE_SERVER_KEY=votre_firebase_key
TELEGRAM_BOT_TOKEN=votre_telegram_bot_token
TWILIO_ACCOUNT_SID=AC_votre_twilio_sid
TWILIO_AUTH_TOKEN=votre_twilio_token

# === CONTENU CRÉATIF ===
UNSPLASH_ACCESS_KEY=votre_unsplash_key
FLATICON_API_KEY=votre_flaticon_key

# === AUTRES SERVICES ===
IPGEOLOCATION_API_KEY=votre_ip_geo_key
OPENWEATHER_API_KEY=votre_weather_key
NEWS_API_KEY=votre_news_key
TINYURL_API_TOKEN=votre_tinyurl_token
GITHUB_TOKEN=ghp_votre_github_token
```

---

# 🚀 **ORDRE D'ACTIVATION RECOMMANDÉ**

## **PRIORITÉ 1 - Immédiat (1h)**
1. ✅ Hugging Face (images IA)
2. ✅ YouTube API (social media)
3. ✅ Stripe (paiements)
4. ✅ Mailgun (emails)

## **PRIORITÉ 2 - Jour 1**
5. ✅ TextRazor (analyse texte)
6. ✅ Reddit + Twitter (social)
7. ✅ Firebase (notifications)
8. ✅ Unsplash (images)

## **PRIORITÉ 3 - Semaine 1**
9. ✅ Toutes les autres APIs selon besoins

---

**🎯 RÉSULTAT:** Avec ces 38 APIs gratuites, vous aurez 100% de fonctionnalité de base pour vos 53 agents IA et 680 microservices!

**📞 CONTACT:** Fahed Mlaiel - mlaiel@live.de