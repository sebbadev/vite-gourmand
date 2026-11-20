# 🛠️ Mémo Développeur — Vite & Gourmand (Git, Bash, psql, FastAPI)


--------------------------------------------------------------------------------

## 1. Terminal Git Bash & Navigation
## 2. Git & Bonnes Pratiques de Commits
## 3. PostgreSQL & Ligne de commande `psql`
## 4. Python & API FastAPI
## 5. Dépannage rapide (Problèmes Fréquents)

-----------------------------------------------------------------------------------------------
## 1. Terminal Git Bash & Navigation

### Déplacement & Fichiers

* `pwd` : Afficher le dossier courant.
* `ls -la` : Lister tous les fichiers et dossiers (y compris masqués comme `.git`).
* `cd /c/chemin/vers/dossier` : Se déplacer sous Windows avec la syntaxe Git Bash.
* `cd ..` : Remonter d'un dossier parent.
* `mkdir -p dossier1/dossier2` : Créer des dossiers imbriqués sans erreur.
* `touch nom_fichier.md` : Créer un fichier vide.
* `clear` (ou `Ctrl + L`) : Nettoyer l'affichage de la console.
* ctrl+C : annuler la saisie
* ctrl+U : effacer tout ce qui se trouve à gauche du curseur sur la ligne courante
* ctrl+A (ou home) : aller au début de la ligne
* ctrl+E (ou fin)  : aller au bout de la ligne
* alt+f ou ctrl+right-arrow : mot par mot à droite
* alt+b ou ctrl+left-arrow : mot par mot à gauche

### Exécution de scripts `.sh`

* `chmod +x admin/scripts/mon_script.sh` : Rendre un script exécutable (1 fois par script).
* `./admin/scripts/mon_script.sh` : Exécuter un script local.
* `bash admin/scripts/mon_script.sh` : Exécuter directement sans modifier les droits.

### Manipulation de fichiers sans éditeur

### Créer et écraser (`>`) ou ajouter à la fin (`>>`)
- `touch mon_fichier.txt` : Créer un fichier vide ou rafraîchir son horodatage.
- `echo "texte" > mon_fichier.txt` : Créer le fichier ou **écraser tout le contenu existant**.
- `echo "nouvelle ligne" >> mon_fichier.txt` : **Ajouter à la fin** du fichier sans rien effacer.
- `cat mon_fichier.txt` : Afficher l'intégralité du contenu dans la console.

### Bloc multi-lignes propre (`cat << 'EOF'`)
Permet d'écrire du texte sur plusieurs lignes exactement tel quel :

	`cat << 'EOF' > mon_script.sh
	#!/bin/bash
	echo "Initialisation..."
	date
	EOF`


-----------------------------------------------------------------------------------------------
## 2. Git & Bonnes Pratiques de Commits

### Démarrage & Diagnostic

* `git init` : Initialiser le dépôt local (ne crée rien dans l'historique tant qu'on ne commit pas).
* `git status` : État des fichiers (modifiés, non suivis, staged).
* `git log --oneline --graph --all` : Historique condensé et visuel des commits.

### Branches

* `git branch` : Lister les branches locales.
* `git checkout -b dev` : Créer la branche `dev` et basculer dessus.
* `git checkout -b feat/nom-fonction dev` : Créer une branche de feature à partir de `dev`.
* `git switch dev` : Revenir sur la branche `dev`.
* `git merge feat/nom-fonction` : Fusionner la feature dans la branche courante.

### Enregistrement & Traçabilité (Conventions du projet)

* `git add nom_fichier` : Préparer un fichier pour le commit.
* `git add .` : Préparer tous les fichiers modifiés (sauf ceux exclus par `.gitignore`).
* `git commit -m "type(scope): #tag message explicite"` : Enregistrer le commit.
* **Exemples :**
* `git commit -m "feat(db): #feat creation table commandes et enums"`
* `git commit -m "fix(auth): #fix correction import Utilisateur dans auth.py"`
* `git commit -m "chore(docs): #chore ajout du cheatsheet developpeur"`

* `git gui` : Ouvrir l'interface graphique native de Git Bash si tu préfères cocher/stager à la souris.


-----------------------------------------------------------------------------------------------
## 3. PostgreSQL & Ligne de commande `psql`

### Connexion & Déconnexion

* `psql -U postgres` : Se connecter avec l'utilisateur `postgres`.
* `psql -U postgres -d vite_gourmand` : Se connecter directement à la base du projet.
* `\q` : Quitter `psql` et revenir au prompt Git Bash.

### Navigation interne psql

* `\l` : Lister toutes les bases de données du serveur.
* `\c vite_gourmand` : Basculer sur la base `vite_gourmand`.
* `\dt` : Lister toutes les tables de la base active.
* `\d nom_table` : Afficher les colonnes, types, clés et index d'une table.
* `\dT+` : Lister tous les types énumérés (`ENUM`) personnalisés.
* `\dn` : Lister les schémas existants (souvent `public`).

### Exécution de scripts SQL & Requêtes utiles

* `\i docs/sql/create_db.sql` : Exécuter un fichier `.sql` directement depuis `psql`.
* `SELECT COUNT(*) FROM utilisateurs;` : Compter les lignes d'une table.
* `SELECT * FROM menus LIMIT 5;` : Afficher un extrait de données.
* `\x` : Basculer en mode affichage étendu (très lisible pour les tables avec beaucoup de colonnes).

### Sauvegarde & Export portable (Jury)

Depuis le terminal Bash (pas dans `psql`) :

```bash
# Exporter la structure pure sans dépendance db_admin
pg_dump -U postgres -d vite_gourmand --schema-only --no-owner --no-privileges -f docs/sql/create_db.sql

# Exporter uniquement les données (fixtures)
pg_dump -U postgres -d vite_gourmand --data-only --inserts -f docs/sql/fixtures.sql

```


-----------------------------------------------------------------------------------------------
## 4. Python & API FastAPI

### Environnement Virtuel (`venv`)

* `cd backend` : Se placer dans le dossier backend.
* `python -m venv venv` : Créer l'environnement virtuel.
* `source venv/Scripts/activate` : Activer le venv sous Git Bash Windows (le prompt affiche `(venv)`).
* `deactivate` : Désactiver l'environnement virtuel.

### Dépendances

* `pip install -r requirements.txt` : Installer toutes les dépendances du projet.
* `pip freeze > requirements.txt` : Enregistrer les nouvelles dépendances installées.

### Lancement du Serveur de Développement

* `uvicorn app.main:app --reload` : Lancer l'API FastAPI avec rechargement automatique à chaque sauvegarde de fichier.
* Adresse de base : `[http://127.0.0.1:8000](http://127.0.0.1:8000)`
* Swagger / Doc interactive OpenAPI : `[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)`
* Documentation Redoc : `[http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)`





-----------------------------------------------------------------------------------------------
## 5. Dépannage rapide (Problèmes Fréquents)

* **`bash: psql: command not found`** :
Lancer `export PATH=$PATH:"/c/Program Files/PostgreSQL/16/bin"` dans Git Bash.
* **Port 8000 déjà utilisé (FastAPI bloqué)** :
Lancer `uvicorn app.main:app --reload --port 8001` pour basculer sur un port libre.
* **Erreur d'import Python `ModuleNotFoundError: No module named 'app'**` :
Vérifier que tu lances `uvicorn` depuis la racine du dossier `backend/` et non depuis `backend/app/`.
---


-----------------------------------------------------------------------------------------------