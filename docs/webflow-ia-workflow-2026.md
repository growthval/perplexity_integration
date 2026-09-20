# Webflow × IA — état des lieux et workflow de création **native** de pages

_Étude réalisée le 20 septembre 2026. Sources : recherche web via l'API Perplexity (Agent + Search)
et **interrogation directe du serveur MCP Webflow connecté à cette session** (qui s'annonce en
version **2.1.0**) — cette seconde source est de première main et prime sur la documentation
publique quand les deux divergent._

---

## 0. La question centrale, et sa réponse

> « Je veux que mon IA crée des pages **nativement** : de vraies sections Webflow, éditables
> dans le Designer. Pas un bloc HTML embed, pas un script. »

**C'est faisable aujourd'hui, et c'est même le mode de fonctionnement normal du MCP Webflow 2.x.**

Le point qui change tout : depuis **MCP 2.0 (21 juillet 2026)**, la création d'éléments est
**headless**. Le Designer n'a plus besoin d'être ouvert, et l'app « Bridge » n'est plus requise,
sauf pour deux choses : les **captures visuelles** (`element_snapshot_tool`) et la **sélection /
navigation dans le canvas en direct**.

Ce que l'agent produit avec les bons outils, c'est un **arbre d'éléments Webflow réels** :
Section, Div Block, Heading, Paragraph, Link Block… avec de **vraies classes** (pas du style
inline), de **vraies variables**, de **vrais composants** et de **vraies interactions IX3.**
Tout est sélectionnable, restylable et éditable à la main ensuite.

### Le tableau de décision

| Besoin | Outil MCP | Ce que ça donne dans le Designer |
|---|---|---|
| Une section entière, vite | `data_whtml_builder` | HTML + CSS → **éléments natifs + classes natives** |
| Élément par élément, contrôle fin | `data_element_builder` | Élément natif au type choisi |
| Classes / styles | `data_style_tool` | Vraies classes Webflow, combo classes incluses |
| Tokens (couleurs, tailles, polices) | `data_variable_tool` | Vraies variables Webflow (≈ custom properties) |
| Composant réutilisable | `data_component_tool` + `data_component_builder` | Vrai composant, avec props, slots et variantes |
| Animations | `data_interactions_tool` | **Vraies interactions IX3**, pas du JavaScript |
| Texte, tag HTML, attributs, alt, id | `data_element_tool` / `data_element_settings_tool` | Réglages natifs du panneau Settings |
| Liste CMS (Collection List) | `data_element_settings_tool` sur un `DynamoWrapper` | Vraie Collection List avec source, filtres, tri |
| Composant React | **Code components** (via la CLI Webflow) | Composant natif, stylisable au panneau Style |
| ⚠️ Code arbitraire | `HtmlEmbed` / `CodeBlock` | **Le cas à éviter** sauf besoin réel |

> Autrement dit : l'embed HTML n'est plus le chemin par défaut, c'est l'exception.

---

## 1. Les règles techniques à connaître (source : serveur MCP 2.1.0 en direct)

Ces règles ne sont pas dans la doc publique sous cette forme — elles viennent du guide que le
serveur MCP renvoie lui-même à l'agent. Ce sont elles qui font la différence entre un résultat
propre et un résultat qui « sent l'IA ».

### 1.1 `data_whtml_builder` — le chemin rapide vers du natif

Il accepte une chaîne `html` **et** une chaîne `css`, et les convertit en éléments + styles Webflow.

Contraintes strictes :

- `html` doit avoir **un seul élément racine**. `<div><p>Hello</p></div>` ✅ — `<div>A</div><div>B</div>` ❌
- `html` ne doit **pas** contenir de balise `<style>` : le CSS passe par le paramètre `css`.
- `css` contient du **CSS brut**, sans balise `<style>`.
- **`@keyframes` interdits.**
- **Media queries limitées aux breakpoints Webflow**, aucune media query personnalisée :

  | Breakpoint | Media query à utiliser |
  |---|---|
  | Desktop (main) | aucune (breakpoint par défaut) |
  | Tablette (medium) | `@media screen and (max-width: 991px)` |
  | Mobile paysage (small) | `@media screen and (max-width: 767px)` |
  | Mobile portrait (tiny) | `@media screen and (max-width: 479px)` |

- `scope_component_id` permet d'insérer **à l'intérieur d'une définition de composant**.
- `return_element_info: true` renvoie l'arbre créé, utile pour enchaîner les retouches.

