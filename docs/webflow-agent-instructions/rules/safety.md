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
