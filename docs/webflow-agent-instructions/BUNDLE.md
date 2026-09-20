# BUNDLE — contenu des Agent Instructions à installer

Ce fichier regroupe les 6 instructions à créer sur le site Webflow, dans un seul document, pour
qu'un agent puisse tout lire d'un coup. Il est **généré** depuis les fichiers du dossier : ne pas
l'éditer directement, éditer les fichiers sources puis relancer `python3 make-bundle.py`.

Chaque section ci-dessous indique le `kind` et le `path` à passer à
`data_agent_instructions_tool > create_instruction`. Le corps de l'instruction est le bloc
markdown qui suit, **sans** la ligne de titre `## Instruction N`.

Les emplacements entre `<…>` sont à remplir avec les ressources réelles du site, découvertes par
l'inventaire (Phase 1 du prompt d'installation). Une instruction laissée générique ne change rien
au comportement de l'agent.

---

## Instruction 1 — `rules/native-first.md`

- `kind`: `rule`
- `path`: `rules/native-first.md`

<!-- début du corps de l'instruction -->

# Règle — Tout doit être natif et éditable dans le Designer

Cette règle s'applique à **toute** création ou modification de structure sur ce site.

## Principe

Ce qui est produit doit être indiscernable d'un travail fait à la main dans le Designer :
de vrais éléments Webflow, de vraies classes, de vraies variables, de vrais composants.
Un intégrateur doit pouvoir reprendre la page sans jamais toucher à du code.

## Ce qu'il faut utiliser

| Besoin | Outil |
|---|---|
| Section ou bloc complet | `data_whtml_builder` |
| Élément précis | `data_element_builder` |
| Classes | `data_style_tool` |
| Tokens | `data_variable_tool` |
| Composant réutilisable | `data_component_tool` + `data_component_builder` |
| Animation | `data_interactions_tool` |

## Ce qui est interdit par défaut

- **Ne pas** créer d'élément `HtmlEmbed` ou `CodeBlock` pour produire une mise en page.
- **Ne pas** injecter de balise `<style>` ni de CSS via le custom code de page pour styler
  des éléments qui pourraient l'être par des classes Webflow.
- **Ne pas** enregistrer de script (`data_scripts_tool`) pour reproduire un comportement
  que les interactions Webflow savent faire.

Un embed, un script ou du custom code ne se justifient que pour une fonctionnalité que Webflow
ne sait pas exprimer nativement (widget tiers, logique applicative, intégration externe).
Dans ce cas : **le dire explicitement, expliquer pourquoi, et demander l'accord** avant de le faire.
Si le besoin est du code applicatif réutilisable, proposer un **code component** plutôt qu'un embed.

## Contraintes de `data_whtml_builder`

- `html` : **un seul élément racine**, aucune balise `<style>`.
- `css` : CSS brut, **sans `@keyframes`**.
- Media queries **uniquement** aux breakpoints Webflow :
  - tablette : `@media screen and (max-width: 991px)`
  - mobile paysage : `@media screen and (max-width: 767px)`
  - mobile portrait : `@media screen and (max-width: 479px)`

## Contraintes de `data_element_builder`

- Créer les styles **avant** de créer les éléments qui les portent.
- Seuls `Container`, `Section`, `DivBlock` et certains éléments DOM acceptent des enfants.
- Seules des instances de composants peuvent être placées dans un slot.
- `set_style` **remplace toute la liste de styles** de l'élément : toujours passer la liste complète.

<!-- fin du corps de l'instruction -->

---

## Instruction 2 — `rules/design-system.md`

- `kind`: `rule`
- `path`: `rules/design-system.md`

<!-- début du corps de l'instruction -->

# Règle — Réutiliser le design system avant de créer

## Inventaire obligatoire avant toute construction

Avant de créer un style, une variable ou un composant, inspecter l'existant :

1. `data_style_tool > get_styles`
2. `data_variable_tool > get_variable_collections` puis `get_variables`
3. `data_component_tool > get_all_components`
4. `data_element_tool > get_all_elements` sur une page de référence, pour apprendre la structure maison

## Réutilisation

- **Toujours réutiliser** un style existant qui convient. Ne créer une classe que si aucune
  existante ne répond au besoin — et le signaler dans le compte rendu.
- **Jamais de valeur en dur** pour une couleur, un espacement, une taille de police ou un rayon
  si une variable existe. Utiliser la variable.
