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
   — par exemple `<page de référence du site>` — pour apprendre la structure maison.

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
