# Prompt d'installation — à coller chez ton agent

> **Prérequis** : l'agent doit avoir le **MCP Webflow connecté et autorisé** sur le bon workspace
> (`https://mcp.webflow.com/mcp`).
>
> Le contenu des instructions vit dans un dépôt public — **rien à copier dans ton projet**.
> Le prompt ci-dessous donne l'URL à l'agent. Si ton agent ne sait pas récupérer d'URL,
> ouvre `BUNDLE.md` et colle son contenu à la suite du prompt.

---

Le contenu des instructions à installer se trouve ici, en accès public :

```
https://raw.githubusercontent.com/growthval/perplexity_integration/claude/busy-franklin-i7zvly/docs/webflow-agent-instructions/BUNDLE.md
```

Récupère ce fichier (fetch HTTP, ou `curl -s <url>`) et garde-le sous la main : il contient les
5 instructions à créer, chacune avec son `kind` et son `path`. Si la récupération échoue, dis-le
et arrête-toi — ne reconstitue pas le contenu de mémoire.
> ⚠️ `raw.githubusercontent.com` met les URLs de **branche** en cache environ 5 minutes. Si le kit
> vient d'être modifié, remplace le nom de branche par un **SHA de commit** dans l'URL : cette
> forme-là est immuable et servie immédiatement.

---

Tu vas installer et mettre à jour la configuration « agent » de mon site Webflow. Travaille dans
l'ordre ci-dessous et **ne saute aucune phase**. Tu as le MCP Webflow connecté.

## Contexte du site — à respecter tout du long

