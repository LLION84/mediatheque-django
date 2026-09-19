# Rapport de projet — Logiciel de gestion de médiathèque

**Médiathèque « Notre livre, notre média »** — Python / Django
Dépôt GitHub : https://github.com/LLION84/mediatheque-django

---

## 1. Étude et correctifs du code fourni

Le code de départ était une ébauche en mode console, avec des classes `livre`, `dvd`,
`cd`, `jeuDePlateau` et `Emprunteur`.

### Les problèmes que j'ai identifiés

**Les attributs étaient déclarés dans la classe, sans `__init__`.** Ils appartenaient
donc à la classe et non à chaque objet : tous les livres auraient partagé les mêmes
valeurs. C'est le défaut le plus grave.

**Rien n'était enregistré.** Toutes les données disparaissaient à la fermeture du
programme, ce qui est impossible pour un logiciel de gestion.

**Le code était dupliqué.** `livre`, `dvd` et `cd` répétaient chacun `name`,
`dateEmprunt`, `disponible` et `emprunteur`. Le même champ écrit trois fois.

**Les normes Python n'étaient pas respectées.** Les classes doivent s'écrire en
PascalCase (`Livre` et non `livre`) et les attributs en snake_case (`date_emprunt` et
non `dateEmprunt`).

**Les types étaient incohérents.** `disponible = ""` et `bloque = ""` sont des chaînes
de caractères alors que ce sont des oui/non.

**Aucune règle métier.** Rien n'empêchait un membre d'avoir 50 emprunts, rien ne
calculait de date de retour.

### Ce que j'ai gardé

L'idée de départ est bonne : distinguer les livres, DVD, CD, jeux de plateau et
emprunteurs. J'ai gardé ce découpage et les attributs propres à chaque type (`auteur`,
`realisateur`, `artiste`, `createur`). J'ai aussi gardé la séparation du jeu de plateau,
qui n'avait ni date d'emprunt ni emprunteur — ce qui correspond à la règle « les jeux de
plateau ne sont pas concernés par les emprunts ».

### Ce que j'ai refait

| Avant | Après |
|---|---|
| Attributs de classe | Champs de modèle Django, propres à chaque objet |
| Aucune sauvegarde | Base de données MySQL |
| Code répété 3 fois | Classe mère `Media` dont héritent `Livre`, `Dvd`, `Cd` |
| `livre`, `dateEmprunt` | `Livre`, `date_emprunt` (normes PEP 8) |
| `disponible = ""` | `BooleanField(default=True)` |
| `emprunteur` dans chaque média | Modèle `Emprunt` dédié |
| `bloque = ""` | Méthode calculée `peut_emprunter()` |
| Application console | Deux applications web Django |

---

## 2. La mise en place des fonctionnalités

### L'organisation du projet

J'ai créé deux applications, comme demandé :

- **`gestion`** — réservée aux bibliothécaires ;
- **`consultation`** — pour les membres, en lecture seule.

Chaque application contient ses propres `models.py`, `views.py`, `urls.py` et `tests.py`.

### Les modèles et l'héritage

```python
class Media(models.Model):
    titre = models.CharField(max_length=200)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return self.titre


class Livre(Media):
    auteur = models.CharField(max_length=200)


class Dvd(Media):
    realisateur = models.CharField(max_length=200)


class Cd(Media):
    artiste = models.CharField(max_length=200)
```

`titre` et `disponible` ne sont écrits qu'une seule fois, dans la classe mère. Les trois
classes filles en héritent et n'ajoutent que ce qui leur est propre.

`JeuDePlateau` n'hérite **pas** de `Media`, volontairement : comme il ne s'emprunte
jamais, il n'a pas besoin du champ `disponible` et ne doit pas pouvoir apparaître dans
un emprunt. La règle métier est donc respectée par la structure même des données, sans
avoir à écrire de contrôle.

