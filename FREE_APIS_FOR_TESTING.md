# 🆓 APIs EXTERNES GRATUITES POUR TESTS RÉELS - AINFLUENCER

**Date:** 24 septembre 2025  
**Projet:** Ainfluencer Platform  
**Objectif:** Tests réels avec APIs gratuites  

---

## 🎯 APIS GRATUITES RECOMMANDÉES (PAR CATÉGORIE)

### 🤖 1. INTELLIGENCE ARTIFICIELLE (GRATUIT)

#### 1.1 Hugging Face API 🆓 **RECOMMANDÉ**
```env
# Variables d'environnement
HUGGINGFACE_API_KEY=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
HUGGINGFACE_MODEL=gpt2-large
```
- **Endpoint:** `https://api-inference.huggingface.co/models/gpt2`
- **Gratuit:** 30,000 requests/mois
- **Modèles disponibles:** GPT-2, BERT, T5, CLIP, etc.
- **Usage:** Génération de contenu, classification, embedding
- **Inscription:** https://huggingface.co/join

#### 1.2 Google Gemini Free Tier 🆓
```env
# Variables d'environnement  
GOOGLE_GEMINI_API_KEY=AIzaSyDJnBaaDrVk-nthKu3q6VEpnqVonhPGe_4
GOOGLE_GEMINI_MODEL=gemini-pro
```
- **Gratuit:** 15 requests/minute, 1M tokens/jour
- **Endpoint:** `https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent`
- **Usage:** Génération de texte, analyse d'images
- **Inscription:** https://makersuite.google.com/app/apikey

#### 1.3 Cohere Free Tier 🆓
```env
COHERE_API_KEY=nAJZFzbtiRM3sDEPISFLVL6l3Law9hxoiutAFcWT
```
- **Gratuit:** 100 requests/minute, 1000 requests/mois
- **Endpoint:** `https://api.cohere.ai/v1/generate`
- **Usage:** Génération de texte, embeddings, classification
- **Inscription:** https://cohere.com/

---

### 📱 2. RÉSEAUX SOCIAUX (GRATUIT/FREEMIUM)

#### 2.1 YouTube Data API v3 🆓 **EXCELLENT**
```env
YOUTUBE_API_KEY=AIzaSyDZmVYU65zQDbtmSa8egSOuFAaRwpcSYn4
YOUTUBE_CLIENT_ID=329063366855-v3s5vcac3oopnev9kh81skkfoe43ijed.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=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
```
- **Gratuit:** 10,000 quota units/jour (largement suffisant)
- **Fonctionnalités:** Upload, analytics, gestion de chaîne
- **Inscription:** https://console.cloud.google.com/apis/library/youtube.googleapis.com

#### 2.2 TikTok API for Developers 🆓
```env
TIKTOK_CLIENT_KEY=xxxxxxxxxxxxxxxxxx
TIKTOK_CLIENT_SECRET=xxxxxxxxxxxxxxxxxx
```
- **Gratuit:** Basic access (limitations sur volume)
- **Fonctionnalités:** Profil, videos, analytics basiques
- **Inscription:** https://developers.tiktok.com/

#### 2.3 Twitter API v2 Free Tier 🆓 ⚠️ **LIMITÉ**
```env
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAxxxxxxxxxxxxxxxxxx
TWITTER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxx
TWITTER_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxx
TWITTER_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxx
```
- **Gratuit:** 500,000 tweets/mois (lecture seule)
- **Limitations:** Pas de publication en gratuit (nécessite plan payant)
- **Use Cases:** Analytics, recherche de tendances, insights audience
- **Application Required:** Processus d'approbation Developer Agreement
- **Documentation:** Voir `TWITTER_X_API_USE_CASE.md` pour use cases détaillés
- **Inscription:** https://developer.twitter.com/en/portal/dashboard

---

### 💳 3. PAIEMENTS TEST (SANDBOX GRATUIT)