- **Ne pas dupliquer une variable** qui existe déjà sous un autre nom.
- Préférer une **combo class** à une nouvelle classe pour une variation mineure.
- Préférer une **instance de composant existant** à une reconstruction d'éléments.

## Nommage

Ce site utilise **Client-First (Finsweet)**, avec des sections issues de la bibliothèque de
composants **Relume**. C'est le système de référence : toute construction nouvelle doit s'y
conformer.

### Deux familles de classes, à ne pas confondre

| Famille | Forme | Rôle | Exemples réels du site |
|---|---|---|---|
| **Utilitaires Client-First** | `mot-mot` (tirets) | Mise en page, espacement, largeur, typo — **réutilisables partout** | `padding-global`, `padding-section-large\|medium\|small`, `container-large\|medium\|small`, `max-width-*`, `heading-style-h1..h6`, `text-size-*`, `text-weight-*`, `text-style-*`, `text-align-center`, `margin-bottom`, `margin-top`, `button`, `button-group` |
| **Classes de composant Relume** | `bloc_élément` (underscore) | Identifient un bloc précis — **propres à ce composant** | `section_header30`, `header30_content`, `layout34_component`, `slider6_component`, `slider6_mask`, `layout370_card-small`, `layout486_content-left`, `layout486_number-wrapper` |

Règles qui en découlent :

- Un **utilitaire** ne se modifie jamais pour un besoin ponctuel : il est partagé par tout le site.
  Si un espacement ne convient pas, utiliser un autre utilitaire existant, pas retoucher celui-ci.
- Une **classe de composant** porte le préfixe de son bloc. Une nouvelle carte dans `layout370`
  s'appelle `layout370_card-small-<quelque-chose>`, jamais `carte-bleue`.
- Les wrappers structurels globaux sont `page-wrapper` puis `main-wrapper`.
- Le suffixe d'une classe de composant peut être composé : `layout486_content-left`,
  `layout486_number-wrapper` — underscore pour séparer le bloc, tirets à l'intérieur du suffixe.

### Structure de section attendue

Relevée sur la page **Accueil**, à reproduire pour toute nouvelle section :

```
section_<nom><NN>.color-scheme-N      ← Section + son schéma de couleur (1 à 4)
└── padding-global                    ← utilitaire : gouttières latérales
    └── container-large               ← utilitaire : largeur max
        └── padding-section-large     ← utilitaire : rythme vertical
            └── <nom><NN>_component   ← classe de composant
                └── text-align-center ← utilitaires empilés, un rôle chacun
                    └── max-width-xlarge
                        ├── margin-bottom
                        ├── text-size-medium
                        └── margin-top
```

**Toute section porte une classe combo `color-scheme-1` à `color-scheme-4`** en plus de sa classe
de section. Ne jamais poser une couleur en dur sur une section : choisir le schéma.

**L'empilement d'utilitaires est voulu, ne pas l'aplatir.** Dans Client-First, chaque div porte
une seule responsabilité (alignement, largeur max, marge). La tentation de fusionner
`text-align-center` + `max-width-xlarge` + `margin-bottom` en une seule classe custom casse le
système : elle produit une classe non réutilisable et rend la page impossible à maintenir pour
un humain. Empiler, c'est le comportement correct.

### Composants

Sont déjà des **composants** sur ce site (icône verte dans le Navigator) : `Global Styles`,
`Preheader`, `navbar11_component`. Ne jamais les reconstruire ni les détacher — les instancier.

Les numéros Relume (`header30`, `layout34`, `layout370`, `slider6`, `navbar11`) identifient le
modèle d'origine. En ajoutant une section issue de Relume, **garder son numéro** dans les noms de
classes : c'est ce qui permet de retrouver le modèle plus tard.

⚠️ Cette structure est relevée sur une seule page. En phase d'inventaire, la **confirmer sur deux
ou trois autres pages** et signaler tout écart plutôt que de généraliser.

### Variables — les 4 collections réelles

| Collection | Contenu |
|---|---|
| **Primitives** | Palettes (Vulcan, Blumine, Sea Green, El Salva, Affair), neutres, opacités, Bleu CTA `#1B56FF` |
| **Color Schemes** | Schémas 1 à 4, chacun avec Text / Background / Foreground / Border / Accent |
| **Typography** | Heading = Cabin, Body = Inter |
| **UI Styles** | Rayons 0px partout, bordures 1px |