À cela s'ajoutent `Membre` et `Emprunt`. J'ai choisi de faire de l'emprunt un modèle à
part entière (plutôt qu'un champ `emprunteur` sur le média) pour garder l'historique :
un emprunt rendu n'est pas effacé, il reçoit une date de retour.

### Les règles métier

Je les ai écrites comme des méthodes, dans la classe concernée :

```python
# Dans Emprunt
def date_limite(self):
    return self.date_emprunt + timedelta(days=self.DUREE_EMPRUNT_JOURS)

def est_en_retard(self):
    if self.date_retour is not None:
        return False
    return date.today() > self.date_limite()


# Dans Membre
def peut_emprunter(self):
    if self.a_du_retard():
        return False
    return self.emprunts_en_cours().count() < self.NB_EMPRUNTS_MAX
```

| Règle de l'énoncé | Où elle est appliquée |
|---|---|
| 3 emprunts maximum | `Membre.peut_emprunter()` |
| Retour sous 1 semaine | `Emprunt.date_limite()` |
| Retard ⇒ plus d'emprunt | `Membre.a_du_retard()` |
| Jeux de plateau non empruntables | Structure des modèles |

Deux choix que je tiens à expliquer :

- Les valeurs `DUREE_EMPRUNT_JOURS = 7` et `NB_EMPRUNTS_MAX = 3` sont des constantes
  nommées, pas des chiffres écrits en dur. Si la médiathèque change de règle, une seule
  ligne est à modifier.
- Le blocage d'un membre est **calculé**, pas stocké. Le code fourni prévoyait un champ
  `bloque` : ce genre de champ finit toujours par se désynchroniser parce qu'on oublie
  de le mettre à jour. `peut_emprunter()` recalcule la réponse à partir des emprunts
  réels, elle ne peut donc jamais être fausse.

### Les pages réalisées

**Application bibliothécaire**

| Fonctionnalité | Adresse |
|---|---|
| Créer un membre | `/gestion/membres/nouveau/` |
| Afficher la liste des membres | `/gestion/membres/` |
| Mettre à jour un membre | `/gestion/membres/<id>/modifier/` |
| Supprimer un membre | `/gestion/membres/<id>/supprimer/` |
| Afficher la liste des médias | `/gestion/medias/` |
| Ajouter un média | `/gestion/medias/ajouter/<type>/` |
| Créer un emprunt | `/gestion/emprunts/nouveau/` |
| Rentrer un emprunt | `/gestion/emprunts/<id>/rentrer/` |

**Application membre**

| Fonctionnalité | Adresse |
|---|---|
| Consulter la liste des médias | `/` |

Quand un emprunt est créé, le média passe automatiquement en « non disponible ». Quand
il est rendu, la date du jour est enregistrée et le média redevient disponible.

### Le style défensif

Je ne fais jamais confiance à ce qui vient du navigateur. Les formulaires sont des
`ModelForm` : Django vérifie tout seul les champs obligatoires, les longueurs et le
format des adresses e-mail, côté serveur.

Pour les emprunts, j'ai mis **deux niveaux** de protection :

```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields["media"].queryset = Media.objects.filter(disponible=True)

def clean(self):
    donnees = super().clean()
    membre = donnees.get("membre")
    if membre and not membre.peut_emprunter():
        raise forms.ValidationError(
            "Ce membre ne peut pas emprunter : il a déjà 3 emprunts en cours, "
            "ou il a un retard."
        )
    return donnees
```

Le premier ne propose que les médias disponibles — c'est pour le confort. Le second
revérifie tout avant d'enregistrer — c'est pour la sécurité : quelqu'un qui modifierait
le formulaire dans son navigateur passerait le premier filtre, jamais le second.

J'utilise aussi `get_object_or_404()` (une fiche inexistante affiche une page 404 propre
au lieu de planter) et `{% csrf_token %}` sur tous les formulaires.

### Les logs

J'ai configuré un journal dans `settings.py` qui écrit dans un fichier
`mediatheque.log`. Les créations de membres, les emprunts et les retours y sont tracés :

```
2026-09-12 15:47:59,318 [INFO] Nouveau membre créé : Paul Martin
```

Cela permet de retrouver ce qui s'est passé en cas de litige ou de bug.

---

## 3. La base de données et les données de test

### Le choix de MySQL

J'ai commencé avec SQLite, puis je suis passé à **MySQL** (via WAMP), parce que SQLite
est un simple fichier sans mot de passe, ce qui ne répond pas au critère de connexion
sécurisée.

### La sécurisation

L'application ne se connecte pas avec `root`. J'ai créé un utilisateur dédié, limité à
la seule base du projet :

```sql
CREATE USER 'mediatheque_user'@'localhost' IDENTIFIED BY '<mot de passe>';
GRANT ALL PRIVILEGES ON mediatheque.* TO 'mediatheque_user'@'localhost';
```

`@'localhost'` veut dire qu'il ne peut se connecter que depuis cette machine, et
`ON mediatheque.*` qu'il n'a aucun droit sur les autres bases du serveur.

