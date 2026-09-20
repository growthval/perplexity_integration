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

Ce site utilise : `<Client-First | Lumos | système maison>`.

- Convention de classes : `<décrire, avec 3 exemples réels du site>`
- Convention de composants : `<décrire>`
- Structure de section attendue :

```
<coller ici la structure réelle du site, par ex.
section
└── container-large
    └── padding-global
        └── padding-section-large
            └── nom_component>
```

**Ne jamais mélanger deux systèmes de nommage.**

## Signes d'un travail bâclé, à ne pas produire

- Une classe unique par élément (`hero-heading-1`, `hero-heading-2`, `button-home`…).
- Des `DivBlock` là où `section`, `header`, `nav`, `main`, `article` ou `aside` conviennent.
- Des éléments sans nom dans le Navigator.
- Des surcharges responsive sur chaque élément au lieu de quelques décisions structurelles.

## Nommage dans le Navigator

Après création, donner un nom lisible à chaque bloc structurant avec
`data_element_tool > set_display_name` (ex. « Hero / Content », « Feature card », « CTA wrapper »).
Un Navigator rempli de « Div Block 14 » est un travail non terminé.
