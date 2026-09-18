#!/usr/bin/env python3
"""Batterie de recherche pour l'étude de marché abris / carports / auvents (Corbigny, Nièvre).

Interroge l'Agent API (analyse rédigée + citations) et la Search API (sources brutes)
via les modules du repo, puis écrit un dossier de sources exploitable.

Prérequis : PERPLEXITY_API_KEY exportée, et api.perplexity.ai autorisé par la
politique réseau de l'environnement. Utiliser --dry-run pour vérifier le plan
sans consommer d'appels.

    python scripts/etude_marche_carports.py --dry-run
    python scripts/etude_marche_carports.py --out etude/
    python scripts/etude_marche_carports.py --only marche concurrence
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from perplexity_agent.client import (  # noqa: E402
    PerplexityConfigError,
    PerplexityRateLimitError,
    ask_web,
)
from perplexity_search.client import search_web  # noqa: E402

ZONE = "Corbigny (58800), Nièvre, Bourgogne-Franche-Comté"
PERIMETRE = "abris de jardin, carports autoportés (bois/alu), auvents adossés à la maison"

INSTRUCTIONS = (
    "Tu produis le matériau d'une étude de marché de type conseil en stratégie. "
    "Réponds en français, de façon factuelle et chiffrée. Cite systématiquement "
    "des sources datées et vérifiables (INSEE, SIRENE, service-public.fr, PLU, "
    "sites d'acteurs, catalogues de prix). Quand une donnée locale n'existe pas, "
    "dis-le explicitement et propose la meilleure approximation (département, "
    "région ou national) en précisant la maille. Ne comble jamais un trou par "
    "une estimation présentée comme un fait."
)


@dataclass
class Workstream:
    """Un chantier d'analyse : une question de synthèse + des requêtes de sourcing."""

    key: str
    title: str
    question: str
    searches: list[str] = field(default_factory=list)