Les noms réels ressemblent à `--color-scheme-1--text` et `--_primitives---colors--vulcan`.
**Ne jamais inventer un nom de variable** de la forme `color--primary` ou `spacing--lg` : ça
n'existe pas ici. Lire `get_variables` et utiliser les identifiants renvoyés.

⚠️ Le **Bleu CTA `#1B56FF`** n'est câblé dans aucun Color Scheme aujourd'hui : il est appliqué en
direct sur `.button`. Ne pas reproduire ce raccourci sur de nouveaux éléments sans le signaler.

### ⚠️ Attributs Finsweet — à ne jamais écraser

Les Collection Lists du site portent des attributs **Finsweet Attributes** (`fs-list-instance`,
`fs-list-element`) qui pilotent filtres, tris et pagination côté client.

**`set_attributes` remplace la liste complète d'attributs de l'élément**, et la clé `attributes` de
`set_settings` aussi. Écrire un seul attribut sans reprendre les autres **supprime les `fs-*` et
casse la liste en production**, silencieusement.

Procédure obligatoire sur tout élément d'une Collection List :
`get_attributes` → reprendre l'intégralité de la liste → y ajouter ou modifier → `set_attributes`.

### Dette de nommage existante

Trois conventions coexistent aujourd'hui sur le site :

| Convention | Exemples | Quoi en faire |
|---|---|---|
| **Relume / Client-First** | `section_layout34`, `layout486_number` | ✅ La référence — tout le neuf s'écrit comme ça |
| kebab custom | `lp-*`, `b2b-*` | ⚠️ Legacy : ne pas étendre, ne pas renommer en masse sans plan validé |
| mixte | `preheader_*` | ⚠️ Idem |

**Tout élément nouveau suit la convention Relume/Client-First**, sans exception. Le legacy se
tolère là où il est, il ne se propage pas. Signaler, ne pas renommer de sa propre initiative :
un renommage de classe se répercute sur toutes les pages qui l'utilisent.

**Ne jamais mélanger deux systèmes de nommage** : pas de Lumos, pas de Tailwind, pas de BEM
inventé pour l'occasion.

**Référence Client-First** : <https://finsweet.com/client-first/docs>

## Signes d'un travail bâclé, à ne pas produire

- Une classe unique par élément (`hero-heading-1`, `hero-heading-2`, `button-home`…).
- Des `DivBlock` là où `section`, `header`, `nav`, `main`, `article` ou `aside` conviennent.
- Des éléments sans nom dans le Navigator.
- Des surcharges responsive sur chaque élément au lieu de quelques décisions structurelles.

## Nommage dans le Navigator

Après création, donner un nom lisible à chaque bloc structurant avec
`data_element_tool > set_display_name` (ex. « Hero / Content », « Feature card », « CTA wrapper »).
Un Navigator rempli de « Div Block 14 » est un travail non terminé.

<!-- fin du corps de l'instruction -->

---

## Instruction 3 — `rules/accessibility-seo.md`

- `kind`: `rule`
- `path`: `rules/accessibility-seo.md`

<!-- début du corps de l'instruction -->

# Règle — Sémantique, accessibilité et SEO

## Sémantique HTML

- Utiliser `data_element_settings_tool > set_tag` pour donner le bon tag :
  `section`, `header`, `nav`, `main`, `footer`, `article`, `aside`.
- Un `DivBlock` générique est le dernier recours, pas le premier.

## Titres

- **Un seul `h1` par page.**
- Hiérarchie sans saut de niveau (`h2` → `h3`, jamais `h2` → `h4`).
- Régler le niveau avec `data_element_tool > set_heading_level`, pas en changeant seulement le style.

## Images

