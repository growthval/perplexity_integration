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