WORKSTREAMS: list[Workstream] = [
    Workstream(
        key="marche",
        title="Dimensionnement du marché adressable",
        question=(
            f"Dimensionne le marché des {PERIMETRE} pour un artisan installateur basé à {ZONE}, "
            "sur une zone de chalandise de 45 minutes de route (Corbigny, Clamecy, Vézelay, "
            "Château-Chinon, Prémery, Lormes, Tannay). Donne : nombre de logements et de maisons "
            "individuelles, part de résidences secondaires, nombre de ménages propriétaires, "
            "évolution démographique sur 10 ans, revenu médian des ménages. Puis estime un marché "
            "annuel en euros en explicitant chaque hypothèse (taux d'équipement, taux de "
            "renouvellement, panier moyen) et distingue TAM, SAM et SOM réaliste en année 1."
        ),
        searches=[
            "INSEE dossier complet commune Corbigny 58800 logements résidences secondaires",
            "INSEE Nièvre parc logements maisons individuelles propriétaires statistiques",
            "marché abris de jardin carport France taille chiffre d'affaires 2025 2026",
            "taux équipement abri de jardin carport maisons individuelles France étude",
        ],
    ),
    Workstream(
        key="demande",
        title="Structure et dynamique de la demande",
        question=(
            f"Analyse la demande pour {PERIMETRE} autour de {ZONE}. Segmente entre particuliers "
            "(résidents permanents, propriétaires de résidences secondaires, néo-ruraux) et "
            "professionnels (exploitations agricoles, viticulteurs, artisans, collectivités, "
            "gîtes et hébergements touristiques). Pour chaque segment : besoins, budget typique, "
            "cycle de décision, saisonnalité, volume estimé. Indique les dynamiques locales qui "
            "portent ou freinent la demande : rénovation énergétique, installation de nouveaux "
            "arrivants, tourisme du Morvan et de Vézelay, parc de bâti ancien."
        ),
        searches=[
            "Nièvre attractivité néo-ruraux installation nouveaux habitants 2025",
            "résidences secondaires Morvan Vézelay tourisme statistiques logement",
            "nombre exploitations agricoles Nièvre canton Corbigny recensement agricole",
        ],
    ),
    Workstream(
        key="concurrence",
        title="Paysage concurrentiel",
        question=(
            f"Cartographie la concurrence pour {PERIMETRE} dans un rayon de 45 minutes "
            f"autour de {ZONE}. "
            "Couvre cinq familles d'acteurs : (1) artisans charpentiers, menuisiers et paysagistes "
            "locaux, (2) constructeurs et poseurs régionaux spécialisés, (3) grandes surfaces de "
            "bricolage et jardineries (Leroy Merlin, Brico Dépôt, Gamm Vert, Point Vert) avec "
            "ou sans pose, (4) vendeurs de kits en ligne, (5) acteurs du carport photovoltaïque. "
            "Pour chacun : noms d'entreprises identifiées, positionnement, gamme de prix, "
            "délais, et ce qu'ils ne "
            "couvrent pas. Conclus sur les espaces laissés vacants."
        ),
        searches=[
            "charpentier menuisier Corbigny Clamecy Tannay Lormes carport abri jardin",
            "constructeur carport bois Nièvre 58 entreprise pose devis",
            "abri de jardin pose installateur Nevers Clamecy Avallon",
            "annuaire SIRENE artisans charpente bois Nièvre canton Corbigny",
        ],
    ),
    Workstream(
        key="prix",
        title="Structure de prix et économie unitaire",
        question=(
            f"Établis la grille de prix du marché français pour {PERIMETRE}, en distinguant "
            "entrée, "
            "milieu et haut de gamme. Pour chaque produit donne : prix public fourni-posé, prix du "
            "kit seul, coût matière indicatif, temps de pose, et marge brute typique d'un artisan "
            "poseur. Précise l'écart de prix entre bois (douglas, épicéa, pin traité) et "
            "aluminium, "
            "l'impact du dallage ou des plots béton, et le coût des options (toiture bac acier, "
            "tuiles, gouttières, bardage, portail). Indique la TVA applicable selon les cas "
            "(10 % en rénovation, 20 % en neuf ou hors conditions) et les critères exacts."
        ),
        searches=[
            "prix carport bois posé 2026 France tarif fourni posé mètre carré",
            "prix abri de jardin bois installé tarif artisan 2026",
            "TVA 10 pourcent travaux abri de jardin carport conditions rénovation",
            "prix bois construction douglas épicéa 2026 évolution cours",
        ],
    ),
    Workstream(
        key="reglementation",
        title="Cadre réglementaire et contraintes locales",
        question=(
            f"Détaille les règles d'urbanisme applicables aux {PERIMETRE} à {ZONE} et alentour. "
            "Couvre : les seuils de déclaration préalable et de permis de construire selon "
            "l'emprise au sol, les règles pour les constructions de moins de 5 m², la taxe "
            "d'aménagement (taux communal et départemental dans la Nièvre, valeur forfaitaire "
            "au m² applicable), les contraintes en périmètre de monument historique et en secteur "
            "ABF — Corbigny et Vézelay sont concernés —, les règles du Parc naturel régional du "
            "Morvan, et les obligations du PLU ou du RNU selon les communes. Termine par les "
            "normes "
            "techniques de résistance au vent et à la neige (Eurocode 1, zones de vent et de neige "
            "applicables à la Nièvre) et l'assurance décennale obligatoire pour le poseur."
        ),
        searches=[
            "déclaration préalable permis construire carport abri jardin seuil emprise au sol",
            "taxe aménagement 2026 abri de jardin carport valeur forfaitaire taux Nièvre",
            "architecte bâtiments de France périmètre monument historique Corbigny Vézelay abri",
            "Eurocode zone vent neige Nièvre 58 carte charges construction",
            "PLU Parc naturel régional Morvan règles annexes constructions",
        ],
    ),
    Workstream(
        key="gtm",
        title="Go-to-market et acquisition client",
        question=(
            "Quels canaux d'acquisition fonctionnent pour un artisan poseur d'abris et carports en "
            f"zone rurale française comme {ZONE} ? Compare : plateformes de devis "
            "(Travaux.com, Habitatpresto, Quotatis) avec leur modèle de tarification et le coût "
            "réel d'un lead, référencement Google local et fiche Google Business, réseaux sociaux "
            "locaux, bouche-à-oreille, partenariats (agences immobilières, notaires, paysagistes, "
            "constructeurs de maisons, gîtes), foires et marchés locaux, mise en avant d'un "
            "chantier "
            "vitrine. Pour chacun : coût d'acquisition estimé, délai avant premiers résultats, et "
            "pertinence en faible densité de population. Termine par la séquence de démarrage "
            "recommandée sur les 6 premiers mois."
        ),
        searches=[
            "coût lead plateforme devis travaux Habitatpresto Quotatis tarif artisan",
            "acquisition client artisan bâtiment zone rurale stratégie locale",
            "référencement local Google Business Profile artisan bâtiment",
        ],
    ),
    Workstream(
        key="risques",
        title="Risques, barrières à l'entrée et facteurs clés de succès",
        question=(
            f"Identifie les risques et barrières à l'entrée pour un nouvel entrant sur {PERIMETRE} "
            f"à {ZONE}. Couvre : obligations de qualification et d'inscription (Chambre de "
            "métiers, "
            "statut juridique, assurance décennale et son coût annuel typique), besoin en fonds de "
            "roulement et investissement matériel de départ, volatilité du prix du bois et de "
            "l'acier, saisonnalité de l'activité et trésorerie, dépendance à la météo, difficulté "
            "de recrutement, concurrence des kits grande distribution et du travail non déclaré, "
            "faible densité de population et coût de déplacement. Conclus par les 5 facteurs clés "
            "de succès qui différencient les acteurs qui réussissent."
        ),
        searches=[
            "assurance décennale artisan charpente menuiserie coût annuel tarif",
            "création entreprise artisanale bâtiment obligations qualification chambre métiers",
            "prix bois acier construction volatilité 2026 approvisionnement",
        ],
    ),
]