### 1.2 `data_element_builder` — les règles d'or

Extraites mot pour mot du guide MCP (section « Important rules for creating elements ») :

1. **Créer les styles d'abord**, si vous comptez les appliquer à la création — sinon la référence
   de style est invalide au moment de la création.
2. **Planifier avant d'appeler l'outil** : type d'élément, styles, attributs, usage.
3. L'élément créé **n'est pas sélectionné automatiquement** (`designer_tool > select_element` pour
   le sélectionner, `data_element_tool > query_elements` pour l'inspecter).
4. **Seuls `Container`, `Section`, `DivBlock` et certains éléments DOM acceptent des enfants.**
5. Seuls des **instances de composants** peuvent aller dans un slot — jamais un élément ordinaire.

Et la règle la plus importante pour un rendu « humain » :

> « When creating or updating elements, most users prefer using existing styles.
> **You should reuse styles if they exist**, unless the user explicitly wants new ones. »

### 1.3 Les breakpoints du `data_style_tool`

| Breakpoint | Portée |
|---|---|
| `xxl` (1920px) | écrans ≥ 1920px |
| `xl` (1440px) | écrans ≥ 1440px |
| `large` (1280px) | écrans ≥ 1280px |
| `main` | tous les écrans, sauf surcharge |
| `medium` (tablette) | écrans ≤ 991px |
| `small` (mobile paysage) | écrans ≤ 767px |
| `tiny` (mobile portrait) | écrans ≤ 478px |

`update_style` sans breakpoint → `main`. Sans `pseudo` → `noPseudo`.

### 1.4 Les détails qui font le « fait main »

- **`set_display_name`** : nomme l'élément dans le Navigator (« Hero / Content », « Feature card »).
  C'est le premier réflexe d'un designer humain, et un agent ne le fait jamais spontanément.
- **`set_tag`** : met la vraie sémantique (`section`, `header`, `nav`, `main`, `article`, `aside`).
  Un `DivBlock` partout est la signature d'une page générée.
- **`set_heading_level`** : hiérarchie h1→h6 correcte, un seul h1.
- **`set_style`** : ⚠️ **remplace toute la liste de styles** de l'élément ; plusieurs styles passés
  ensemble sont traités comme des **combo classes**.
- **`element_snapshot_tool`** : PNG de l'élément pour vérifier visuellement (Designer + Bridge App
  requis). À utiliser comme étape de contrôle avant de dire « c'est fait ».
- **`data_interactions_tool`** : le **seul** outil qui crée des animations. Appeler
  `data_interactions_tool > guide` **avant** d'écrire un payload (la validation applique des règles
  de parité Designer que le schéma JSON n'exprime pas). Deux pièges annoncés d'emblée :
  animer `opacity` sous `wf:transform` et **jamais** sous `wf:style` ; écrire les valeurs de
  propriétés en **tableaux/tuples**, jamais en objet `{from, to}`. Et surtout : **une écriture
  réussie ne prouve pas que l'animation tourne** — vérifier en Preview ou sur la page publiée.

> ⚠️ Point de vigilance : plusieurs sources publiques (y compris des pages de doc encore en ligne)
> affirment que le MCP **ne peut pas** créer d'interactions IX3. C'était vrai en v1 ; le serveur
> 2.1.0 expose bien `data_interactions_tool`. Fiez-vous au serveur, pas à ces pages.

---

## 2. Agent Instructions — la réponse à « quelles instructions donner à mon agent »

C'est **la** fonctionnalité que vous cherchez, et elle est native à Webflow depuis **MCP 2.0
(juillet 2026)**, avec la **génération automatique depuis le site** ajoutée le **2 septembre 2026**.

### 2.1 Le principe

Les **Agent Instructions** sont des documents **Markdown stockés sur le site Webflow** (pas dans
votre client). Le serveur MCP les sert automatiquement à **n'importe quel agent connecté** —
Claude, Cursor, Codex. Elles sont donc **portables** entre outils, contrairement à un
`CLAUDE.md` local.

Deux formes :

| Forme | Chemin | Quand |
|---|---|---|
| **Rule** | `rules/<nom>.md` ou `.mdc` | « À chaque fois que tu travailles sur ce site… » |
| **Skill** | `<nom-du-skill>/SKILL.md` | « Quand on te demande ce type de tâche… » |

Un skill peut avoir des fichiers compagnons : `<nom-du-skill>/<dossier>/<fichier>.md`.
Le nom du skill doit être en **kebab-case minuscule**.

