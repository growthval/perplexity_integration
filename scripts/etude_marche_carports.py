#!/usr/bin/env python3
"""Collecte pour l'étude de marché carports bois — Corbigny (Nièvre).

Pose une série de questions COURTES et ATOMIQUES à l'Agent API Perplexity :
une question = un fait. Les réponses sont recombinées à l'analyse.

Les questions longues déclenchent des 502 côté Perplexity ; le découpage
en questions courtes est délibéré, pas cosmétique.

    python scripts/etude_marche_carports.py --dry-run
    python scripts/etude_marche_carports.py
    python scripts/etude_marche_carports.py --only demographie prix
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from perplexity_agent.client import (  # noqa: E402
    PerplexityConfigError,
    PerplexityRateLimitError,
    ask_web,
)

ZONE = "Corbigny (58800), Nièvre — zone de chalandise 45 minutes de route"
PROJET = "carports bois autoportés, auvents adossés, abris pro et agricoles"

INSTRUCTIONS = (
    "Réponds en français, brièvement et factuellement. Donne des chiffres "
    "précis avec leur année et leur source (INSEE, SIRENE, recensement "
    "agricole, service-public.fr, sites d'entreprises, catalogues). Privilégie "
    "les données 2024, 2025 et 2026 ; si la donnée la plus récente est plus "
    "ancienne, dis-le. Si une donnée n'existe pas à la maille demandée, "
    "indique-le explicitement et donne la maille supérieure disponible. "
    "N'invente aucun chiffre. Pas d'introduction ni de conclusion : les faits."
)

MAX_RETRIES = 3


@dataclass
class Question:
    key: str
    block: str
    text: str


QUESTIONS: list[Question] = [
    # --- Démographie et zone de chalandise -------------------------------
    Question("pop_ccc", "demographie",
             "Combien d'habitants compte la communauté de communes "
             "Tannay-Brinon-Corbigny dans la Nièvre selon l'INSEE ? "
             "Donne le chiffre le plus récent et son année."),
    Question("pop_communes", "demographie",
             "Quelle est la population INSEE de ces communes de la Nièvre : "
             "Corbigny, Clamecy, Château-Chinon, Prémery, Lormes, Tannay, "
             "Varzy, Moulins-Engilbert ? Précise l'année."),
    Question("pop_evolution", "demographie",
             "Comment a évolué la population du département de la Nièvre "
             "entre 2015 et 2025 selon l'INSEE ? Donne les chiffres et le "
             "taux d'évolution annuel moyen."),
    Question("revenus", "demographie",
             "Quel est le revenu médian disponible par ménage dans la Nièvre "
             "et à Corbigny selon l'INSEE ? Compare à la moyenne française."),

    # --- Logement et propriété -------------------------------------------
    Question("logements_nievre", "logement",
             "Combien de logements compte le département de la Nièvre et "
             "quelle part sont des maisons individuelles ? Source INSEE, "
             "année la plus récente."),
    Question("proprietaires", "logement",
             "Quelle part des ménages de la Nièvre sont propriétaires de leur "
             "résidence principale selon l'INSEE ? Compare à la moyenne "
             "nationale."),
    Question("residences_secondaires", "logement",
             "Quelle part des logements de la Nièvre sont des résidences "
             "secondaires selon l'INSEE ? Compare à la moyenne française."),
    Question("logements_corbigny", "logement",
             "Combien de logements compte la commune de Corbigny (58800) et "
             "comment se répartissent-ils entre résidences principales, "
             "secondaires et logements vacants ? Source INSEE."),

    # --- Motorisation (décisif pour un carport) --------------------------
    Question("motorisation_nievre", "motorisation",
             "Quel est le taux d'équipement automobile des ménages dans la "
             "Nièvre selon l'INSEE ? Donne la part de ménages possédant 0, 1, "
             "2 voitures ou plus."),
    Question("motorisation_rural", "motorisation",
             "Le taux de motorisation des ménages est-il plus élevé en zone "
             "rurale qu'en zone urbaine en France ? Donne des chiffres INSEE "
             "récents."),
    Question("parc_auto", "motorisation",
             "Combien de voitures particulières sont immatriculées dans le "
             "département de la Nièvre ? Donne le chiffre le plus récent."),

    # --- Prix pratiqués ---------------------------------------------------
    Question("prix_carport_bois_1v", "prix",
             "Quel est le prix d'un carport en bois pour une voiture, fourni "
             "et posé, en France en 2025-2026 ? Donne une fourchette."),
    Question("prix_carport_bois_2v", "prix",
             "Quel est le prix d'un carport en bois pour deux voitures, "
             "fourni et posé, en France en 2025-2026 ?"),
    Question("prix_carport_alu", "prix",
             "Quel est l'écart de prix entre un carport en aluminium et un "
             "carport en bois en France en 2025-2026 ?"),
    Question("prix_auvent", "prix",
             "Quel est le prix d'un auvent ou carport adossé à la maison, en "
             "bois, fourni et posé, en France en 2025-2026 ?"),
    Question("prix_abri_agricole", "prix",
             "Quel est le prix d'un hangar ou abri agricole en bois pour une "
             "exploitation en France en 2025-2026 ?"),
    Question("prix_kit", "prix",
             "Quel est le prix d'un carport en bois en kit chez Leroy Merlin, "
             "Brico Dépôt ou sur internet en 2025-2026 ?"),
    Question("tarif_artisan", "prix",
             "Quel est le tarif horaire moyen facturé par un charpentier ou "
             "un menuisier en France en 2025-2026 ?"),
    Question("prix_bois", "prix",
             "Comment a évolué le prix du bois de construction (douglas, "
             "épicéa, pin) en France entre 2024 et 2026 ?"),

    # --- Concurrence ------------------------------------------------------
    Question("concurrents_nievre", "concurrence",
             "Quelles entreprises fabriquent ou posent des carports en bois "
             "dans le département de la Nièvre (58) ? Donne des noms "
             "d'entreprises et leur ville."),
    Question("concurrents_local", "concurrence",
             "Quels charpentiers, menuisiers ou constructeurs bois sont "
             "installés à Corbigny, Clamecy, Tannay, Lormes ou "
             "Château-Chinon dans la Nièvre ?"),
    Question("densite_artisans", "concurrence",
             "Combien d'entreprises de charpente et de menuiserie bois sont "
             "enregistrées dans le département de la Nièvre ? Source SIRENE "
             "ou Chambre de métiers."),
    Question("gsb_pose", "concurrence",
             "Les grandes surfaces de bricolage comme Leroy Merlin ou Brico "
             "Dépôt proposent-elles un service de pose de carport en France, "
             "et à quel tarif ?"),

    # --- Marché France (contexte bref) ------------------------------------
    Question("marche_france", "marche_france",
             "Quelle est la taille du marché du carport et de l'abri de "
             "voiture en France ? Donne un chiffre d'affaires et sa source."),
    Question("tendance_carport", "marche_france",
             "Le marché du carport est-il en croissance en France en "
             "2024-2026 ? Quels facteurs le portent ou le freinent ?"),
    Question("trends", "marche_france",
             "Comment ont évolué les recherches Google pour « carport » et "
             "« carport bois » en France depuis 2022 ? Y a-t-il une "
             "saisonnalité marquée dans l'année ?"),

    # --- Demande professionnelle et agricole ------------------------------
    Question("agriculture", "demande_pro",
             "Combien d'exploitations agricoles compte la Nièvre et comment "
             "ce nombre évolue-t-il ? Source recensement agricole."),
    Question("immobilier", "demande_pro",
             "Comment évolue le marché immobilier dans la Nièvre en "
             "2024-2026 : nombre de transactions, prix moyen d'une maison, "
             "attractivité du département ?"),

    # --- Réglementation (pratique, bref) ----------------------------------
    Question("urbanisme", "reglementation",
             "Quelles autorisations d'urbanisme faut-il pour construire un "
             "carport en France : seuils de déclaration préalable et de "
             "permis de construire selon l'emprise au sol ?"),
    Question("taxe", "reglementation",
             "Un carport est-il soumis à la taxe d'aménagement en France en "
             "2026, et à quel montant par mètre carré ?"),
]

BLOCK_TITLES = {
    "demographie": "Démographie et zone de chalandise",
    "logement": "Logement et propriété",
    "motorisation": "Motorisation des ménages",
    "prix": "Prix pratiqués",
    "concurrence": "Concurrence",
    "marche_france": "Marché France (contexte)",
    "demande_pro": "Demande professionnelle et agricole",
    "reglementation": "Réglementation",
}


def ask_with_retry(question: Question, *, preset: str) -> dict:
    """Une question, avec reprise sur 429 et sur les 5xx transitoires."""
    record: dict = {"key": question.key, "block": question.block, "question": question.text}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            answer = ask_web(question.text, preset=preset, instructions=INSTRUCTIONS)
        except PerplexityRateLimitError as exc:
            wait = exc.retry_after_seconds or 2**attempt
            if attempt == MAX_RETRIES:
                record["error"] = f"429 après {MAX_RETRIES} tentatives: {exc}"
                return record
            time.sleep(wait)
            continue
        except PerplexityConfigError as exc:
            transient = any(code in str(exc) for code in ("500", "502", "503", "504"))
            if transient and attempt < MAX_RETRIES:
                time.sleep(2**attempt)
                continue
            record["error"] = str(exc)
            return record

        record["answer"] = answer.text
        # Perplexity ne renseigne pas les annotations de message : les sources
        # arrivent dans search_results, avec des marqueurs [web:N] dans le texte.
        record["sources"] = answer.search_results or [
            {"title": "", "url": url, "snippet": ""} for url in answer.citations
        ]
        record["model"] = answer.model
        record["attempts"] = attempt
        return record

    record["error"] = "échec après retries"
    return record


def write_markdown(records: list[dict], path: Path) -> None:
    lines = [
        "# Collecte — étude de marché carports bois",
        "",
        f"**Zone** : {ZONE}  ",
        f"**Périmètre** : {PROJET}  ",
        f"**Collecte du** : {date.today().isoformat()}",
        "",
        "> Matériau brut produit par `scripts/etude_marche_carports.py`.",
        "",
    ]
    for block, title in BLOCK_TITLES.items():
        block_records = [r for r in records if r["block"] == block]
        if not block_records:
            continue
        lines += [f"## {title}", ""]
        for record in block_records:
            lines += [f"### {record['question']}", ""]
            if "error" in record:
                lines += [f"*Échec : {record['error']}*", ""]
                continue
            lines += [record["answer"], ""]
            if record.get("sources"):
                urls = []
                for i, source in enumerate(record["sources"][:12], start=1):
                    label = source.get("title") or source["url"]
                    urls.append(f"{i}. [{label}]({source['url']})")
                lines += ["<details><summary>Sources</summary>", ""] + urls + ["", "</details>", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default="etude", help="Dossier de sortie.")
    parser.add_argument("--only", nargs="*", default=None, help="Limiter à ces blocs.")
    parser.add_argument("--preset", default="medium", help="Preset Agent API.")
    parser.add_argument("--workers", type=int, default=4, help="Requêtes en parallèle.")
    parser.add_argument("--dry-run", action="store_true", help="Afficher le plan.")
    args = parser.parse_args(argv)

    selected = QUESTIONS
    if args.only:
        blocks = set(args.only)
        unknown = blocks - set(BLOCK_TITLES)
        if unknown:
            print(f"error: bloc(s) inconnu(s): {', '.join(sorted(unknown))}", file=sys.stderr)
            return 2
        selected = [q for q in QUESTIONS if q.block in blocks]

    if args.dry_run:
        for block, title in BLOCK_TITLES.items():
            questions = [q for q in selected if q.block == block]
            if not questions:
                continue
            print(f"\n[{block}] {title}")
            for q in questions:
                print(f"  - {q.text[:88]}")
        print(f"\nTotal : {len(selected)} questions courtes, {args.workers} en parallèle.")
        return 0

    if not os.environ.get("PERPLEXITY_API_KEY"):
        print("PERPLEXITY_API_KEY absente. Voir docs/etude-marche-carports.md.", file=sys.stderr)
        return 1

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"{len(selected)} questions, {args.workers} en parallèle…\n", flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        records = list(pool.map(lambda q: ask_with_retry(q, preset=args.preset), selected))

    ok = 0
    for record in records:
        if "error" in record:
            print(f"  ✗ {record['key']}: {record['error'][:80]}", file=sys.stderr)
        else:
            ok += 1
            print(f"  ✓ {record['key']}: {len(record['sources'])} sources")

    (out_dir / "collecte.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_markdown(records, out_dir / "collecte.md")
    print(f"\n{ok}/{len(records)} réussies → {out_dir}/collecte.json, {out_dir}/collecte.md")
    return 0 if ok == len(records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