- Toute image porteuse de sens a un **alt descriptif**.
- Les images décoratives ont un alt vide (`alt_text: null` marque l'asset comme décoratif).
- Passer par `asset_tool > upload_image_by_url` ou `data_assets_tool`, jamais par une URL externe
  en dur dans un embed.

## Liens et boutons

- Un lien qui navigue est un `Link Block` / `TextLink` avec `set_link` — pas un div cliquable.
- Libellés explicites : jamais « cliquez ici » seul.

## Responsive

Vérifier la mise en page aux breakpoints `medium` (≤991px), `small` (≤767px) et `tiny` (≤478px).
Privilégier des choix structurels (flex/grid qui se réorganisent) plutôt qu'une surcharge par élément.

## Métadonnées

Avant de considérer une page terminée :

- Titre et meta description renseignés (`pages_tool > update_page_settings`).
- Image Open Graph.
- Schéma JSON-LD si le type de page s'y prête
  (`data_pages_tool > bulk_update_pages_schema_markup`).
- Inclusion sitemap cohérente (`data_sitemap_tool`) — les changements sur les items CMS sont
  **staged** et nécessitent une republication.

<!-- fin du corps de l'instruction -->

---

## Instruction 4 — `rules/localization.md`

- `kind`: `rule`
- `path`: `rules/localization.md`

<!-- début du corps de l'instruction -->

# Règle — Localisation (Webflow Localize, locale secondaire EN)

Ce site utilise l'add-on **Localize**.

- **Locale primaire : français (affichée `FR-FR` dans le Designer).** C'est la langue source.
- **Locale secondaire : anglais.**

⚠️ **Ne jamais deviner les identifiants.** Le code affiché dans le sélecteur du Designer n'est pas
un identifiant utilisable par l'API. Lire `data_sites_tool > get_site` → champ `locales`, et en
extraire, pour l'anglais, **l'`id` de locale** (pour `data_localization_tool`) **et le
`cmsLocaleId`** (pour `data_cms_tool`) — voir la section suivante.

## Le modèle mental, avant tout

**Une locale secondaire n'est pas une copie du site.** C'est une **surcouche de traduction** sur la
même structure : mêmes pages, mêmes éléments, mêmes composants, mêmes items CMS. Seul le contenu
change.

Conséquences, non négociables :

- **Ne jamais dupliquer une page pour en faire la version EN.** Pas de `/en/accueil` créée à la main.
- **Ne jamais dupliquer un composant** pour une variante linguistique.
- **Ne jamais créer une collection CMS parallèle** pour l'anglais.

Si tu es tenté de dupliquer quelque chose pour l'anglais, c'est que tu as le mauvais modèle :
arrête-toi et demande.

## Découvrir les locales — et le piège des deux identifiants

`data_sites_tool > get_site` renvoie le champ `locales`, où la locale primaire est marquée
séparément des secondaires. **Attention, deux identifiants distincts y cohabitent :**

| Identifiant | À utiliser avec |
|---|---|
| `id` de la locale | `data_localization_tool` (contenu statique, composants, props) |
| `cmsLocaleId` | `data_cms_tool` (items CMS) |

Les confondre produit des erreurs ou des écritures dans la mauvaise locale. Relis le champ
`locales` plutôt que de réutiliser un identifiant de mémoire.

## Contenu statique et composants

`data_localization_tool` **n'écrit que dans les locales secondaires**. La locale primaire est en
**lecture seule** via cet outil : pour corriger le texte source, éditer l'élément lui-même
(`data_element_tool > set_text`) sur la locale primaire.

Workflow :

1. `data_sites_tool > get_site` — récupérer les identifiants de locale.
2. `data_localization_tool > list_components` — les composants localisables.
3. Lire l'état actuel : `get_page_content` / `get_component_content`
   (avec `localeId` pour la locale secondaire, sans pour la primaire).
4. Écrire : `update_static_content` (page), `update_component_content` (composant),
   `update_component_properties` (valeurs de props) — `localeId` **obligatoire**, secondaire uniquement.

## CMS multilingue

**Créer des items dans plusieurs locales est possible** — c'est une limite de l'ancienne version
du MCP, plus d'actualité :

- **Nouvel item dans des locales précises** : `create_collection_items`, entrée sans `id`,
  avec `cmsLocaleIds`. Les variantes sont **liées** et partagent un seul item ID.
- **Nouvel item dans toutes les locales** : `allCmsLocales: true` sur l'entrée.
  Seul `true` est accepté, et il ne peut pas accompagner `id` ni `cmsLocaleIds`.
- **Ajouter une locale à un item existant** : même `create_collection_items`, avec l'`id` de
  l'item et les nouvelles locales dans `cmsLocaleIds`.
- **Contenu différent par locale** : plusieurs entrées partageant le même `id`, chacune avec
  **une seule** locale dans `cmsLocaleIds` et son propre `fieldData`.
- **Lire** : `list_collection_items` avec `allCmsLocales: true`, ou `cmsLocaleId`
  (liste séparée par virgules pour plusieurs). Chaque variante revient comme une ligne distincte.

Deux points à ne pas oublier :

- **La création n'écrit qu'en staging.** Publier ensuite avec `publish_collection_items`, en
  passant les `cmsLocaleIds` voulus dans chaque `{ id, cmsLocaleIds }`.
- **La limite de 100 items par requête compte chaque variante de locale**, pas chaque item.
  Un lot de 60 items en 2 locales fait 120 : découper.

## Conséquences sur la construction des pages

- **Un HTML embed n'est pas localisable** comme un nœud de texte natif. Tout texte destiné à être
  traduit doit être dans un vrai élément Webflow. C'est une raison de plus d'appliquer
  `rules/native-first.md` sans exception.
- **Ne jamais figer une hauteur** sur un bloc contenant du texte : la longueur change d'une langue
  à l'autre. Laisser le contenu dicter la hauteur, prévoir le retour à la ligne.
- Même prudence sur les boutons, onglets et navigations : un libellé qui tient sur une ligne en
  français peut en prendre deux en anglais, ou l'inverse.
- Vérifier le rendu **dans les deux locales** avant de considérer une section terminée.

## Limites connues

- Le **custom code libre au niveau page** est mono-locale : si un `localeId` est passé, il doit
  être celui de la locale **primaire**.
- Les contrôles de **ton et de formalité** par langue de la traduction IA relèvent de l'offre
  Localize avancée. Ne pas présumer qu'ils sont disponibles : tester, et me dire ce que tu obtiens.
- Vérifier le comportement `hreflang` et les métadonnées SEO par locale sur le site publié plutôt
  que de le supposer.

<!-- fin du corps de l'instruction -->

---

## Instruction 5 — `rules/safety.md`

- `kind`: `rule`
- `path`: `rules/safety.md`

<!-- début du corps de l'instruction -->

# Règle — Garde-fous et validation humaine

## Actions qui exigent une confirmation explicite

Ne jamais faire sans accord formel, demandé et obtenu dans la conversation :

- **Publier** le site ou des items CMS.
- **Supprimer** quoi que ce soit : `remove_element`, `unregister_component`, `delete_asset`,
  `delete_font`, `delete_collection_field`, `delete_form_submission`, `delete_variable`.
  Ces actions sont **irréversibles via l'API**.
- Modifier un **style global** ou un **composant partagé** (impact sur tout le site).
- Modifier le **custom code** de site ou de page.
- Changer le **schéma CMS** (champs, groupes de champs).
- Toute opération touchant **plus de 5 pages** ou **plus de 20 items CMS** d'un coup.
- Créer un **dossier d'assets** — ils ne sont pas supprimables ensuite.
- **Compresser des assets** : le fichier d'origine n'est pas conservé.

## Avant d'agir

- Annoncer le plan : quels éléments, quels styles, quels composants seront créés ou modifiés.
- **Ce site est sur un plan site CMS : le branching n'est pas disponible.** Il exige un
  workspace Enterprise. Ne propose pas, ne planifie pas et ne mentionne pas de workflow en
  branche. Si vérification nécessaire, `list_branches` est le **seul** test valable : un 403
  `not_enterprise_plan_site` est définitif pour tout le site — ne le retente pas et n'essaie pas
  une autre action de branche en espérant un autre résultat. Le champ `canBranch` n'est **pas**
  un signal d'éligibilité.
- À la place, pour toute refonte non triviale, travailler sur une copie :
  1. dupliquer la page — `data_pages_tool > create_page` avec `duplicateOf` et `draft: true` ;
  2. construire sur la copie, jamais sur la page en production ;
  3. publier **uniquement sur le domaine de staging `*.webflow.io`** pour faire valider,
     jamais sur le domaine principal ;
  4. basculer seulement après validation explicite.

## Avant de déclarer une tâche terminée

1. Capture visuelle avec `element_snapshot_tool` (Designer + Bridge App ouverts).
2. Vérifier : hiérarchie des titres, alt text, variables utilisées, aucune classe orpheline.
3. Vérifier le rendu aux trois breakpoints mobiles.
4. **Lister explicitement** tout ce qui a été créé : nouvelles classes, nouvelles variables,
   nouveaux composants, nouvelles pages.
5. **Signaler tout écart** au design system, plutôt que de le passer sous silence.

Une écriture réussie n'est pas une preuve de bon fonctionnement — en particulier pour les
interactions, où un payload accepté peut ne jamais animer. Vérifier en Preview ou sur la page publiée.

<!-- fin du corps de l'instruction -->

---

## Instruction 6 — `build-native-section/SKILL.md`

- `kind`: `skill`
- `path`: `build-native-section/SKILL.md`

<!-- début du corps de l'instruction -->

# Skill — Construire une section native

Utiliser ce skill quand on demande de **créer ou refondre une section de page** sur ce site
(hero, features, témoignages, pricing, CTA, footer…).

## Objectif

Produire une section qui ressemble en tout point à un travail fait à la main dans le Designer :
structure sémantique, classes réutilisées, variables du design system, composants existants,
responsive maîtrisé — et **aucun embed HTML**.

## Étape 1 — Comprendre le site avant de toucher à quoi que ce soit

1. `data_agent_instructions_tool > search_instructions` : charger les règles du site.
2. `data_style_tool > get_styles` : inventorier les classes disponibles.
3. `data_variable_tool > get_variables` : inventorier les tokens.
4. `data_component_tool > get_all_components` : voir ce qui est réutilisable.
5. `data_element_tool > get_all_elements` (depth 3-4) sur une page de référence
   — **la page Accueil** est la référence : elle porte les sections Relume de base
   (`section_header30`, `section_layout34`) dans la structure Client-First du site.

**Ne pas sauter cette étape.** C'est elle qui décide si le résultat ressemble au site ou à un template.

## Étape 2 — Annoncer le plan

Avant d'écrire, énoncer :

- la structure prévue (arbre d'éléments) ;
- les classes **réutilisées** et celles qu'il faudra **créer** (avec justification) ;
- les variables utilisées ;
- les composants réutilisés ;
- ce qui nécessite une validation.

## Étape 3 — Préparer les styles

Créer d'abord, avec `data_style_tool > create_style`, **uniquement** les classes qui manquent.
Utiliser les **noms longs de propriétés CSS**. Pour une variation mineure, préférer une
combo class (`parent_style_name`).

## Étape 4 — Construire la structure

Deux chemins, au choix selon la complexité :

**A. Section complète → `data_whtml_builder`**
- `html` : un seul élément racine, pas de `<style>`.
- `css` : CSS brut, pas de `@keyframes`, media queries uniquement à 991 / 767 / 479 px.
- `return_element_info: true` pour récupérer l'arbre créé.

**B. Construction fine → `data_element_builder`**
- Élément par élément, en partant du conteneur.
- Rappel : seuls `Container`, `Section`, `DivBlock` et certains DOM acceptent des enfants.

## Étape 5 — Sémantique et finition

Pour chaque élément structurant :

1. `data_element_settings_tool > set_tag` — vrai tag HTML.
2. `data_element_tool > set_heading_level` — hiérarchie des titres.
3. `data_element_tool > set_display_name` — nom lisible dans le Navigator.
4. `data_element_tool > set_text` / `set_image_asset` / `set_link` — contenu réel.
5. Alt text sur les images.

## Étape 6 — Composants

Si la section contient un motif répété (carte, item de liste, bloc de témoignage) :

1. Construire **un** exemplaire propre.
2. `data_component_tool > transform_element_to_component`.
3. `data_component_props_tool > create_prop` pour exposer ce qui varie
   (titre, texte, image, lien).
4. `data_component_builder` pour instancier les autres, puis
   `set_component_instance_prop_values` pour leur contenu.

Ne pas dupliquer dix fois le même bloc d'éléments : c'est la signature d'un travail non réfléchi.

## Étape 7 — Responsive

`data_style_tool > update_style` aux breakpoints `medium`, `small`, `tiny`.
Privilégier quelques décisions structurelles nettes plutôt qu'une surcharge par élément.

## Étape 8 — Animations (si demandé)

1. `data_interactions_tool > guide` **avant** d'écrire le payload.
2. Animer `opacity` sous `wf:transform`, **jamais** sous `wf:style`.
3. Valeurs de propriétés en **tableaux/tuples**, jamais en objet `{from, to}`.
4. Vérifier en Preview : une écriture acceptée n'anime pas forcément.

## Étape 9 — Vérifier et rendre compte

1. `element_snapshot_tool` sur la section (Designer + Bridge App ouverts).
2. Contrôler : hiérarchie des titres, alt text, variables plutôt que valeurs en dur,
   aucune classe créée pour un seul élément, rendu aux trois breakpoints mobiles.
3. Rendre compte en listant : éléments créés, **classes créées** (et pourquoi),
   **variables créées**, composants créés, et tout écart au design system.
4. **Ne pas publier** sans validation explicite.

<!-- fin du corps de l'instruction -->

---
