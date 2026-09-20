# Kit de démarrage — Agent Instructions Webflow

Fichiers prêts à installer sur un site Webflow pour qu'un agent IA (Claude, Cursor, Codex…)
construise des pages **natives** et **propres**.

## Installation

**Option A — interface Webflow.** Site → section *Instructions* → créer une Rule ou un Skill →
coller le contenu du fichier correspondant.

**Option B — via MCP.** Demandez à votre agent :

> Crée ces agent instructions sur le site `<site_id>` avec
> `data_agent_instructions_tool > create_instruction`, en respectant les chemins indiqués.

| Fichier local | `kind` | `path` Webflow |
|---|---|---|
| `rules/native-first.md` | `rule` | `rules/native-first.md` |
| `rules/design-system.md` | `rule` | `rules/design-system.md` |
| `rules/accessibility-seo.md` | `rule` | `rules/accessibility-seo.md` |
| `rules/safety.md` | `rule` | `rules/safety.md` |
| `build-native-section/SKILL.md` | `skill` | `build-native-section/SKILL.md` |

## Avant de les installer

Lancez d'abord `generate_instruction` pour `design-system`, `brand-guidelines` et
`asset-guidelines` : Webflow produit des brouillons à partir de votre site réel. Relisez-les,
corrigez-les, **puis** ajoutez ces règles-ci par-dessus.

## À personnaliser

Les passages entre `<…>` sont des emplacements à remplir avec vos vraies ressources. Une
instruction qui **référence le composant réel** vaut dix instructions qui le décrivent en prose.
