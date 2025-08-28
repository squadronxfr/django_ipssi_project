# Makefile pour simplifier les commandes courantes
# Utilisation: `make <cible>`

# ------------- Variables -------------
APP_DIR := app
MANAGE := $(APP_DIR)/manage.py
PY := python
PIP := pip
VENV := .venv
SHELL := /bin/sh

# ------------- Aide -------------
.PHONY: help
help:
	@echo "Commandes Make disponibles:"
	@echo "  Docker:" 
	@echo "    make docker-up           # Lancer en premier-plan"
	@echo "    make docker-up-build     # Build + run en premier-plan"
	@echo "    make docker-up-d         # Lancer en arrière-plan (detached)"
	@echo "    make docker-down         # Arrêter et nettoyer les conteneurs"
	@echo "    make docker-restart      # Redémarrer le service web"
	@echo "    make docker-logs         # Afficher les logs du service web"
	@echo "    make docker-migrate      # Exécuter les migrations"
	@echo "    make docker-superuser    # Créer un superutilisateur"
	@echo "    make docker-shell        # Ouvrir un shell Django dans le conteneur"
	@echo "  Local (sans Docker):"
	@echo "    make venv                # Créer un environnement virtuel (.venv)"
	@echo "    make install             # Installer les dépendances dans .venv"
	@echo "    make migrate             # Appliquer les migrations"
	@echo "    make makemigrations      # Créer de nouvelles migrations"
	@echo "    make superuser           # Créer un superutilisateur"
	@echo "    make shell               # Ouvrir un shell Django"
	@echo "    make run                 # Lancer le serveur de développement (0.0.0.0:8000)"

# ------------- Cibles Docker -------------
.PHONY: docker-up docker-up-build docker-up-d docker-down docker-restart docker-logs docker-migrate docker-superuser docker-shell

docker-up:
	sudo docker-compose up

docker-up-build:
	sudo docker-compose up --build

docker-up-d:
	sudo docker-compose up -d

docker-down:
	sudo docker-compose down

docker-restart:
	sudo docker-compose restart web

docker-logs:
	sudo docker-compose logs -f web

docker-migrate:
	sudo docker-compose exec web $(PY) manage.py migrate

docker-superuser:
	sudo docker-compose exec web $(PY) manage.py createsuperuser

docker-shell:
	sudo docker-compose exec web $(PY) manage.py shell

# ------------- Cibles Locales -------------
.PHONY: venv install migrate makemigrations superuser shell run

$(VENV):
	python3.11 -m venv $(VENV)

venv: $(VENV)
	@echo "Environnement virtuel prêt dans $(VENV)"

install: venv
	. $(VENV)/bin/activate; $(PIP) install -r requirements.txt

migrate: venv
	. $(VENV)/bin/activate; cd $(APP_DIR) && $(PY) manage.py migrate

makemigrations: venv
	. $(VENV)/bin/activate; cd $(APP_DIR) && $(PY) manage.py makemigrations

superuser: venv
	. $(VENV)/bin/activate; cd $(APP_DIR) && $(PY) manage.py createsuperuser

shell: venv
	. $(VENV)/bin/activate; cd $(APP_DIR) && $(PY) manage.py shell

run: venv
	. $(VENV)/bin/activate; cd $(APP_DIR) && $(PY) manage.py runserver 0.0.0.0:8000
