# Kit de démarrage — Agent Instructions Webflow

De quoi faire construire à un agent IA (Claude, Cursor, Codex…) des pages Webflow **natives** et
**propres** : de vrais éléments, de vraies classes, de vrais composants, éditables dans le Designer.

## Les fichiers

| Fichier | À quoi ça sert |
|---|---|
| **`INSTALL-PROMPT.md`** | **Le prompt à coller chez ton agent.** Il fait tout : vérifier les infos à jour, inventorier le site, auditer les règles périmées, générer, installer, tester. |
| **`BUNDLE.md`** | Les 5 instructions en un seul document, avec leurs `kind` et `path`. C'est ce que l'agent lit pour les installer. Généré — ne pas éditer à la main. |
| `rules/native-first.md` | Interdit l'embed HTML par défaut, impose les outils natifs et leurs contraintes |
| `rules/design-system.md` | Inventaire et réutilisation des styles, variables et composants avant toute création |
| `rules/accessibility-seo.md` | Sémantique, hiérarchie des titres, alt, responsive, métadonnées |
| `rules/safety.md` | Ce qui exige une validation humaine, et la vérification avant de dire « c'est fait » |
| `build-native-section/SKILL.md` | Le playbook en 9 étapes pour construire une section |
| `make-bundle.py` | Régénère `BUNDLE.md` après modification d'un fichier d'instruction |

## Utilisation

1. Ouvre une session avec ton agent, **MCP Webflow connecté et autorisé** sur le bon workspace.
2. Donne-lui accès à ce dossier (ou au moins à `BUNDLE.md`).
3. Colle le contenu de `INSTALL-PROMPT.md`.
4. Réponds à ses questions aux points d'arrêt : choix du site, validation de l'audit de conflits,
   choix de la collection CMS, décisions sur les instructions déjà présentes.

Le prompt est conçu pour **s'arrêter et demander** avant chaque écriture significative, et pour
ne rien publier.

## Accès sans rien copier dans ton projet

Le dépôt est **public** : ton agent peut lire ces fichiers directement, tu n'as aucun fichier à
importer. Trois voies, de la plus simple à la plus intégrée.

**1. Par URL (le plus simple, marche partout).** Le prompt contient déjà l'URL du bundle.
Fichiers bruts :

```
https://raw.githubusercontent.com/growthval/perplexity_integration/claude/busy-franklin-i7zvly/docs/webflow-agent-instructions/INSTALL-PROMPT.md
https://raw.githubusercontent.com/growthval/perplexity_integration/claude/busy-franklin-i7zvly/docs/webflow-agent-instructions/BUNDLE.md
```

⚠️ **Le cache.** `raw.githubusercontent.com` met les URLs de branche en cache environ 5 minutes.
Si tu modifies une règle et relances l'agent dans la foulée, il lira l'ancienne version. Parade :
remplace le nom de branche par un **SHA de commit** — cette forme est immuable et servie
immédiatement, et elle fige aussi la version que l'agent installe.

```
https://raw.githubusercontent.com/growthval/perplexity_integration/<sha>/docs/webflow-agent-instructions/BUNDLE.md
```

(`git rev-parse HEAD` pour obtenir le SHA.)

**2. En connectant le dépôt à ton agent.** Claude Code sur le web : ajoute
`growthval/perplexity_integration` aux sources de la session. Claude Code en local ou Cursor :
`git clone` **à côté** de ton projet, pas dedans, et pointe l'agent dessus.

**3. La vraie réponse à long terme : ne plus avoir besoin du dépôt du tout.** Une fois la
Phase 4 passée, les instructions vivent **sur le site Webflow**. Le serveur MCP les sert
automatiquement à n'importe quel agent connecté — Claude, Cursor, Codex — sans aucun fichier
nulle part. Ce dépôt ne sert plus qu'à la maintenance du kit.

## Installation manuelle (sans agent)

Site Webflow → section *Instructions* → créer une Rule ou un Skill → coller le contenu du fichier
correspondant, au `path` indiqué dans `BUNDLE.md`.

## À personnaliser

Les passages entre `<…>` sont des emplacements à remplir avec tes vraies ressources : système de
nommage, structure de section type, classes les plus utilisées, page de référence. Une instruction
qui **référence le composant réel** vaut dix instructions qui le décrivent en prose — le serveur
MCP résout ces références à la lecture, ce qui empêche l'agent de choisir un composant au nom
approchant ou de travailler sur une doc périmée.

## Après l'installation

Les Agent Instructions sont stockées **sur le site Webflow**, pas dans ton client : elles suivent
donc d'un outil à l'autre (Claude, Cursor, Codex). Elles peuvent aussi voyager entre sites via les
**Shared Libraries**.

Mets-les à jour quand tu te surprends à répéter la même correction à ton agent : c'est le signe
qu'une règle manque.

Contexte complet et sources : `../webflow-ia-workflow-2026.md`.
