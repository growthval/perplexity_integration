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
