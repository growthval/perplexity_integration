# Étude de marché — abris, carports et auvents (Corbigny, Nièvre)

## Cadrage

| | |
|---|---|
| **Zone** | Corbigny (58800) + zone de chalandise 45 min : Clamecy, Vézelay, Château-Chinon, Prémery, Lormes, Tannay |
| **Périmètre produit** | Abris de jardin · carports autoportés (bois/alu) · auvents adossés |
| **Hors périmètre** | Carports photovoltaïques · carports renforcés anti-vent (positionnement technique) |
| **Cibles** | Particuliers et professionnels |

Sept chantiers d'analyse : dimensionnement du marché, structure de la demande,
paysage concurrentiel, structure de prix et économie unitaire, cadre
réglementaire, go-to-market, risques et facteurs clés de succès.

La collecte est automatisée par `scripts/etude_marche_carports.py`, qui interroge
l'Agent API (analyse rédigée + citations) et la Search API (sources brutes) et
écrit `etude/dossier-sources.md` et `etude/sources.json`.

```bash
python scripts/etude_marche_carports.py --dry-run   # plan, sans appel API
python scripts/etude_marche_carports.py             # collecte complète
python scripts/etude_marche_carports.py --only prix concurrence
```

Coût d'un passage complet : 7 appels Agent API + 7 appels Search API.

## Prérequis : débloquer Perplexity dans l'environnement cloud

Deux verrous indépendants. **Les deux doivent être levés** — la clé seule ne
suffit pas, le réseau seul non plus.

### 1. Autoriser le domaine `api.perplexity.ai`

Par défaut l'environnement est en niveau **Trusted**, qui n'autorise que les
dépôts de paquets et quelques domaines courants. `api.perplexity.ai` n'en fait
pas partie : le proxy répond `403` au CONNECT.

1. Aller sur [claude.ai/code](https://claude.ai/code)
2. Ouvrir le sélecteur d'environnement (icône nuage), survoler l'environnement
   utilisé et cliquer l'icône de réglages à droite
3. Dans **Network access**, choisir **Custom**
4. Dans **Allowed domains**, ajouter sur une ligne : `api.perplexity.ai`
5. Cocher **Also include default list of common package managers** — sinon PyPI
   devient inaccessible et le SDK `perplexityai` ne s'installe plus

### 2. Fournir la clé API

Deux méthodes, au choix.

**A — Variable d'environnement** (tous les plans, le plus simple)

Dans le champ **Environment variables** du même dialogue, au format `.env` :

```
PERPLEXITY_API_KEY=pplx-...
```

⚠️ La documentation est explicite : *toute personne qui utilise
l'environnement peut lire cette valeur.* À réserver à une clé dédiée,
révocable depuis [console.perplexity.ai](https://console.perplexity.ai).

**B — API credential** (plans Pro et Max uniquement) — **méthode retenue**

Section **Identifiants API** → **Ajouter un identifiant**. La clé est attachée
aux requêtes par le proxy *après* leur sortie de la session : elle n'atteint
jamais Claude, ni les commandes exécutées, ni les variables d'environnement.

| Champ | Valeur |
|---|---|
| Nom | `Perplexity API` |
| Type d'identifiant | `Bearer` |
| **Sites web autorisés** | **`api.perplexity.ai`** |
| En-tête : Nom / Préfixe / Valeur | `Authorization` / `Bearer` / la clé |

Le champ **Sites web autorisés** est celui qu'on oublie : vide, l'identifiant
ne s'applique à aucun host et ne débloque rien.

Avec cette méthode, **Accès réseau** peut rester sur **De confiance** : les
hosts déclarés sur un identifiant API sont joignables même si le niveau
d'accès réseau ne les autoriserait pas. L'étape 1 devient facultative.

#### Variable d'environnement factice obligatoire

Le code refuse de démarrer si `PERPLEXITY_API_KEY` est absente — `_client()`
lève `PerplexityConfigError` **avant** d'émettre la requête, donc avant que le
proxy puisse injecter la clé. Il faut donc quand même renseigner, dans
**Variables d'environnement** :

```
PERPLEXITY_API_KEY=placeholder-la-vraie-cle-est-injectee-par-le-proxy
```

Ce n'est pas un secret : la vraie clé reste dans l'identifiant API.

#### Réserve à vérifier

Le SDK pose son propre en-tête `Authorization: Bearer <placeholder>`. Le proxy
doit le **remplacer**, pas l'ajouter en double — sinon Perplexity renvoie 401.
Le lien **« Voir l'exemple curl résolu »** du dialogue montre la requête
réellement émise : un seul en-tête `Authorization` = configuration correcte.

En cas d'échec, repli sur la méthode A : supprimer l'identifiant, passer
**Accès réseau** en **Custom** avec `api.perplexity.ai`, et mettre la vraie
clé dans `PERPLEXITY_API_KEY`.

### 3. Ouvrir une nouvelle session

> *« Chaque session copie les valeurs de l'environnement une seule fois, au
> démarrage. Les sessions déjà en cours conservent les valeurs avec lesquelles
> elles ont démarré. »*

Une session déjà ouverte ne verra donc **jamais** la nouvelle configuration.
Il faut en démarrer une nouvelle après avoir enregistré.

### 4. Vérifier

```bash
pip install -e .
python scripts/search_smoke_test.py   # attendu : HTTP 200 OK
python scripts/smoke_test.py          # attendu : HTTP 200 OK
```

Si `403` persiste : le domaine n'est pas passé en allowlist.
Si `PERPLEXITY_API_KEY is not set` : la variable n'est pas descendue dans la
session, ou la session date d'avant la modification.

## Points de vigilance sur les données

- **Les fourchettes de prix des agrégateurs de devis ne sont pas des données.**
  Une première recherche donne 6 000–22 000 € matériel + pose en commune rurale
  de la Nièvre : fourchette trop large pour être exploitable, et probablement
  gonflée par des projets photovoltaïques. À recouper avec des catalogues et
  devis réels.
- **Maille géographique.** Peu de statistiques existent à l'échelle de Corbigny.
  Toujours préciser si un chiffre est communal, cantonal, départemental ou
  national, et ne jamais extrapoler silencieusement.
- **Contraintes ABF.** Corbigny et Vézelay sont en périmètre de monument
  historique ; le Parc naturel régional du Morvan ajoute ses propres règles.
  Cela conditionne le délai et le taux de refus des projets.
