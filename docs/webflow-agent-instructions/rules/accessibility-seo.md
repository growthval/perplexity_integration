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