### 2.2 Ce qui les rend puissantes : les références résolues

Une instruction peut **référencer les ressources réelles du site** — variables, classes,
composants, pages, collections CMS, locales, autres instructions. À la lecture, le serveur
**résout et inline** ces références (`read_instruction` avec `resolve_references: true`, le défaut).

Conséquence concrète : au lieu d'écrire « utilise le composant hero standard », vous pointez **le
composant réel**. L'agent ne peut plus choisir un composant au nom approchant ni travailler sur une
doc périmée.

### 2.3 Génération automatique

`data_agent_instructions_tool > generate_instruction` génère un **brouillon** de skill à partir du
site lui-même. Quatre types :

- `design-system`
- `brand-guidelines`
- `asset-guidelines`
- `cms-guidelines` (exige une collection CMS en source primaire)

C'est **asynchrone** : premier appel → `taskId`, puis rappels avec `task_id` jusqu'à
`finished`/`failed`, puis lecture du `resourceUri`. **Les résultats sont des brouillons** :
à relire avant de s'en servir comme référence.

### 2.4 Ce qu'il faut y mettre

Ce qu'un site ne peut pas deviner tout seul, et qu'il faut donc écrire :

- **Périmètre et objectif** du skill.
- **Références aux ressources réelles** (composants, variables, collections).
- **Règles de réutilisation** : quoi réutiliser, quand il est permis de créer du neuf.
- **Nommage et structure** : classes, composants, hiérarchie de sections, champs CMS.
- **Règles de contenu** : ton, longueurs, mentions légales, conventions de CTA.
- **Responsive et accessibilité** : comportement aux breakpoints, hiérarchie des titres, alt, contraste.
- **Étapes de vérification** avant de déclarer la tâche terminée.
- **Limites de sécurité** : ce qui exige une validation humaine (publier, supprimer, toucher aux
  styles globaux ou aux composants partagés, modifier le custom code, changer le schéma CMS).

Un jeu de fichiers prêt à l'emploi est fourni dans **`docs/webflow-agent-instructions/`** de ce
dépôt (voir §6).

### 2.5 Distribution

Les Agent Instructions peuvent voyager via les **Shared Libraries** : le design system et sa
gouvernance suivent les composants partagés d'un site à l'autre du workspace.

### 2.6 À ne pas confondre

| | Où c'est stocké | Portable ? |
|---|---|---|
| **Agent Instructions** (rules/skills du site) | Sur le site Webflow | ✅ tous les clients MCP |
| **Webflow Skills** (`github.com/webflow/webflow-skills`) | Dans votre client (Claude Code…) | ❌ local à l'agent |

Les deux sont complémentaires : les Skills Webflow sont des playbooks génériques
(audit de site, mise à jour CMS en masse, publication sûre…), les Agent Instructions portent
la connaissance **de votre site**.

**Docs :**
- <https://university.webflow.com/courses/create-agent-instructions-webflow>
- <https://university.webflow.com/course-lesson/plan-your-agent-instructions>
- <https://university.webflow.com/course-lesson/agent-instructions-skills-and-rules>
- <https://university.webflow.com/course-lesson/create-manage-agent-instructions>
- <https://university.webflow.com/glossary/agent-instructions>
- <https://webflow.com/updates/agent-instructions-generation>
- <https://developers.webflow.com/mcp/reference/skills>
- <https://github.com/webflow/webflow-skills>

---

## 3. Connecter Claude à Webflow

### 3.1 Les trois voies

| Voie | Pour qui | Commande / lien |
|---|---|---|
| **Claude Code** | Dev, workflows scriptés | `claude mcp add --transport http webflow https://mcp.webflow.com/mcp` puis `/mcp` pour l'OAuth |
| **Claude Desktop / claude.ai** | Usage quotidien, non-dev | Connecteur : `+` → « Add connectors » → Webflow (basculer « Featured » sur « All ») |
| **API / agent maison** | Automatisation serveur | Data API v2 + OAuth ou site token |

Endpoint de production : `https://mcp.webflow.com/mcp` — endpoint beta : `https://mcp.webflow.com/beta/mcp`.

### 3.2 Ce qu'il faut savoir sur l'autorisation

- **OAuth**, aucune clé API stockée localement.
- L'agent hérite **exactement** de vos rôles et permissions Webflow — il ne peut rien faire que
  vous ne puissiez faire.
