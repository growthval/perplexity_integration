#!/usr/bin/env python3
"""Regenerate BUNDLE.md from the instruction files. Run after editing any of them."""
from __future__ import annotations

import pathlib

HERE = pathlib.Path(__file__).parent

FILES = [
    ("rules/native-first.md", "rule"),
    ("rules/design-system.md", "rule"),
    ("rules/accessibility-seo.md", "rule"),
    ("rules/safety.md", "rule"),
    ("build-native-section/SKILL.md", "skill"),
]

HEADER = """# BUNDLE — contenu des Agent Instructions à installer

Ce fichier regroupe les 5 instructions à créer sur le site Webflow, dans un seul document, pour
qu'un agent puisse tout lire d'un coup. Il est **généré** depuis les fichiers du dossier : ne pas
l'éditer directement, éditer les fichiers sources puis relancer `python3 make-bundle.py`.

Chaque section ci-dessous indique le `kind` et le `path` à passer à
`data_agent_instructions_tool > create_instruction`. Le corps de l'instruction est le bloc
markdown qui suit, **sans** la ligne de titre `## Instruction N`.

Les emplacements entre `<…>` sont à remplir avec les ressources réelles du site, découvertes par
l'inventaire (Phase 1 du prompt d'installation). Une instruction laissée générique ne change rien
au comportement de l'agent.

---
"""


def build() -> str:
    parts = [HEADER]
    for i, (path, kind) in enumerate(FILES, 1):
        body = (HERE / path).read_text(encoding="utf-8").rstrip()
        parts += [
            f"## Instruction {i} — `{path}`\n",
            f"- `kind`: `{kind}`\n- `path`: `{path}`\n",
            "<!-- début du corps de l'instruction -->\n",
            body + "\n",
            "<!-- fin du corps de l'instruction -->\n",
            "---\n",
        ]
    return "\n".join(parts)


if __name__ == "__main__":
    target = HERE / "BUNDLE.md"
    target.write_text(build(), encoding="utf-8")
    print(f"wrote {target} ({len(target.read_text(encoding='utf-8'))} chars)")
