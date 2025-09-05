# 🔍 CHECKLIST DIAGNOSTIC BACKEND AINFLUE
## Tests Approfondis pour Résoudre Définitivement les Problèmes

### 📋 PHASE 1: ANALYSE ENVIRONNEMENT
- [ ] **1.1** Vérifier Python version et modules installés
  ```bash
  python --version
  pip list | grep -E "(fastapi|uvicorn|pydantic)"
  ```

- [ ] **1.2** Tester les imports critiques
  ```bash
  python -c "import fastapi; print('FastAPI OK')"
  python -c "import uvicorn; print('Uvicorn OK')"
  python -c "from dotenv import load_dotenv; print('DotEnv OK')"
  ```

- [ ] **1.3** Vérifier les variables d'environnement
  ```bash
  cat .env | grep CORS
  echo $CORS_ORIGINS
  ```

### 📋 PHASE 2: ANALYSE STRUCTURE FICHIERS
- [ ] **2.1** Vérifier l'intégrité du main.py
  ```bash
  python -m py_compile main.py
  python -c "import main; print('Import main.py OK')"
  ```

- [ ] **2.2** Tester la création de l'app FastAPI
  ```bash
  python -c "from main import app; print(f'App type: {type(app)}')"
  ```

- [ ] **2.3** Vérifier les endpoints définis
  ```bash
  python -c "from main import app; print([route.path for route in app.routes])"
  ```

### 📋 PHASE 3: TESTS RÉSEAU ET PORTS
- [ ] **3.1** Vérifier que le port 8000 est libre
  ```bash
  lsof -i :8000
  netstat -tulpn | grep :8000
  ```

- [ ] **3.2** Tester le bind d'adresse
  ```bash
  python -c "import socket; s=socket.socket(); s.bind(('0.0.0.0', 8000)); print('Port OK'); s.close()"
  ```

### 📋 PHASE 4: TESTS DÉMARRAGE SERVEUR
- [ ] **4.1** Démarrage avec gestion d'erreurs détaillée
  ```bash
  cd /workspaces/Ainflue
  python -c "
  import sys
  import traceback
  try:
      from main import app
      import uvicorn
      print('✓ Imports OK')
      uvicorn.run(app, host='0.0.0.0', port=8000, log_level='debug')
  except Exception as e:
      print(f'❌ ERREUR: {e}')
      traceback.print_exc()
  "
  ```

- [ ] **4.2** Test de démarrage en mode debug
  ```bash
  python -u main.py 2>&1 | tee debug_output.log
  ```

### 📋 PHASE 5: TESTS ENDPOINTS INDIVIDUELS
- [ ] **5.1** Test endpoint racine
  ```bash
  python -c "
  from main import app
  from fastapi.testclient import TestClient
  client = TestClient(app)
  response = client.get('/')
  print(f'Status: {response.status_code}')
  print(f'Response: {response.json()}')
  "
  ```

- [ ] **5.2** Test endpoint health
  ```bash
  python -c "
  from main import app
  from fastapi.testclient import TestClient
  client = TestClient(app)
  response = client.get('/health')
  print(f'Health Status: {response.status_code}')
  print(f'Health Response: {response.json()}')
  "
  ```

- [ ] **5.3** Test tous les endpoints
  ```bash
  python -c "
  from main import app
  from fastapi.testclient import TestClient
  client = TestClient(app)
  endpoints = ['/', '/health', '/status', '/agents', '/crawlers', '/analytics/revenue']
  for endpoint in endpoints:
      try:
          response = client.get(endpoint)
          print(f'{endpoint}: {response.status_code} ✓')
      except Exception as e:
          print(f'{endpoint}: ERREUR - {e} ❌')
  "
  ```

### 📋 PHASE 6: TESTS CORS ET MIDDLEWARE
- [ ] **6.1** Vérifier configuration CORS
  ```bash
  python -c "
  from main import app
  for middleware in app.middleware_stack:
      print(f'Middleware: {type(middleware).__name__}')
  "
  ```