Le mot de passe n'est **pas** dans le code. `settings.py` le lit dans un fichier `.env`,
exclu du dépôt par le `.gitignore` :

```python
"PASSWORD": os.environ.get("DB_PASSWORD"),
```

Le dépôt contient un fichier `.env.example` qui montre quelles variables créer, sans
donner leur valeur.

J'ai aussi activé le mode strict de MySQL : sans lui, une donnée trop longue est coupée
silencieusement au lieu d'être refusée.

### Les données de test

Je les ai saisies via l'interface d'administration de Django (`/admin`) :

| Type | Entrées |
|---|---|
| Livres | Germinal (Zola), Dune (Herbert), 1984 (Orwell), L'Étranger (Camus) |
| DVD | Inception (Nolan), Le Parrain (Coppola) |
| CD | Discovery (Daft Punk), Thriller (Michael Jackson) |
| Jeux de plateau | Catan (Klaus Teuber), Dixit (Jean-Louis Roubira) |
| Membres | Marie Dupont, Zinou Blaise, Paul Martin |

Ce jeu de données permet de tester tous les cas : des médias empruntables et d'autres
qui ne le sont pas, et un membre qui peut atteindre la limite de 3 emprunts.

---

## 4. Stratégie de tests

J'ai écrit **15 tests**, organisés en trois niveaux. Django crée une base temporaire
avant de les lancer et la supprime après : mes vraies données ne sont jamais touchées.

**Niveau 1 — les modèles (3 tests)**
Vérifier que l'héritage fonctionne (un `Livre` possède bien `titre` et `disponible`
hérités de `Media`) et que les objets s'affichent correctement.

**Niveau 2 — les règles métier (3 tests)**
Un test par règle de l'énoncé : la date limite tombe bien 7 jours plus tard, un membre
avec 3 emprunts ne peut plus emprunter, un membre en retard est bloqué.

**Niveau 3 — les fonctionnalités (9 tests)**
Un test par fonctionnalité demandée. J'utilise le client de test de Django, qui se
comporte comme un navigateur : il visite les pages et soumet les formulaires.

| Test | Fonctionnalité |
|---|---|
| `test_afficher_liste_membres` | Afficher la liste des membres |
| `test_creer_membre` | Créer un membre |
| `test_modifier_membre` | Mettre à jour un membre |
| `test_supprimer_membre` | Supprimer un membre |
| `test_afficher_liste_medias` | Afficher la liste des médias |
| `test_ajouter_media` | Ajouter un média |
| `test_creer_emprunt` | Créer un emprunt |
| `test_rentrer_emprunt` | Rentrer un emprunt |
| `test_catalogue_public` | Consultation de la liste des médias |

**Exécution**

```
python manage.py test gestion
```

```
Found 15 test(s).
Ran 15 tests in 0.814s

OK
```

Les 15 tests passent sans erreur.

Une difficulté sur le test du retard : `date_emprunt` est rempli automatiquement avec la
date du jour et ne peut pas être modifié normalement. Pour simuler un emprunt vieux de
dix jours, j'écris directement en base avec `.update()`, puis je recharge l'objet avec
`refresh_from_db()`.

---

## 5. Instructions d'exécution

La procédure complète est dans le fichier **README.md** du dépôt. En résumé :

1. installer Python 3 et un serveur MySQL (WAMP) ;
2. cloner le dépôt ;
3. créer un environnement virtuel, puis `pip install -r requirements.txt` ;
4. créer la base `mediatheque` et l'utilisateur dédié (les commandes SQL sont dans le
   README) ;
5. copier `.env.example` en `.env` et y mettre le mot de passe choisi ;
6. `python manage.py migrate` puis `python manage.py createsuperuser` ;
7. `python manage.py runserver`.

---

## 6. Bilan

Toutes les fonctionnalités demandées sont en place et testées. Les quatre règles métier
de l'énoncé sont respectées : trois par du code testé, la quatrième par la conception
même des modèles. Les données sont enregistrées dans une base MySQL dont le mot de passe
ne figure nulle part dans le dépôt.

L'interface reste volontairement minimale, la mise en forme CSS étant confiée à un
designer d'après l'énoncé.

Ce que j'améliorerais avec plus de temps : protéger l'application bibliothécaire par une
authentification (`@login_required`), et appeler une API externe comme Open Library pour
pré-remplir le titre et l'auteur d'un livre à partir de son ISBN.