#### 3.1 Stripe Test Mode 🆓 **PARFAIT**
```env
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
- **100% Gratuit en mode test**
- **Cartes test:** 4242 4242 4242 4242 (Visa), 5555 5555 5555 4444 (Mastercard)
- **Fonctionnalités complètes:** Paiements, abonnements, webhooks
- **Inscription:** https://stripe.com/

#### 3.2 PayPal Sandbox 🆓 **PARFAIT**
```env
PAYPAL_CLIENT_ID=Axxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
PAYPAL_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
PAYPAL_MODE=sandbox
```
- **100% Gratuit en sandbox**
- **Comptes test fournis** par PayPal
- **Inscription:** https://developer.paypal.com/

#### 3.3 Square Sandbox 🆓
```env
SQUARE_ACCESS_TOKEN=EAAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SQUARE_APPLICATION_ID=sandbox-sq0idb-xxxxxxxxxxxxxxxxxx
```
- **Gratuit en mode sandbox**
- **Inscription:** https://developer.squareup.com/

---

### 📧 4. EMAIL & SMS (GRATUIT)

#### 4.1 Resend 🆓 **EXCELLENT**
```env
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
- **Gratuit:** 3,000 emails/mois
- **Excellent deliverability**
- **Inscription:** https://resend.com/

#### 4.2 SendGrid Free Tier 🆓
```env
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
- **Gratuit:** 100 emails/jour
- **Inscription:** https://sendgrid.com/

#### 4.3 Twilio Free Trial 🆓
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1xxxxxxxxxx
```
- **Gratuit:** $15.50 de crédit + numéro test
- **SMS vers numéros vérifiés uniquement en trial**
- **Inscription:** https://twilio.com/

---

### 🗄️ 5. BASE DE DONNÉES (GRATUIT)

#### 5.1 Supabase Free Tier 🆓 **EXCELLENT**
```env
SUPABASE_URL=https://xxxxxxxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxxx
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxxx
```
- **Gratuit:** 500MB DB, 2GB stockage, 5GB bandwidth
- **PostgreSQL + Auth + Storage + Realtime**
- **Inscription:** https://supabase.com/

#### 5.2 PlanetScale Free Tier 🆓
```env
PLANETSCALE_DB_URL=mysql://xxxxxx:xxxxxx@xxxxxx.planetscale.sh:3306/xxxxxx?ssl={"rejectUnauthorized":true}
```
- **Gratuit:** 1 base, 5GB stockage, 1B rows reads/mois
- **MySQL serverless**
- **Inscription:** https://planetscale.com/

#### 5.3 MongoDB Atlas Free Tier 🆓
```env
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/database
```
- **Gratuit:** 512MB stockage
- **Inscription:** https://mongodb.com/atlas

---

### 📊 6. ANALYTICS & MONITORING (GRATUIT)

#### 6.1 Google Analytics 4 🆓
```env
GOOGLE_ANALYTICS_MEASUREMENT_ID=G-XXXXXXXXXX
GOOGLE_ANALYTICS_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
```
- **100% Gratuit**
- **Analytics web complet**
- **Inscription:** https://analytics.google.com/

#### 6.2 Sentry Free Tier 🆓
```env
SENTRY_DSN=https://xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@o000000.ingest.sentry.io/0000000
```
- **Gratuit:** 5,000 errors/mois
- **Monitoring d'erreurs**
- **Inscription:** https://sentry.io/

#### 6.3 LogRocket Free Tier 🆓
```env
LOGROCKET_APP_ID=xxxxxx/project-name
```
- **Gratuit:** 1,000 sessions/mois
- **Session replay**
- **Inscription:** https://logrocket.com/

---

### 🔍 7. RECHERCHE & DONNÉES (GRATUIT)

