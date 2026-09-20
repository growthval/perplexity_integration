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
- Sur un site Enterprise, préférer une **branche** (`create_branch` → travail → `publish_branch`
  pour prévisualiser → `merge_branch`) plutôt que d'éditer la page principale.
  Vérifier la disponibilité avec `list_branches` — et **seulement** avec ça : le champ `canBranch`
  n'est pas un signal d'éligibilité.

## Avant de déclarer une tâche terminée

1. Capture visuelle avec `element_snapshot_tool` (Designer + Bridge App ouverts).
2. Vérifier : hiérarchie des titres, alt text, variables utilisées, aucune classe orpheline.
3. Vérifier le rendu aux trois breakpoints mobiles.
4. **Lister explicitement** tout ce qui a été créé : nouvelles classes, nouvelles variables,
   nouveaux composants, nouvelles pages.
5. **Signaler tout écart** au design system, plutôt que de le passer sous silence.

Une écriture réussie n'est pas une preuve de bon fonctionnement — en particulier pour les
interactions, où un payload accepté peut ne jamais animer. Vérifier en Preview ou sur la page publiée.