- Toutes les modifications sont tracées dans le **site activity log**.
- ⚠️ **Une autorisation = un seul Workspace.** Pour un autre workspace, il faut réautoriser — et
  sur les connecteurs (Claude, ChatGPT), cela peut impliquer de supprimer et réinstaller le connecteur.
- Seuls les **owners/admins** d'un site peuvent l'autoriser ; les autres apparaissent grisés.

### 3.3 La Bridge App

Installée automatiquement à l'autorisation OAuth (pas depuis la marketplace publique).
Elle n'est **plus nécessaire** pour créer des éléments depuis MCP 2.0. Elle reste requise pour :

- les captures visuelles (`element_snapshot_tool`) ;
- lire/changer la sélection courante, la page courante, le mode, la branche ;
- naviguer dans le canvas.

Pour l'utiliser : ouvrir le site dans le Designer → lancer « Webflow MCP Bridge App » depuis le
panneau Apps → attendre la connexion → la laisser ouverte (on peut la réduire).

**Docs :**
- <https://developers.webflow.com/mcp/reference/overview>
- <https://developers.webflow.com/mcp/reference/getting-started>
- <https://developers.webflow.com/mcp/reference/how-it-works>
- <https://developers.webflow.com/mcp/installing/claude-code>
- <https://developers.webflow.com/mcp/faqs>
- <https://webflow.com/integrations/anthropic-claude>
- <https://webflow.com/feature/mcp>
- <https://github.com/webflow/mcp-server>
- <https://webflow.com/resources/mcp-starter-kit>
- <https://developers.webflow.com/mcp/examples/prompts>
- <https://webflow.com/blog/writing-prompts-webflow-mcp>
- <https://university.webflow.com/learning-paths/ai-the-webflow-mcp>

---

## 4. Le workflow recommandé, étape par étape

### Phase 0 — Préparer le terrain (une fois par site)

1. Connecter le MCP et autoriser le bon workspace.
2. Lancer `generate_instruction` pour `design-system`, `brand-guidelines` et `asset-guidelines`.
3. **Relire les brouillons générés** et les corriger — c'est là que se joue la qualité future.
4. Ajouter vos propres `rules/` : conventions de nommage, accessibilité, garde-fous (voir §6).
5. Écrire un skill `build-native-section/SKILL.md` qui décrit **votre** façon de construire.

### Phase 1 — Avant de construire (à chaque tâche)

1. `data_agent_instructions_tool > search_instructions` pour charger le contexte du site.
2. `data_style_tool > get_styles` et `data_variable_tool > get_variables` : **inventorier l'existant**.
3. `data_component_tool > get_all_components` : voir ce qui est déjà réutilisable.
4. `data_element_tool > get_all_elements` sur une page de référence : apprendre la structure maison.

> C'est l'étape que tout le monde saute, et c'est elle qui décide si le résultat ressemble
> à votre site ou à un template générique.

### Phase 2 — Construire

1. **Créer d'abord les styles et variables manquants** (`create_style`, `create_*_variable`).
2. Construire la structure :
   - section complète → `data_whtml_builder` (en respectant les contraintes du §1.1) ;
   - retouche fine → `data_element_builder`.
3. Poser la sémantique : `set_tag`, `set_heading_level`, `set_display_name`.
4. Réglages et contenu : `set_text`, `set_image_asset`, `set_link`, `set_attributes`, alt text.
5. Composants : `transform_element_to_component` pour transformer un bloc existant, puis
   `create_prop` pour exposer ce qui doit varier, et `data_component_builder` pour instancier.
6. Responsive : `update_style` aux breakpoints `medium` / `small` / `tiny`.
7. Animations : `data_interactions_tool > guide`, **puis** le payload.

### Phase 3 — Vérifier avant de dire « c'est fait »

1. `element_snapshot_tool` (Designer + Bridge ouverts) pour un contrôle visuel réel.
2. Vérifier : hiérarchie des titres, alt text, variables utilisées plutôt que valeurs en dur,
   aucune classe orpheline créée pour un seul élément.
3. Métadonnées de page : `pages_tool > update_page_settings`, schéma JSON-LD via
   `data_pages_tool > bulk_update_pages_schema_markup`.
4. **Ne pas publier sans validation** — et sur un site Enterprise, préférer une branche
   (`create_branch` → `publish_branch` → `merge_branch`).

---

## 5. Conventions pour que ce soit « propre comme fait main »

