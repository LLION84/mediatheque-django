# Médiathèque « Notre livre, notre média »

Logiciel de gestion de médiathèque développé avec **Django 6.1** et **MySQL**.

Le projet comporte deux applications :

- **`gestion`** — application bibliothécaire : membres, médias et emprunts ;
- **`consultation`** — application membre : consultation du catalogue en lecture seule.

Le rapport complet du projet se trouve dans le fichier [RAPPORT.md](RAPPORT.md).

---

## Prérequis

| Logiciel | Version | Remarque |
|---|---|---|
| Python | 3.10 ou supérieur | https://www.python.org/downloads/ — cocher **« Add python.exe to PATH »** à l'installation |
| Serveur MySQL | 5.7 ou supérieur | WAMP, XAMPP, MAMP ou MySQL seul |
| Git | — | uniquement pour cloner le dépôt |

---

## Installation

### 1. Récupérer le projet

```bash
git clone https://github.com/LLION84/mediatheque-django.git
cd mediatheque-django
```

### 2. Créer l'environnement virtuel

**Windows (PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> Si PowerShell refuse d'exécuter le script d'activation :
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, puis relancer la commande.

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Créer la base de données et son utilisateur

Démarrer le serveur MySQL (icône WAMP verte), ouvrir **phpMyAdmin**
(`http://localhost/phpmyadmin`, utilisateur `root`, mot de passe vide par défaut),
puis exécuter dans l'onglet **SQL** :

```sql
CREATE DATABASE mediatheque CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

CREATE USER 'mediatheque_user'@'localhost' IDENTIFIED BY 'VotreMotDePasse';
GRANT ALL PRIVILEGES ON mediatheque.* TO 'mediatheque_user'@'localhost';
GRANT ALL PRIVILEGES ON `test_mediatheque`.* TO 'mediatheque_user'@'localhost';
FLUSH PRIVILEGES;
```

> La deuxième ligne `GRANT` autorise la base temporaire que Django crée pour exécuter
> les tests. Sans elle, `manage.py test` échoue avec une erreur d'accès refusé.

### 5. Configurer les identifiants

Copier le fichier d'exemple et y renseigner le mot de passe choisi à l'étape 4 :

**Windows**

```powershell
copy .env.example .env
```

**macOS / Linux**

```bash
cp .env.example .env
```

Puis éditer `.env` :

```
DB_NAME=mediatheque
DB_USER=mediatheque_user
DB_PASSWORD=VotreMotDePasse
DB_HOST=127.0.0.1
DB_PORT=3306
```

> Le fichier `.env` n'est jamais versionné : il est exclu par le `.gitignore`. C'est lui
> qui garde le mot de passe hors du code source.

### 6. Créer les tables

```bash
python manage.py migrate
```

### 7. Créer un compte administrateur

```bash
python manage.py createsuperuser
```

Le mot de passe ne s'affiche pas pendant la saisie, c'est normal.

---

## Lancer l'application

```bash
python manage.py runserver
```

| Adresse | Application |
|---|---|
| http://127.0.0.1:8000/ | Catalogue public (membres) |
| http://127.0.0.1:8000/gestion/membres/ | Gestion des membres |
| http://127.0.0.1:8000/gestion/medias/ | Gestion des médias |
| http://127.0.0.1:8000/gestion/emprunts/ | Emprunts et retours |
| http://127.0.0.1:8000/admin | Administration Django |

---

## Ajouter des données de test

Se connecter à `http://127.0.0.1:8000/admin` avec le compte créé à l'étape 7. Tous les
modèles y sont disponibles : Livres, Dvds, Cds, Jeu de plateaus, Membres, Emprunts.

Jeu de données utilisé pour les démonstrations :

| Type | Entrées |
|---|---|
| Livres | Germinal (Zola), Dune (Herbert), 1984 (Orwell), L'Étranger (Camus) |
| DVD | Inception (Nolan), Le Parrain (Coppola) |
| CD | Discovery (Daft Punk), Thriller (Michael Jackson) |
| Jeux de plateau | Catan (Klaus Teuber), Dixit (Jean-Louis Roubira) |
| Membres | Marie Dupont, Zinou Blaise, Paul Martin |

---

## Exécuter les tests

```bash
python manage.py test gestion
```

Résultat attendu :

```
Found 15 test(s).
Ran 15 tests in 0.814s

OK
```

---

## Règles métier appliquées

- Un membre ne peut pas avoir plus de **3 emprunts** simultanés.
- Un emprunt doit être rendu sous **7 jours**.
- Un membre ayant un emprunt **en retard** ne peut plus emprunter.
- Les **jeux de plateau** sont en consultation sur place et ne peuvent pas être
  empruntés.

---

## Journalisation

Les créations de membres, les emprunts et les retours sont enregistrés dans le fichier
`mediatheque.log`, créé automatiquement à la racine du projet au premier événement.

---

## En cas de problème

| Message | Cause et solution |
|---|---|
| `Can't connect to MySQL server` / `WinError 10061` | Le serveur MySQL n'est pas démarré : lancer WAMP et attendre l'icône verte |
| `'NoneType' object has no attribute 'startswith'` | Le fichier `.env` est absent ou mal placé : il doit être à la racine, à côté de `manage.py` |
| `Access denied for user ... 'test_mediatheque'` | Le `GRANT` sur la base de test n'a pas été exécuté (étape 4) |
| `django-admin n'est pas reconnu` | L'environnement virtuel n'est pas activé (étape 2) |