- **Plan du site : CMS.** (C'est le plan *site*, pas le plan *workspace*.)
- **Le branching n'est donc pas disponible** : il gate sur un workspace Enterprise. Ne propose
  aucun workflow en branche. Pour itérer sans risque : dupliquer la page
  (`create_page` avec `duplicateOf` et `draft: true`), travailler sur la copie, publier
  **uniquement sur le domaine de staging `*.webflow.io`**, basculer après validation.
- Ce que le plan CMS permet et qui est utile ici : le CMS et ses collections, le custom code de
  site et de page, et la **publication de code components** (elle exige un plan site CMS ou
  supérieur, ou un workspace payant — le plan CMS suffit).
- **Add-ons : seul Localize est actif.** Analyze et Optimize ne le sont **pas** — ne propose
  aucun workflow qui en dépende (`data_analyze_tool` échouera, c'est normal).
- **Le site est bilingue** via Localize : locale primaire **français** (`FR-FR` dans le Designer),
  locale secondaire **anglais**. Une locale secondaire est une **surcouche de traduction** sur la
  même structure, pas une copie : ne duplique jamais une page, un composant ou une collection pour
  l'anglais. Ne devine aucun identifiant de locale — lis-les dans `get_site`.
  Les contrôles de ton/formalité de la traduction IA relèvent de l'offre Localize avancée :
  teste avant d'en dépendre et dis-moi ce que tu obtiens.
- **Le site** : « Service Limo Car » — chauffeur privé haut de gamme, mise à disposition longue
  durée, événementiel et services VIP, Paris / France / international. Registre premium et sobre.
- **Système de design : Client-First (Finsweet)**, avec des sections de la bibliothèque **Relume**.
  Deux familles de classes coexistent et ne se traitent pas pareil : les **utilitaires**
  Client-First en tirets (`padding-global`, `container-large`, `padding-section-large`,
  `max-width-xlarge`, `text-align-center`, `margin-bottom`, `text-size-medium`,
  `heading-style-h2`), partagés par tout le site et **à ne jamais modifier** pour un besoin
  ponctuel ; et les **classes de composant** Relume en underscore (`section_header30`,
  `header30_content`, `layout34_component`, `slider6_component`, `layout370_card-small`), propres
  à leur bloc. Wrappers globaux : `page-wrapper` puis `main-wrapper`.
  Détail complet dans `rules/design-system.md` du bundle.

## Phase 0 — Vérifier l'état réel, ne rien supposer

1. Appelle `webflow_guide_tool` et **note la version du serveur MCP** annoncée. Tout ce qui suit
   doit être vérifié contre cette version, pas contre ta mémoire ni contre des articles de blog.
2. Liste mes sites (`data_sites_tool`) et demande-moi lequel traiter si le choix est ambigu.
   Ne devine jamais un `site_id`. Relève au passage le champ `locales` du site et **note les deux
   identifiants distincts** qu'il contient : l'`id` de locale (pour `data_localization_tool`) et le
   `cmsLocaleId` (pour `data_cms_tool`). Les confondre écrit dans la mauvaise locale.
3. Va lire la page <https://developers.webflow.com/home/changelog> et repère **toute entrée
   postérieure au 20 septembre 2026**. Si quelque chose contredit les instructions ci-dessous,
   **signale-le-moi avant d'agir** — c'est la source à jour qui gagne.
4. Si un outil te manque pour une étape, appelle `get_more_tools` plutôt que de te rabattre sur
   un contournement.

## Phase 1 — Inventorier le site

Avant toute écriture, construis une image réelle du site :

- `data_agent_instructions_tool > search_instructions` — les instructions **déjà présentes**.
- `data_style_tool > get_styles` — les classes existantes.
- `data_variable_tool > get_variable_collections` puis `get_variables` — les tokens.
- `data_component_tool > get_all_components` — les composants réutilisables.
- `data_element_tool > get_all_elements` (depth 4-5) sur la page **Accueil**, puis sur deux autres
  pages — la structure maison. Confirme que Client-First + Relume y est appliqué de façon
  cohérente, et **signale tout écart** au lieu de généraliser ce que tu vois sur une seule page.
- `data_localization_tool > list_components` — les composants localisables, et l'état actuel de la
  locale EN sur une page représentative (`get_page_content` avec le `localeId` secondaire) :
  qu'est-ce qui est déjà traduit, qu'est-ce qui ne l'est pas ?

Déduis-en : quel système de nommage est utilisé (Client-First, Lumos, maison…), quelle est la
structure de section type, et quelles sont les 5 à 10 classes les plus réutilisées.

## Phase 2 — Audit de conflits (obligatoire, avant toute écriture)

Cherche les règles périmées, **à deux endroits** :

**A. Sur le site** — les instructions renvoyées par `search_instructions`.

**B. Dans mon projet local** — lis, s'ils existent :
`CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.cursor/rules/*`, `.windsurfrules`,
`.github/copilot-instructions.md`, `README.md`, et tout fichier de `docs/` ou `.claude/`
qui parle de Webflow.

Pour chaque source, traque ces affirmations — **toutes étaient vraies en MCP 1.x et sont fausses
aujourd'hui** :

| Affirmation périmée à chercher | Réalité actuelle |
|---|---|
| « le Designer doit être ouvert pour créer des éléments » | Faux depuis MCP 2.0 : la création est headless |
| « la Bridge App est requise » (en général) | Requise seulement pour les captures visuelles et la sélection/navigation en direct |
| « le MCP ne peut pas créer d'interactions IX3 » | Faux : `data_interactions_tool` existe |
| « utiliser un HTML embed pour construire une section » | Obsolète : `data_whtml_builder` produit des éléments natifs |
| `element_tool > add_or_update_attribute` | Remplacé par `data_element_tool > set_attributes` |
| `set_id` / `update_id_attribute` | Remplacés par `data_element_settings_tool > set_dom_id` |
| `get_variants` | N'existe pas : `data_component_tool > get_component` avec `options.includeVariants` |
| « 46+ data tools » / anciennes listes d'outils | Jeu d'outils consolidé ; se fier à la découverte MCP |
| commande CLI `webflow library` | Renommée `webflow devlink` (CLI 2.0, mai 2026) |
| commande CLI `webflow cloud create` | Renommée `webflow cloud init` |
| Node.js < 22.13 | Minimum 22.13.0 depuis la CLI 2.0 |
| « le champ `canBranch` indique si le branching est disponible » | Faux : seul `list_branches` fait foi (403 `not_enterprise_plan_site` = indisponible) |
| toute règle qui suppose un workflow en branche | Indisponible sur ce site (plan CMS) : remplacer par page dupliquée en `draft` + publication staging |
| « on ne peut pas créer d'items CMS localisés » | **Faux aujourd'hui** : `create_collection_items` accepte `cmsLocaleIds` et `allCmsLocales: true` |
| toute règle qui crée une page, un composant ou une collection **dupliqués** pour l'anglais | Mauvais modèle : Localize est une surcouche sur la même structure |
| toute règle qui suppose Analyze ou Optimize | Ces add-ons ne sont pas actifs sur ce site |
| toute règle qui impose un autre système de classes (Lumos, BEM, Tailwind, noms libres) | Ce site est en **Client-First** : conflit direct, à corriger |
| toute règle qui pousse à fusionner les utilitaires empilés en une classe custom | Contraire à Client-First : l'empilement est voulu |
| « on peut créer des items CMS localisés » | Faux : on peut seulement mettre à jour des items localisés existants |

Cherche aussi les **contradictions entre mes propres fichiers** (deux systèmes de nommage de
classes qui coexistent, deux conventions de structure, une règle locale qui interdit ce qu'une
instruction du site impose).

**Livrable de cette phase — avant toute écriture :** un tableau avec, pour chaque problème,
`fichier ou instruction` / `ligne ou extrait` / `pourquoi c'est périmé` / `correction proposée`.
Puis **attends mon feu vert**.

## Phase 3 — Générer les instructions depuis mon site

Lance `data_agent_instructions_tool > generate_instruction` pour, dans cet ordre :

1. `design-system`
2. `brand-guidelines`
3. `asset-guidelines`
4. `cms-guidelines` — celui-ci exige une collection CMS en source primaire : demande-moi laquelle,
   ou propose la plus structurante après avoir listé les collections.

C'est **asynchrone** : premier appel → `taskId`, puis rappels avec `task_id` jusqu'à `finished`
ou `failed`, puis lecture du `resourceUri`. Les résultats sont des **brouillons** :
lis-les, résume-moi ce qu'ils contiennent, et signale ce qui est faux ou incomplet.
Ne les passe pas en non-brouillon sans mon accord.

## Phase 4 — Installer les règles et le skill

Depuis le bundle récupéré en tête de prompt, crée les instructions suivantes avec
`data_agent_instructions_tool > create_instruction` :

| `kind` | `path` |
|---|---|
| `rule` | `rules/native-first.md` |
| `rule` | `rules/design-system.md` |
| `rule` | `rules/accessibility-seo.md` |
| `rule` | `rules/localization.md` |
| `rule` | `rules/safety.md` |
| `skill` | `build-native-section/SKILL.md` |

Règles d'écriture :

- **Si un chemin existe déjà : n'écrase rien.** Montre-moi un diff entre l'existant et le nouveau,
  et attends ma décision (garder, fusionner, remplacer).
- **Remplis les emplacements `<…>`** avec ce que tu as découvert en Phase 1 : le vrai système de
  nommage, la vraie structure de section, les vraies classes et variables, une vraie page de
  référence. Une instruction générique ne sert à rien.
- **Référence les ressources réelles** du site (composants, variables, collections) plutôt que de
  les décrire en prose — c'est ce qui empêche un agent de choisir un composant au nom approchant.
- Cohérence avec la Phase 3 : si un brouillon généré contredit une règle du bundle, dis-le-moi
  plutôt que de choisir tout seul.

## Phase 5 — Corriger les fichiers de mon projet

Applique les corrections validées en Phase 2 sur mes fichiers locaux :
supprime ou réécris les règles périmées, résous les contradictions, et ajoute un renvoi vers les
Agent Instructions du site pour ce qui est désormais porté par Webflow plutôt que par le projet.
Ne supprime rien qui ne soit pas dans la liste que j'ai validée.

## Phase 6 — Tester

Vérifie que l'installation fonctionne, sans rien publier :

1. Rappelle `search_instructions` : les 5 instructions doivent être là.
2. Lis-en une avec `read_instruction` et `resolve_references: true` : les références aux ressources
   du site doivent bien être résolues et inlinées.
3. Test à blanc : demande-toi « comment construirais-je une section hero sur ce site ? » et
   montre-moi le plan que produisent les instructions — sans rien créer.
4. Second test à blanc : « comment ajouterais-je la version EN d'une nouvelle section ? »
   Le plan doit passer par `data_localization_tool` sur la locale secondaire, **sans dupliquer
   quoi que ce soit** et avec les bons identifiants de locale. S'il propose une page dupliquée,
   la règle `rules/localization.md` n'a pas été prise en compte — signale-le.

## Contraintes valables sur toute la mission

- **Ne publie rien**, ne supprime rien, ne modifie aucun style global ni composant partagé sans
  mon accord explicite. Si une publication est validée, elle va **d'abord sur `*.webflow.io`**.
- **Aucun workflow en branche** : le plan du site ne le permet pas (voir Contexte du site).
- Annonce ton plan avant chaque phase d'écriture.
- À la fin, liste tout ce qui a été créé ou modifié — sur le site **et** dans le projet.
- Quand tu n'es pas sûr, dis-le au lieu de deviner.