def run_workstream(ws: Workstream, *, preset: str) -> dict:
    """Exécute un chantier : une synthèse Agent API + les requêtes Search API."""
    record: dict = {"key": ws.key, "title": ws.title, "question": ws.question}

    try:
        answer = ask_web(ws.question, preset=preset, instructions=INSTRUCTIONS)
    except PerplexityRateLimitError as exc:
        record["error"] = f"429 rate limit: {exc}"
        return record
    except PerplexityConfigError as exc:
        record["error"] = f"échec de la requête: {exc}"
        return record

    record["analysis"] = answer.text
    record["citations"] = answer.citations
    record["model"] = answer.model
    record["response_id"] = answer.response_id

    sources: list[dict] = []
    # La Search API accepte jusqu'à 5 requêtes par appel.
    for start in range(0, len(ws.searches), 5):
        batch = ws.searches[start : start + 5]
        try:
            found = search_web(batch, max_results=10, country="FR")
        except (PerplexityRateLimitError, PerplexityConfigError) as exc:
            record.setdefault("search_errors", []).append(str(exc))
            continue
        sources.extend(asdict(item) for item in found.results)
    record["sources"] = sources

    return record


def write_markdown(records: list[dict], path: Path) -> None:
    lines = [
        "# Étude de marché — abris, carports et auvents",
        "",
        f"**Zone** : {ZONE}  ",
        f"**Périmètre produit** : {PERIMETRE}  ",
        f"**Collecte du** : {date.today().isoformat()}",
        "",
        "> Dossier de sources brut produit par `scripts/etude_marche_carports.py`.",
        "> À recouper avant intégration dans la note finale.",
        "",
    ]
    for record in records:
        lines += [f"## {record['title']}", ""]
        if "error" in record:
            lines += [f"**Échec de la collecte** : {record['error']}", ""]
            continue
        lines += [record["analysis"], ""]
        if record.get("citations"):
            lines += ["### Citations", ""]
            lines += [f"- {url}" for url in record["citations"]]
            lines += [""]
        if record.get("sources"):
            lines += ["### Sources complémentaires", ""]
            for source in record["sources"]:
                lines.append(f"- [{source['title']}]({source['url']})")
            lines += [""]
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default="etude", help="Dossier de sortie (défaut: etude).")
    parser.add_argument(
        "--only", nargs="*", default=None, help="Ne lancer que ces chantiers (par clé)."
    )
    parser.add_argument("--preset", default="high", help="Preset Agent API (défaut: high).")
    parser.add_argument(
        "--dry-run", action="store_true", help="Afficher le plan sans appeler l'API."
    )
    args = parser.parse_args(argv)

    selected = WORKSTREAMS
    if args.only:
        keys = set(args.only)
        unknown = keys - {ws.key for ws in WORKSTREAMS}
        if unknown:
            print(f"error: chantier(s) inconnu(s): {', '.join(sorted(unknown))}", file=sys.stderr)
            return 2
        selected = [ws for ws in WORKSTREAMS if ws.key in keys]

    if args.dry_run:
        print(f"Zone      : {ZONE}")
        print(f"Périmètre : {PERIMETRE}")
        print(f"Preset    : {args.preset}\n")
        total_searches = 0
        for ws in selected:
            print(f"[{ws.key}] {ws.title}")
            print(f"  1 question Agent API ({len(ws.question)} caractères)")
            for query in ws.searches:
                print(f"  search: {query}")
            total_searches += len(ws.searches)
            print()
        print(
            f"Total : {len(selected)} appels Agent API, "
            f"{total_searches} requêtes Search API réparties en "
            f"{sum((len(ws.searches) + 4) // 5 for ws in selected)} appels."
        )
        return 0

    if not os.environ.get("PERPLEXITY_API_KEY"):
        print(
            "PERPLEXITY_API_KEY n'est pas définie. Créer une clé sur "
            "https://console.perplexity.ai puis l'exporter, ou la configurer sur "
            "l'environnement cloud. Voir docs/etude-marche-carports.md.",
            file=sys.stderr,
        )
        return 1

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for ws in selected:
        print(f"→ {ws.title} …", flush=True)
        record = run_workstream(ws, preset=args.preset)
        if "error" in record:
            print(f"  échec : {record['error']}", file=sys.stderr)
        else:
            print(f"  ok : {len(record['citations'])} citations, {len(record['sources'])} sources")
        records.append(record)

    (out_dir / "sources.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_markdown(records, out_dir / "dossier-sources.md")
    print(f"\nÉcrit dans {out_dir}/ : sources.json, dossier-sources.md")
    return 0 if all("error" not in r for r in records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