### 5.1 Un seul système de nommage

| Système | Pour qui | Lien |
|---|---|---|
| **Client-First** (Finsweet) | Équipes, livraison client, sites marketing | <https://finsweet.com/client-first/docs> |
| **Lumos** (Timothy Ricks) | Systèmes fluides, tokens, responsive avancé | <https://lumos.timothyricks.com/> |

Structure Client-First typique, à donner en exemple à l'agent :

```
section
└── container-large
    └── padding-global
        └── padding-section-large
            └── hero_component
                ├── hero_content
                └── hero_image-wrapper
```

⚠️ **Ne jamais mélanger deux systèmes** : `container`, `padding`, `section` existent dans les deux
avec des sens différents.

### 5.2 Les cinq signatures d'une page générée à éviter

1. **Une classe par élément** (`hero-heading-1`, `hero-heading-2`, `button-home`, `button-about`).
   → Réutiliser, combiner en combo classes.
2. **Des valeurs en dur** au lieu des variables (`#1a1a1a` plutôt que le token couleur).
3. **Des `DivBlock` partout** au lieu de `section` / `header` / `nav` / `main` / `article`.
4. **Aucun nom dans le Navigator** — que des « Div Block 12 ».
5. **Des surcharges responsive partout**, au lieu de quelques décisions nettes.

### 5.3 Variables plutôt que valeurs

Les variables Webflow fonctionnent comme des custom properties CSS et acceptent trois formes de
valeur : `static_value`, `existing_variable_id` (alias) ou `custom_value` (expression CSS libre —
`calc()`, `clamp()`, `color-mix()`…). Les **modes** de collection permettent en plus un
thème clair/sombre propre, applicable par style via `set_style_variable_mode`.

**Docs :**
- <https://developers.webflow.com/designer/reference/variables-overview>
- <https://webflow.com/webflow-way/design-systems/variables>
- <https://developers.webflow.com/designer/reference/creating-retrieving-elements>
- <https://developers.webflow.com/designer/reference/styles-overview>
- <https://developers.webflow.com/designer/reference/elements-overview>

---

## 6. Kit de démarrage fourni

Le dossier **`docs/webflow-agent-instructions/`** contient des fichiers prêts à coller dans
l'espace Instructions de votre site (ou à pousser via
`data_agent_instructions_tool > create_instruction`) :

| Fichier | Chemin Webflow | Rôle |
|---|---|---|
| `rules/native-first.md` | `rules/native-first.md` | Interdit l'embed HTML par défaut, impose les outils natifs |
| `rules/design-system.md` | `rules/design-system.md` | Réutilisation des styles et variables avant création |
| `rules/accessibility-seo.md` | `rules/accessibility-seo.md` | Sémantique, hiérarchie des titres, alt, métadonnées |
| `rules/safety.md` | `rules/safety.md` | Ce qui exige une validation humaine |
| `rules/localization.md` | `rules/localization.md` | Modèle Localize, identifiants de locale, CMS multilingue, impacts sur le design |
| `build-native-section/SKILL.md` | `build-native-section/SKILL.md` | Le playbook complet de construction d'une section |

Et deux fichiers pour l'installation :

- **`INSTALL-PROMPT.md`** — le prompt à coller chez votre agent. Il lui fait vérifier les
  informations à jour (version du serveur MCP, changelog), inventorier le site, **auditer les
  règles périmées** dans les instructions existantes et dans les fichiers du projet
  (`CLAUDE.md`, `.cursorrules`…), générer les instructions depuis le site, installer le kit,
  puis tester — avec un point d'arrêt avant chaque écriture significative.
- **`BUNDLE.md`** — les 5 instructions en un seul document avec leurs `kind` et `path`,
  pour que l'agent lise tout d'un coup. Régénéré par `make-bundle.py`.

Le dépôt étant public, l'agent peut lire ces fichiers par URL, **sans rien importer dans votre
projet** — le prompt contient déjà l'URL du bundle. Et une fois la phase d'installation passée,
les instructions vivent sur le site Webflow : le serveur MCP les sert à n'importe quel agent
connecté, sans fichier nulle part.

---

## 7. Panorama des nouveautés IA Webflow (2025 → sept. 2026)

### 7.1 Chronologie développeurs / agents

