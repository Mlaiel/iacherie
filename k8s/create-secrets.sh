#!/bin/bash

# Script pour créer les Kubernetes Secrets avec toutes les 61 APIs
# À exécuter dans Google Cloud Shell après avoir configuré kubectl

set -e

echo "=========================================="
echo "🔐 Création des Secrets Kubernetes"
echo "=========================================="
echo ""

# Vérifier que kubectl est configuré
if ! kubectl get nodes &> /dev/null; then
    echo "❌ Erreur: kubectl n'est pas configuré correctement"
    echo "Exécutez: gcloud container clusters get-credentials iacherie-cluster --region=europe-west1"
    exit 1
fi

# Vérifier que le namespace existe
if ! kubectl get namespace iacherie-prod &> /dev/null; then
    echo "📦 Création du namespace iacherie-prod..."
    kubectl create namespace iacherie-prod
fi

echo "🔑 Création du secret avec toutes les APIs..."

# Créer le secret avec TOUTES les clés API
kubectl create secret generic iacherie-api-keys \
  --namespace=iacherie-prod \
  --from-literal=SECRET_KEY='iacherie_enterprise_secret_key_for_production_2025' \
  --from-literal=JWT_SECRET='jwt_secret_enterprise_production' \
  --from-literal=POSTGRES_PASSWORD='iacherie_secure_db_password_2025' \
  --from-literal=REDIS_PASSWORD='iacherie_redis_password_2025' \
  \
  --from-literal=OPENAI_API_KEY='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' \
  --from-literal=HUGGINGFACE_API_KEY='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' \
  --from-literal=HUGGINGFACE_READ_TOKEN='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' \
  --from-literal=HUGGINGFACE_WRITE_TOKEN='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' \
  --from-literal=HUGGINGFACE_CLIENT_SECRET='0eeef090-4619-4bce-af07-e1ea33052c90' \
  \
  --from-literal=GOOGLE_GEMINI_API_KEY='AIzaSyB7uD-W_h7jMnVErySX1bBXpaq9IBKUScw' \
  --from-literal=COHERE_API_KEY='3jzgTIpHY3Mhq5yZGMnjh0p4ztB4a1zgOxfT7j1a' \
  --from-literal=ANTHROPIC_API_KEY='sk-ant-api03-xxx' \
  --from-literal=REPLICATE_API_KEY='r8_xxx' \
  \
  --from-literal=STABILITY_API_KEY='sk-27IUt5x6MOaD6Pi9QH50bQqBdNemO9LNLD0SaEF4lp3nqPZB' \
  --from-literal=LEONARDO_API_KEY='leonardo-xxx' \
  --from-literal=RUNWAYML_API_KEY='key_e0ed28320d6a292d28b27922e2512fe732453aa2c21d2a48c35cea1b837592be279fe5ca78619e5b0d973961c9b150d5d01e5201be957f4f84284e6517d8e8eb' \
  --from-literal=UNSPLASH_ACCESS_KEY='WKxWKnSt5q7NjbjNAwlcAeOApEs2RfGh6-6cjzwJokA' \
  --from-literal=UNSPLASH_SECRET_KEY='22HtLoj2sMxtGP8H8aTstFhCteH-hLG3bdCCJfCXWkg' \
  --from-literal=FREEPIK_API_KEY='FPSX99b0c97913639d47ba9ff53ca971611c' \
  --from-literal=FLATICON_API_KEY='FPSX99b0c97913639d47ba9ff53ca971611c' \
  --from-literal=PEXELS_API_KEY='pexels-xxx' \
  \
  --from-literal=ELEVENLABS_API_KEY='sk_71841f241f8962ecf0b9626c69aaf3394427146b8809934b' \
  --from-literal=FREESOUND_API_KEY='vgspKtAIP6NcQc995U8dHrOApuckeO0sX0DRMzn3' \
  --from-literal=FREESOUND_CLIENT_ID='DC7XnlZJBpt8CaCLHzdv' \
  --from-literal=SPOTIFY_CLIENT_ID='spotify-xxx' \
  --from-literal=SPOTIFY_CLIENT_SECRET='spotify-secret-xxx' \
  \
  --from-literal=TWITTER_API_KEY='8vGK4rE2hNKXZcJFqRL0e7MYT' \
  --from-literal=TWITTER_API_KEY_SECRET='mXP9sKF3qW7zNVE8jRY6lHB4tD2cGfAs1oUqZh9iTxLpeMnJvC' \
  --from-literal=TWITTER_ACCESS_TOKEN='1970823085877043200-Lq8Nd3Wv5MzKxY4FcHj2TpBgRu9NaV6X' \
  --from-literal=TWITTER_ACCESS_TOKEN_SECRET='7BqNx3MzHwK9jFpL4cRyVt8sG2nWq5aEfUzXb6dYhJmTkPoIvC' \
  --from-literal=TWITTER_BEARER_TOKEN='AAAAAAAAAAAAAAAAAAAAAP9o4QEAAAAAUoZudouoqEbPzTog6u3zg348Phc%3DfLmev3E3Uyt7QzYaKogQJQSprvCAyXhJyFO8lGqBTOshq2Vvnq' \
  --from-literal=TWITTER_CLIENT_SECRET='c52JNRaU7axAaz0cnvbyiILDCLIl6UkSI0KzfLqLCcWBKhsWwL' \
  \
  --from-literal=INSTAGRAM_APP_SECRET='3c7a0bd91e823e82088666b7821e565a' \
  --from-literal=INSTAGRAM_ACCESS_TOKEN='EAAJl94obWKkBPjhz1CHthndRA4yqwBLpyOB7ZAJD1b3ZAERYr4eg2SpJIaHUoZAGQfZAkJsyp5T6J3VxKQsyaSLg5FFiOLCORslKmpZA80LaGj9dRAKlUdCDNmdvESniRIXKNDTg1hHkH9WkXSQNQrLrTnqcHMdxtCNxpoC9WvwaIcotma0k9wtGDWZCBAa0sZBWpjuK43k1EZCH9FqoDgDUqsjIpITqQQUYJ5d48E5VZChJz2lq3qyZB5OCbVuwGkZAAZDZD' \
  --from-literal=INSTAGRAM_CLIENT_SECRET='3c7a0bd91e823e82088666b7821e565a' \
  \
  --from-literal=FACEBOOK_APP_SECRET='ceb72052bcbbde0420e345b821e36833' \
  --from-literal=FACEBOOK_ACCESS_TOKEN='EAAJl94obWKkBPjhz1CHthndRA4yqwBLpyOB7ZAJD1b3ZAERYr4eg2SpJIaHUoZAGQfZAkJsyp5T6J3VxKQsyaSLg5FFiOLCORslKmpZA80LaGj9dRAKlUdCDNmdvESniRIXKNDTg1hHkH9WkXSQNQrLrTnqcHMdxtCNxpoC9WvwaIcotma0k9wtGDWZCBAa0sZBWpjuK43k1EZCH9FqoDgDUqsjIpITqQQUYJ5d48E5VZChJz2lq3qyZB5OCbVuwGkZAAZDZD' \
  \
  --from-literal=DISCORD_BOT_TOKEN='MTQyMjM0OTkzNjkzODMyNDA1Mg.GaYmJg.yNSEfeua4KdM3huvLgOBWvbSe4eGChNqwF6RLA' \
  --from-literal=DISCORD_PUBLIC_KEY='bbd18a7882997874701a36cf26103f850563b2ae40bf76ac1df87116d59a7cc4' \
  --from-literal=DISCORD_CLIENT_SECRET='qYDPCHughQ8DYqC85KpdqkqiVfApbdbk' \
  \
  --from-literal=REDDIT_CLIENT_SECRET='NTOnMfOokzIA9B_TvbZ-FuBigH3kcA' \
  \
  --from-literal=YOUTUBE_API_KEY='AIzaSyDZmVYU65zQDbtmSa8egSOuFAaRwpcSYn4' \
  --from-literal=YOUTUBE_CLIENT_SECRET='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' \
  \
  --from-literal=RESEND_API_KEY='re_R2ezj125_7hX1R19ZPAHuTPA8sNep7YnM' \
  --from-literal=SENDGRID_API_KEY='SG.xxx' \
  --from-literal=TWILIO_ACCOUNT_SID='ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' \
  --from-literal=TWILIO_AUTH_TOKEN='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' \
  \
  --from-literal=TINYURL_API_KEY='V6nENR9gI5ESnWfKRORk715xHV2kywjjvAPkry5OhlDamik7hM5X1FMfjB7u' \
  --from-literal=IPGEOLOCATION_API_KEY='3d09384c67c14f3d96b20d1b9e082c34' \
  --from-literal=TEXTRAZOR_API_KEY='095fa25a57d1822ef373e299e9ad4ca2062f1284e7b2024685c7dd3a' \
  --from-literal=TYPEFORM_API_KEY='tfp_HeSFt7Rfz3iYxPJG1gG52vXFx5pcAk5E8XLxU1UpbDHA_3pf1kvVyLWURTB' \
  --from-literal=STRIPE_WEBHOOK_SECRET='whsec_xxx' \
  \
  --from-literal=GOOGLE_ANALYTICS_API_SECRET='1JmMyxhjRZaYsYtMnVQzgg' \
  --from-literal=PAGESPEED_API_KEY='AIzaSyDZmVYU65zQDbtmSa8egSOuFAaRwpcSYn4' \
  --from-literal=ALGOLIA_API_KEY='5002d9c53aa2cd1cdbbd40d440947c6f' \
  --from-literal=SENTRY_DSN='https://e4d3be4623ada1b28cad9035f3b0cdd5@o4510074853457920.ingest.de.sentry.io/4510074859094096' \
  --from-literal=MIXPANEL_TOKEN='mixpanel-xxx' \
  \
  --from-literal=SUPABASE_ANON_KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhlYnp6cmFibXNldWVnemNreXBpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg3MTc0MTYsImV4cCI6MjA3NDI5MzQxNn0.ae87xApCjZCl_Zkj_NGkJioVifd4Mn_BWPJgpc6zb-M' \
  --from-literal=SUPABASE_SERVICE_KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhlYnp6cmFibXNldWVnemNreXBpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODcxNzQxNiwiZXhwIjoyMDc0MjkzNDE2fQ.HeAdETv3ERKFsw1JWXPRTU80YPp2EzPZ0O6ZQ6kaI8k' \
  \
  --from-literal=AZURE_CLIENT_SECRET='Tmh8Q~fzZGAfPTs2gA5u4guIdXeG3AGCJg4jLaVI' \
  \
  --from-literal=PINECONE_API_KEY='pcsk_3nrQ14_Sen3JoVS7FZZaM6dK56BH41PxKT1M9U2Y51ncnMhxN6awVXcraA69kaDNBSQUks' \
  \
  --from-literal=GITHUB_TOKEN='ghu_SvQA3qYLUVdlnHOMUJJncJEwazACuj1Q0cBi' \
  \
  --from-literal=CLOUDINARY_API_KEY='cloudinary-xxx' \
  --from-literal=CLOUDINARY_API_SECRET='cloudinary-secret-xxx' \
  --from-literal=DEEPL_API_KEY='deepl-xxx' \
  --from-literal=LOGROCKET_APP_ID='logrocket-xxx' \
  --from-literal=LOOM_API_KEY='loom-xxx' \
  --from-literal=RAPIDAPI_KEY='rapidapi-xxx' \
  --from-literal=SQUARE_ACCESS_TOKEN='square-xxx' \
  --from-literal=VIMEO_ACCESS_TOKEN='vimeo-xxx' \
  --from-literal=VIMEO_CLIENT_SECRET='vimeo-secret-xxx' \
  --dry-run=client -o yaml | kubectl apply -f -

echo ""
echo "✅ Secret créé avec succès!"
echo ""
echo "🔍 Vérification:"
kubectl get secret iacherie-api-keys -n iacherie-prod
echo ""
echo "📊 Nombre de clés stockées:"
kubectl get secret iacherie-api-keys -n iacherie-prod -o json | jq '.data | length'
echo ""
echo "=========================================="
echo "✅ Configuration terminée!"
echo "=========================================="
