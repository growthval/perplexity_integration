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