| Date | Nouveauté | Statut |
|---|---|---|
| 4 sept. 2025 | Le MCP supporte le Designer | Livré |
| 13 janv. 2026 | **Support Claude Code** + documentation des Webflow Skills | Livré |
| 16–24 mars 2026 | API Components & Elements étendues (création sans élément racine, lookup par ID, variantes, recherche) | **Beta publique** |
| 1er avr. 2026 | **MCP v1.2** — conversion HTML brut → éléments, outils d'éléments étendus | Livré |
| 30 avr. 2026 | **AI code components** — génération de composants React par l'IA | GA |
| 21 mai 2026 | **MCP 1.3** — +30 outils : composants, props, variantes, branches | Livré |
| 21 mai 2026 | DevLink exporte les Interactions (moteur GSAP) | Livré |
| 29 mai 2026 | **CLI 2.0** — `webflow library` → `webflow devlink`, `cloud create` → `cloud init`, Node ≥ 22.13 | Livré |
| 17 sept. 2026 | **`webflow apps` promu GA** — namespace canonique de Webflow Cloud dans la CLI (v2.8.0) ; `webflow cloud` déprécié | GA |
| **21 juil. 2026** | **MCP 2.0 / 2.0.1 — le tournant** : la plupart des opérations deviennent headless, Agent Instructions, permissions et audit renforcés | Livré |
| 24 août 2026 | Webflow disponible dans **Codex et ChatGPT** | Livré |
| 28 août 2026 | **Slot restrictions** — garde-fous sur ce qu'on peut insérer dans un slot | Livré |
| 2 sept. 2026 | **Agent Instructions Generation** | Déploiement |
| 2 sept. 2026 | **Composants dans le contenu CMS** (Rich Text) | Déploiement |
| 2 sept. 2026 | **Édition visuelle des AI code components** | Live |
| 2 sept. 2026 | **Breakpoint canvas** — tous les breakpoints côte à côte | Déploiement |
| 16 sept. 2026 | **Webflow AEO** disponible (Enterprise) | GA Enterprise |
| 19 sept. 2026 | Webflow AI activé par défaut sur Enterprise | Livré |
| 20 sept. 2026 | Serveur MCP en **2.1.0** (constaté en direct) | — |

### 7.2 Les fonctionnalités IA natives du produit

| Fonctionnalité | Ce que ça fait | Depuis | Plan |
|---|---|---|---|
| **AI Assistant** (Designer) | Assistant contextuel : génère/modifie des sections, du copy, du contenu CMS, des code components | oct. 2024, refonte agentique sept. 2025 | Selon workspace, crédits IA |
| **AI site builder** | Génère un site complet éditable depuis un prompt (multi-pages depuis 2026) | beta fév. 2025, GA **5 fév. 2026** | Tous, toggle admin |
| **AI code components** | Génère des composants React sur le canvas ; éditables visuellement depuis sept. 2026 | 30 avr. 2026 | Publication : Workspace payant ou Site CMS+ |
| **Optimize** | Suggestions CRO et variantes d'expérimentation | 29 mai 2025 | Add-on Optimize |
| **Analyze** | Analytics natif + insights trafic référé par IA | oct. 2024 / sept. 2025 | Add-on |
| **AEO** | Mesure la visibilité dans les moteurs de réponse, agents de recommandation en boucle fermée | privée avr. 2026, **Enterprise sept. 2026** | Enterprise |
| **AI SEO / alt text** | Audit et génération des titres, meta, alt, schema | 29 oct. 2025 | Site ou Workspace payant |
| **AI translation** | Traduction LLM gérant le Rich Text et le formatage inline ; ton et formalité par langue | mai 2026 / juil. 2026 | Localization ; ton = Advanced/Enterprise |

**Liens :**
- <https://webflow.com/blog/webflow-conf-2026-announcements>
- <https://webflow.com/blog/2026-builder-keynote>
- <https://webflow.com/blog/mcp-2-features>
- <https://developers.webflow.com/home/changelog>
- <https://webflow.com/updates>
- <https://webflow.com/updates/webflow-ai-assistant> · <https://webflow.com/updates/ai-site-builder-evolved>
- <https://webflow.com/updates/ai-code-components> · <https://webflow.com/updates/ai-seo-aeo>
- <https://webflow.com/blog/introducing-webflow-aeo> · <https://webflow.com/solutions/aeo>

---

## 8. Webflow Cloud, code components et CLI

_(Si « Cloud » dans votre question désignait **Webflow Cloud** et non Claude, cette section est la réponse.)_

### 8.1 Webflow Cloud