#### 7.1 Algolia Free Tier 🆓
```env
ALGOLIA_APPLICATION_ID=XXXXXXXXXX
ALGOLIA_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
- **Gratuit:** 10,000 requests/mois, 10,000 records
- **Recherche ultra-rapide**
- **Inscription:** https://algolia.com/

#### 7.2 Pinecone Free Tier 🆓
```env
PINECONE_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
PINECONE_ENVIRONMENT=us-west1-gcp
```
- **Gratuit:** 1M vectors, 1 index
- **Vector database pour IA**
- **Inscription:** https://pinecone.io/

---

## 🛠️ SCRIPT D'INSTALLATION RAPIDE

```bash
# Créer le fichier .env avec les APIs gratuites
cat > .env.testing << EOF
# IA & ML (Gratuit)
HUGGINGFACE_API_KEY=hf_VOTRE_CLE_ICI
GOOGLE_GEMINI_API_KEY=AIzaSy_VOTRE_CLE_ICI

# Réseaux Sociaux (Gratuit)
YOUTUBE_API_KEY=AIzaSy_VOTRE_CLE_ICI

# Paiements Test (Gratuit)
STRIPE_PUBLISHABLE_KEY=pk_test_VOTRE_CLE_ICI
STRIPE_SECRET_KEY=sk_test_VOTRE_CLE_ICI

# Email (Gratuit) 
RESEND_API_KEY=re_VOTRE_CLE_ICI

# Base de données (Gratuit)
SUPABASE_URL=https://VOTRE_PROJET.supabase.co
SUPABASE_ANON_KEY=VOTRE_CLE_ICI

# Analytics (Gratuit)
GOOGLE_ANALYTICS_MEASUREMENT_ID=G-XXXXXXXXXX
SENTRY_DSN=https://VOTRE_DSN@sentry.io/PROJET

# Recherche (Gratuit)
ALGOLIA_APPLICATION_ID=VOTRE_APP_ID
ALGOLIA_API_KEY=VOTRE_CLE_ICI
EOF

echo "✅ Fichier .env.testing créé avec APIs gratuites!"
```

---

## 📋 CHECKLIST D'INSCRIPTION

### ✅ Actions à faire (15-30 minutes)

1. **🤖 IA & ML**
   - [ ] Créer compte Hugging Face → Récupérer API key
   - [ ] Activer Google AI Studio → Récupérer Gemini API key

2. **📱 Réseaux Sociaux** 
   - [ ] Google Cloud Console → Activer YouTube Data API
   - [ ] TikTok Developers → Demander accès API

3. **💳 Paiements**
   - [ ] Stripe → Créer compte → Récupérer clés test
   - [ ] PayPal Developer → Créer app sandbox

4. **📧 Communication**
   - [ ] Resend → Créer compte → API key
   - [ ] Twilio → Trial account

5. **🗄️ Données**
   - [ ] Supabase → Nouveau projet → Récupérer URLs/keys
   - [ ] Sentry → Nouveau projet → DSN

**🎯 RÉSULTAT:** Plateforme Ainfluencer testable avec vraies APIs mais 100% gratuit!

---

## 💡 CONSEILS POUR LES TESTS

### 🔧 Variables d'environnement essentielles
```bash
# Charger le fichier de test
export $(cat .env.testing | xargs)

# Vérifier les clés
echo "Hugging Face: ${HUGGINGFACE_API_KEY:0:10}..."
echo "YouTube: ${YOUTUBE_API_KEY:0:10}..."
echo "Stripe Test: ${STRIPE_SECRET_KEY:0:15}..."
```

### 🧪 Tests recommandés
1. **IA:** Test génération de contenu avec Hugging Face
2. **YouTube:** Upload d'une vidéo test
3. **Paiements:** Création d'un paiement test Stripe  
4. **Email:** Envoi d'email avec Resend
5. **Analytics:** Tracking d'événements

**🎯 Ces APIs gratuites permettent de tester 90% des fonctionnalités d'Ainfluencer sans aucun coût!**