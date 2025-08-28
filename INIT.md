# django_ipssi_project — Guide de démarrage

Ce dépôt contient une application Django prête à l’emploi, exécutable avec Docker (recommandé pour un démarrage rapide) ou localement sans Docker.

Application web par défaut: http://localhost:8000/

## Prérequis

- Option Docker:
  - Docker et Docker Compose installés (Docker Desktop sous Windows/Mac, docker engine + docker-compose sous Linux)
- Option sans Docker:
  - Python 3.11
  - pip
  - (recommandé) virtualenv ou venv
- Optionnel:
  - make (GNU Make) pour utiliser les raccourcis fournis par le Makefile

Le code source Django se trouve dans le dossier `app/` (le `manage.py` est à `app/manage.py`). Le port HTTP utilisé est `8000`.

---

## Démarrer avec Docker (recommandé)

1) Construire et lancer les services (en mode développement avec rechargement grâce au volume monté):

```bash
make docker-up-build
# ou
# docker-compose up --build
```

2) Accéder à l’application:

- http://localhost:8000/

3) Arrêter:

- Arrêt en premier plan: Ctrl + C
- Ou en arrière-plan: `docker-compose up -d` pour démarrer, puis `docker-compose down` pour arrêter et nettoyer les conteneurs.

Notes:
- Le fichier `docker-compose.yml` mappe le répertoire `./app` dans le conteneur (`/app`). Les modifications de code sont rechargées automatiquement par le serveur Django (dev server).
- Le `Dockerfile` expose le port 8000 et lance: `python manage.py runserver 0.0.0.0:8000`.

### Commandes utiles avec Docker

Vous pouvez utiliser Make pour simplifier ces commandes.

- Exécuter des migrations (si nécessaire):

```bash
make docker-migrate
# équivalent: docker-compose exec web python manage.py migrate
```

- Créer un superutilisateur:

```bash
make docker-superuser
# équivalent: docker-compose exec web python manage.py createsuperuser
```

- Ouvrir un shell Django:

```bash
make docker-shell
# équivalent: docker-compose exec web python manage.py shell
```

- Lancer / arrêter les conteneurs:

```bash
make docker-up-build   # build + run
make docker-up-d       # run détaché
make docker-down       # arrêt + nettoyage
make docker-logs       # suivre les logs
```

---

## Démarrer sans Docker (exécution locale)

### Option rapide avec Make

Sur macOS/Linux (ou Windows via Git Bash), vous pouvez utiliser Make:

```bash
make install   # crée .venv si nécessaire + installe les dépendances
make migrate   # applique les migrations
make run       # lance le serveur sur 0.0.0.0:8000
```

Si vous préférez, suivez les étapes manuelles ci-dessous.

1) Se placer à la racine du projet:

```bash
cd /chemin/vers/django_ipssi_project
```

2) Créer un environnement virtuel Python 3.11 et l’activer:

- macOS / Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

- Windows (PowerShell):

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3) Installer les dépendances:

```bash
pip install -r requirements.txt
```

4) Appliquer les migrations (la base SQLite se trouve par défaut dans `app/db.sqlite3`):

```bash
cd app
python manage.py migrate
```

5) Lancer le serveur de développement:

```bash
python manage.py runserver 0.0.0.0:8000
```

6) Ouvrir l’application:

- http://localhost:8000/

7) (Optionnel) Créer un superutilisateur:

```bash
python manage.py createsuperuser
```

8) Arrêter le serveur:

- Ctrl + C dans le terminal où il s’exécute.

---

## Variables d’environnement et configuration

- Le projet utilise la configuration Django par défaut (voir `app/app/settings.py`).
- Pour des environnements plus avancés (ex: DEBUG, SECRET_KEY, ALLOWED_HOSTS), adaptez `settings.py` ou utilisez des variables d’environnement selon vos besoins.

---

## Dépannage

- Le port 8000 est déjà utilisé:
  - Fermez l’application qui occupe ce port ou changez le port: `python manage.py runserver 0.0.0.0:8001` (et ajustez aussi le mapping `ports` dans docker-compose si vous utilisez Docker).

- Modifications non prises en compte avec Docker:
  - Vérifiez que le service tourne et que le volume `./app:/app` est bien monté. Redémarrez: `docker-compose restart web`.

- Problèmes de dépendances en local:
  - Recréez l’environnement virtuel et réinstallez: `rm -rf .venv && python3.11 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.

---

## Structure du projet (extrait)

```
.
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── app/
    ├── manage.py
    ├── db.sqlite3
    └── app/
        ├── settings.py
        ├── urls.py
        ├── wsgi.py
        └── asgi.py
```

Bon développement !