Hébergement managé d'applications full-stack, sur l'infrastructure Cloudflare Workers, **monté sous
une URL de votre site Webflow** (`example.com/app`) ou en app autonome. **GA depuis le 21 juillet 2025.**

- Frameworks : **Next.js**, **Astro**, **Vite**, statique sans framework.
- Déploiement : dépôt **GitHub** connecté (ou CLI pour les sources locales).
- Stockage : SQLite (D1), KV, Object Storage (R2).
- ⚠️ **Ne jamais coder en dur le chemin de montage** : pas de `basePath`/`assetPrefix` (Next.js) ni
  de `base`/`build.assetsPrefix` (Astro) — Webflow Cloud les injecte au build.
- Pilotable par l'agent via `data_apps_tool` (apps, environnements, déploiements, domaines, logs).
  ⚠️ Les **valeurs** de variables d'environnement passent par la CLI, jamais par le chat ni la
  ligne de commande.

<https://developers.webflow.com/webflow-cloud/intro> ·
<https://developers.webflow.com/webflow-cloud/environment/configuration> ·
<https://developers.webflow.com/webflow-cloud/examples> ·
<https://developers.webflow.com/webflow-cloud/changelog>

### 8.2 Code components (React dans Webflow)

Des composants React **réels**, importés via la CLI, qui deviennent des composants Webflow
stylisables dans le panneau Style. C'est la bonne réponse quand un besoin dépasse ce que le
Designer sait exprimer — **et c'est natif**, contrairement à un embed.

<https://developers.webflow.com/code-components/introduction> ·
<https://developers.webflow.com/code-components/component-architecture> ·
<https://developers.webflow.com/code-components/examples> ·
<https://webflow.com/feature/code-components>

### 8.3 CLI et DevLink

- CLI : <https://developers.webflow.com/cli/command-reference> — ⚠️ depuis le 17/09/2026, le
  namespace Webflow Cloud est **`webflow apps`** (`webflow cloud` est déprécié). Vérifier la
  surface courante avec `webflow apps --help`.
- Skills officiels : <https://github.com/webflow/webflow-skills> — installables par
  `webflow skills install` (avec `--dry-run`, `--agent claude-code,cursor`, lockfile).
- DevLink (export de composants Webflow vers React, interactions GSAP incluses depuis mai 2026) :
  <https://developers.webflow.com/devlink/reference/overview>

---

## 9. Écosystème tiers

| Outil | Connexion technique | Statut |
|---|---|---|
| **Relume** | App Marketplace (import de sitemap/pages/composants), copier-coller, Data API | GA — suppose la structure Client-First |
| **Figma to Webflow** | Plugin Figma → éléments/styles Webflow | GA — le responsive et le CMS restent manuels |
| **Cursor / Codex** | Même serveur MCP distant + OAuth | GA (Codex depuis le 24 août 2026) |
| **Wized** | Script runtime + attributs sur les éléments Webflow | GA |
| **Finsweet Attributes** | Librairie JS pilotée par attributs HTML | GA |
| **Make / Zapier / n8n** | Data API v2 + webhooks | GA |
| **v0, Lovable** | **Pas de connecteur Webflow natif vérifié** — production de code à reprendre | — |

<https://webflow.com/integrations/relume> · <https://webflow.com/integrations/figma-to-webflow> ·
<https://webflow.com/apps/ai> · <https://developers.webflow.com/data/reference/introduction>

---

## 10. SEO / AEO en 2026

- **`llms.txt`** : Webflow annonce une génération automatique (≈ août 2026). **À vérifier en
  production** sur `https://votredomaine.com/llms.txt` : code HTTP, redirections, `Content-Type`,
  mise à jour après publication.
- **`robots.txt`** : éditeur natif dans les réglages SEO. Les crawlers IA (GPTBot, ClaudeBot,
  PerplexityBot) se pilotent là — **rien n'est allowlisté automatiquement**.
- **Schema JSON-LD** : natif dans les réglages de page, lisible/écrivable par l'agent via
  `data_pages_tool > query_pages_schema_markup` et `bulk_update_pages_schema_markup`
  (API livrée le 18 mai 2026).
- **Sitemap** : inclusion par page et par item CMS pilotable via `data_sitemap_tool`
  (⚠️ les changements sur les items CMS sont **staged** — il faut republier).
- **Webflow AEO** : mesure des citations dans les moteurs de réponse + agents correctifs.
  **Enterprise uniquement** à ce jour.

---

## 11. Limites et pièges connus