- [ ] **6.2** Test requête CORS
  ```bash
  python -c "
  from main import app
  from fastapi.testclient import TestClient
  client = TestClient(app)
  headers = {'Origin': 'http://localhost:3000'}
  response = client.get('/health', headers=headers)
  print(f'CORS Test: {response.status_code}')
  print(f'CORS Headers: {dict(response.headers)}')
  "
  ```

### 📋 PHASE 7: TESTS PERFORMANCE ET STABILITÉ
- [ ] **7.1** Test charge multiple requêtes
  ```bash
  python -c "
  from main import app
  from fastapi.testclient import TestClient
  import time
  client = TestClient(app)
  print('Test de charge...')
  for i in range(10):
      start = time.time()
      response = client.get('/health')
      duration = time.time() - start
      print(f'Requête {i+1}: {response.status_code} en {duration:.3f}s')
  "
  ```

- [ ] **7.2** Test mémoire et ressources
  ```bash
  python -c "
  import psutil
  import os
  process = psutil.Process(os.getpid())
  print(f'Mémoire utilisée: {process.memory_info().rss / 1024 / 1024:.2f} MB')
  print(f'CPU utilisé: {process.cpu_percent()}%')
  "
  ```

### 📋 PHASE 8: TESTS INTÉGRATION COMPLÈTE
- [ ] **8.1** Démarrage serveur en arrière-plan
  ```bash
  cd /workspaces/Ainflue
  python main.py &
  SERVER_PID=$!
  sleep 5
  ```

- [ ] **8.2** Test connectivité externe
  ```bash
  curl -v http://localhost:8000/health
  curl -v http://localhost:8000/status
  curl -v http://localhost:8000/agents
  ```

- [ ] **8.3** Test stabilité 60 secondes
  ```bash
  for i in {1..20}; do
    curl -s http://localhost:8000/health > /dev/null
    if [ $? -eq 0 ]; then
      echo "Test $i: ✓"
    else
      echo "Test $i: ❌"
    fi
    sleep 3
  done
  ```

- [ ] **8.4** Nettoyage
  ```bash
  kill $SERVER_PID
  ```

### 📋 PHASE 9: DIAGNOSTIC ERREURS COMMUNES
- [ ] **9.1** Erreur "Address already in use"
  ```bash
  lsof -ti:8000 | xargs -r kill -9
  echo "Port 8000 libéré"
  ```

- [ ] **9.2** Erreur import modules
  ```bash
  pip install --upgrade fastapi uvicorn python-dotenv
  ```

- [ ] **9.3** Erreur permissions
  ```bash
  ls -la main.py
  chmod +x main.py
  ```

### 📋 PHASE 10: SOLUTIONS DÉFINITIVES
- [ ] **10.1** Si problème d'imports → Corriger les dépendances
- [ ] **10.2** Si problème de port → Utiliser port alternatif (8001, 8002)
- [ ] **10.3** Si problème CORS → Configurer allow_origins=["*"]
- [ ] **10.4** Si instabilité → Désactiver reload, utiliser workers=1

### 📊 RAPPORT FINAL
```
✅ ÉLÉMENTS FONCTIONNELS:
- [ ] Python et modules installés
- [ ] main.py sans erreurs de syntaxe
- [ ] FastAPI app créée correctement
- [ ] Tous les endpoints répondent
- [ ] CORS configuré
- [ ] Serveur stable pendant 60s
- [ ] Tests de charge réussis

❌ PROBLÈMES IDENTIFIÉS:
- [ ] Liste des erreurs trouvées
- [ ] Actions correctives nécessaires

🎯 ACTIONS PRIORITAIRES:
1. ________________________________
2. ________________________________
3. ________________________________
```

### 🚀 COMMANDES DE DÉMARRAGE DÉFINITIVES
Après tous les tests, utiliser cette séquence :
```bash
cd /workspaces/Ainflue
pkill -f "python.*main.py" 2>/dev/null
lsof -ti:8000 | xargs -r kill -9
python main.py
```