| Limite | Détail |
|---|---|
| **Locales** | `data_localization_tool` **n'écrit que dans les locales secondaires** : la locale primaire est en lecture seule via cet outil (pour corriger le texte source, éditer l'élément avec `set_text`). ⚠️ Deux identifiants distincts cohabitent dans le champ `locales` du site : l'`id` de locale pour `data_localization_tool`, le `cmsLocaleId` pour `data_cms_tool`. |
| **Items CMS localisés** | ✅ **Créables** depuis MCP 2.x : `create_collection_items` accepte `cmsLocaleIds` ou `allCmsLocales: true`, et les variantes sont liées sous un seul item ID. La création n'écrit qu'en **staging** — publier ensuite avec `publish_collection_items`. La limite de 100 items par requête compte **chaque variante de locale**. *(Plusieurs sources publiques affirment encore l'inverse : c'était une limite de MCP 1.x.)* |
| **Branches** | **Enterprise uniquement.** Le champ `canBranch` **n'est pas** un signal d'éligibilité — seul `list_branches` fait foi (403 `not_enterprise_plan_site` = indisponible). |
| **Interactions** | Une écriture acceptée ne garantit pas que l'animation tourne. Vérifier en Preview. |
| **Accès et rôles** | Le MCP ne peut pas modifier les accès site/workspace, ajouter des utilisateurs ni attribuer des rôles. |
| **Polices** | Gère les polices personnalisées uploadées ; Google/Adobe Fonts passent par les réglages du site. |
| **Un workspace par autorisation** | Changer de workspace = réautoriser (parfois réinstaller le connecteur). |
| **Actions destructrices** | `remove_element`, `unregister_component`, `delete_asset`, `delete_font`, `delete_form_submission` : **irréversibles via l'API**. Faire confirmer. |
| **`set_style` remplace** | Passer une liste partielle écrase les classes existantes de l'élément. |
| **Dossiers d'assets** | Créables via l'API, **pas supprimables**. |
| **Doc publique en retard** | Certaines pages affirment encore des limites levées en 2.x. Le serveur MCP fait foi. |

---

## 12. Annexe — index des liens

**MCP & agents**
<https://developers.webflow.com/mcp/reference/overview> ·
<https://developers.webflow.com/mcp/reference/getting-started> ·
<https://developers.webflow.com/mcp/reference/how-it-works> ·
<https://developers.webflow.com/mcp/installing/claude-code> ·
<https://developers.webflow.com/mcp/faqs> ·
<https://developers.webflow.com/mcp/examples/prompts> ·
<https://developers.webflow.com/mcp/reference/skills> ·
<https://github.com/webflow/mcp-server> ·
<https://github.com/webflow/webflow-skills> ·
<https://webflow.com/resources/mcp-starter-kit> ·
<https://webflow.com/blog/writing-prompts-webflow-mcp>

**Agent Instructions**
<https://university.webflow.com/courses/create-agent-instructions-webflow> ·
<https://university.webflow.com/course-lesson/plan-your-agent-instructions> ·
<https://university.webflow.com/course-lesson/agent-instructions-skills-and-rules> ·
<https://university.webflow.com/course-lesson/create-manage-agent-instructions> ·
<https://webflow.com/updates/agent-instructions-generation>

**Designer API & développement**
<https://developers.webflow.com/designer/reference/introduction> ·
<https://developers.webflow.com/designer/reference/creating-retrieving-elements> ·
<https://developers.webflow.com/designer/reference/elements-overview> ·
<https://developers.webflow.com/designer/reference/styles-overview> ·
<https://developers.webflow.com/designer/reference/variables-overview> ·
<https://developers.webflow.com/data/reference/introduction> ·
<https://developers.webflow.com/reference>

**Webflow Cloud, code components, CLI**
<https://developers.webflow.com/webflow-cloud/intro> ·
<https://developers.webflow.com/code-components/introduction> ·
<https://developers.webflow.com/cli/command-reference> ·
<https://developers.webflow.com/devlink/reference/overview>

**Changelogs & annonces**
<https://developers.webflow.com/home/changelog> ·
<https://webflow.com/updates> ·
<https://webflow.com/blog/webflow-conf-2026-announcements> ·
<https://webflow.com/blog/mcp-2-features>

**Conventions**
<https://finsweet.com/client-first/docs> ·
<https://lumos.timothyricks.com/> ·
<https://webflow.com/webflow-way/design-systems/variables>
