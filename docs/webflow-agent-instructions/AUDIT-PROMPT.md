# Prompt d'audit et de remise en ordre du projet

> À coller dans la session Claude Code **du projet Webflow Dev**, avant de démarrer une tâche de
> construction de page. Il produit un **rapport**, puis n'agit qu'après validation.

---

Avant de démarrer une nouvelle tâche de construction de page, je veux savoir si le projet est en
état. Tu vas l'auditer, me remettre un rapport, et **n'exécuter aucune réorganisation avant mon
accord explicite**.

## Règles valables du début à la fin

- **Aucune suppression, aucun déplacement, aucune réécriture pendant les phases A à F.** Tu lis,
  tu classes, tu proposes. Rien d'autre.
- **Un fichier dont tu ne comprends pas l'usage n'est pas un fichier mort.** Il va dans
  « à clarifier », et tu me poses la question. Le doute ne tranche jamais vers la suppression.
- **Ne sors jamais du dépôt**, à une exception près : tu peux **lire** `E:\structure_maker`
  (Phase E). Tu n'y écris rien. Et toujours pas de `~/.claude/` ni de fichiers hors du projet.
- **Ne touche pas à `.agents/skills/` ni `.claude/skills/`.** Ils sont gérés par
  `webflow-skills-lock.json` et restaurés par la CLI. Tu peux les analyser, pas les modifier.
- Si une action te paraît évidente mais destructive, elle passe quand même par mon accord.

## Phase A — Sécurité (en premier, toujours)

Cherche dans **tout** le dépôt, y compris l'historique git si nécessaire :

1. Secrets et jetons : `.env`, `.env.*`, clés d'API, tokens Webflow, identifiants SMTP,
   webhooks n8n, clés OVH. Fouille en particulier `migration-audit/ovh-backup/`,
   `tasks/b2b-i18n/*.js`, `tasks/phase*.json`, `tasks/sticky-cta-and-contact-dropdown/*.js`,
   `limo-car-components/n8n-workflow-spec.md`.
2. Données personnelles ou commerciales sensibles : `domains_export_2026-05-10.csv`,
   `fs-failed-301-uploads.csv`, `TARIFS Limo Cars 2023+ règles 07_2024.xlsx`,
   `tasks/reponse-client-codes-aeroport.md`, `email-notification-b2b.html`.
   Ces fichiers sont-ils versionnés ? Devraient-ils l'être ?
3. Un secret trouvé : **ne le recopie pas** dans ton rapport. Donne le chemin, la ligne, la nature
   — jamais la valeur. Et dis si le fichier est suivi par git.

**Un secret versionné est un blocage.** Signale-le en tête de rapport, avant tout le reste.

## Phase B — Inventaire et classement

Passe en revue **chaque fichier et dossier** du dépôt et attribue-lui exactement un verdict :

| Verdict | Sens |
|---|---|
| **ACTIF** | Sert aujourd'hui, ou décrit un dispositif en production |
| **ARCHIVE** | Trace d'un travail terminé, à conserver mais à ranger et dater |
| **MORT** | Sortie intermédiaire, doublon, artefact de build — ne sert plus à rien |
| **À CLARIFIER** | Tu ne peux pas trancher sans moi |

Points d'attention que j'ai repérés — ils orientent, ils ne remplacent pas ton propre examen :

- **`tasks/` est devenu un fourre-tout** : une vingtaine de fichiers à plat mélangeant plans,
  scripts Python, dumps JSON, widgets JS, PDF. Propose une arborescence.
- **`tasks/.pdf-build/node_modules/`** : des dépendances dans le dépôt. Vérifie si c'est suivi
  par git.
- **Artefacts versionnés par numéro** : `style-v1.4.js`, `widget-v1.4.js`, `lcB2bFormJS-1.3.0.js`,
  `lcB2bMailJS-1.1.0.js`, `lcB2bUiJS-1.2.0.js`, `freeform-footer-b2b-v2.js` et
  `freeform-footer-b2b-EN-PROD-2026-09-0*.js`. Pour chacun : **quelle version tourne réellement
  sur le site ?** Croise avec `data_scripts_tool > get_site_scripts` / `get_page_scripts` et le
  custom code libre. Une version qui ne tourne nulle part et qui n'est pas la plus récente est
  candidate à l'archivage, pas à la suppression.
- **`migration-audit/`** : projet TypeScript autonome (WordPress → Webflow). La migration est-elle
  terminée ? `output/`, `i18n/`, `ovh-backup/` sont-ils des sorties régénérables ?
- **`limo-car-components/`** : deux fichiers seulement. Dossier vivant ou amorce abandonnée ?
- **`tasks/chunks/chunk1-3.json`**, **`adsback-source-tree.json` et `.txt`** (même contenu sous
  deux formats ?), **`phase2_clear.json`**, **`phase4_*.json`** : sorties intermédiaires ?
- **`tracking-ads-agency.md` et `.pdf`** : le PDF est-il régénérable depuis le `.md` via
  `.pdf-build` ? Si oui, il n'a pas à être versionné.
- Les trois documents déjà marqués « archive » en en-tête : vérifie que l'en-tête est bien en
  première ligne et que la date correspond au contenu.

## Phase C — Cohérence de la configuration agent

C'est le point le plus important pour la suite, parce que le site porte désormais ses propres
Agent Instructions.

1. Liste les instructions du site : `data_agent_instructions_tool > search_instructions`.
2. Relis `.claude/rules/webflow-cms.md`, `webflow-custom-code.md`, `webflow-design.md`,
   `webflow-publishing.md`, `.claude/agents/cms-specialist.md`, `webflow-auditor.md`, et `CLAUDE.md`.
3. Pour chaque règle locale, tranche : **duplique** une instruction du site, la **contredit**, ou
   **complète** utilement ?
   - Duplication → proposer de supprimer la version locale et de renvoyer vers l'instruction du
     site, qui est portable entre Claude, Cursor et Codex.
   - Contradiction → **la signaler en priorité**. Deux sources de vérité qui divergent, c'est la
     garantie d'un résultat incohérent à la prochaine construction de page.
   - Complément → garder, et dire pourquoi.
4. `.claude/hooks/bash-firewall.ps1`, `pre-publish-check.ps1`, `webflow-validate.ps1` : que
   font-ils exactement, se déclenchent-ils encore, et risquent-ils de bloquer ou de fausser une
   tâche de construction de page ? Sont-ils compatibles avec la façon dont le projet tourne
   aujourd'hui ?
5. `.claude/agents/` : ces deux sous-agents sont-ils encore alignés sur les skills installés et
   sur les instructions du site, ou répètent-ils des consignes désormais portées ailleurs ?
6. `.agents/skills/` et `.claude/skills/` contiennent le même jeu de 32 skills. Explique le
   rapport entre les deux (liens symboliques ?), confirme que le lockfile suffit à tout
   restaurer, et vérifie que `webflow-skills-lock.json` est bien suivi par git.

## Phase D — Hygiène git

- `.gitignore` racine et `migration-audit/.gitignore` : que couvrent-ils, que laissent-ils passer ?
- Y a-t-il des fichiers suivis qui ne devraient pas l'être (dépendances, sorties de build,
  binaires volumineux) ? Donne les tailles.
- Le dépôt contient-il des fichiers de plus de 1 Mo ? Lesquels, et sont-ils justifiés ?
- État courant : branche, fichiers modifiés non commités, commits non poussés.

## Phase E — L'arborescence cible passe par `structure_maker`

Il y a sur **`E:\structure_maker`** un projet à moi qui sert à construire des infrastructures de
projet propres. **L'arborescence cible ne s'invente pas : elle vient de lui.**

1. Tu as le droit de **lire** ce dossier. Tu n'y écris rien, tu n'y modifies rien.
2. **Comprends-le avant de t'en servir.** Lis son `README`, son point d'entrée, sa configuration,
   et s'il s'exécute, son `--help`. Puis dis-moi en trois lignes : ce qu'il fait, comment on
   l'invoque, ce qu'il produit. **Ne présume ni de son interface, ni de ses conventions, ni de son
   format de configuration** — découvre-les.
3. Ensuite, selon sa nature :
   - **Il génère une arborescence** → fais-le tourner en simulation / `--dry-run` s'il en a un,
     ou sur une copie. Jamais directement sur le projet à ce stade.
   - **Il définit des conventions** (gabarit, schéma, documentation) → dérive l'arborescence cible
     de ces conventions.
   - **Il valide une structure existante** → passe le projet dedans et rapporte ses constats tels
     quels, sans les réinterpréter.
4. **Conflits : signale, ne tranche pas.** Certains chemins sont imposés par des outils externes
   et ne sont pas négociables — `.claude/`, `.agents/`, `webflow-skills-lock.json`, `.vscode/`,
   et tout chemin cité dans `CLAUDE.md` ou dans un hook. Si `structure_maker` veut les déplacer,
   dis-le-moi, n'obéis pas.
5. S'il est inaccessible, ou s'il ne s'applique pas à ce type de projet, **dis-le et continue** :
   propose alors une arborescence cible classique. L'audit ne s'arrête pas pour autant.

## Phase F — Le rapport

Écris-le dans **`project-audit.md`** à la racine, et donne-m'en la synthèse en réponse.
Structure attendue :

1. **Bloquants** — secrets versionnés, contradictions de règles. En tête, rien avant.
2. **Tableau d'inventaire** — une ligne par fichier ou dossier : chemin, verdict, justification
   en une phrase, action proposée.
3. **Arborescence cible** — celle dérivée de `structure_maker` (Phase E), en regard de
   l'actuelle. Dis ce que tu as compris de l'outil, et signale explicitement chaque écart que tu
   as dû arbitrer entre ses conventions et les contraintes du projet.
4. **Plan d'exécution ordonné** — par groupes, du plus sûr au plus risqué, avec pour chaque groupe
   ce qui est réversible et ce qui ne l'est pas.
5. **À clarifier** — tes questions, formulées pour que je puisse répondre par oui/non ou par un
   choix.
6. **Verdict de démarrage** — le projet est-il prêt pour une tâche de construction de page ? Si
   non, qu'est-ce qui bloque exactement ?

**Arrête-toi là et attends ma réponse.**

## Phase G — Exécution, après mon accord seulement

Quand j'aurai validé, groupe par groupe :

- Travaille sur une branche dédiée, en partant d'un état propre.
- Applique l'arborescence cible de la Phase E. Si `structure_maker` sait faire les déplacements
  lui-même, vérifie d'abord qu'il est **conscient de git** : sinon, laisse-le produire la cible et
  fais les déplacements toi-même avec `git mv`, sans quoi l'historique se perd. Après son passage,
  compare ce qu'il a réellement fait à ce qu'il avait annoncé.
- **`git mv` pour tout déplacement** — jamais supprimer puis recréer, l'historique se perd.
- **Rien ne se supprime au premier passage.** Ce qui est MORT part dans `_trash/` à la racine,
  avec `_trash/README.md` listant l'origine de chaque fichier et la date. Suppression réelle
  dans un second temps, une fois que le projet aura tourné quelques jours sans manquer de rien.
- Un commit par groupe, avec un message qui dit ce qui bouge et pourquoi.
- Après chaque groupe : vérifie que rien n'est cassé — les scripts qui tournent encore tournent,
  `webflow skills install --project` restaure toujours, les chemins cités dans `CLAUDE.md` existent.
- Mets `CLAUDE.md` à jour **en dernier**, pour refléter la nouvelle arborescence.

## Phase H — Feu vert pour construire

Une fois la remise en ordre faite, confirme point par point :

1. Les 6 instructions du site répondent et leurs références se résolvent.
2. `CLAUDE.md` ne contredit aucune d'elles.
3. Les hooks ne bloquent pas une tâche de construction.
4. La CLI Webflow démarre (`npx webflow --version`).
5. Le MCP Webflow est connecté et autorisé sur le bon workspace.
6. L'arbre de travail est propre et poussé.

Puis propose-moi un test à blanc : décris — **sans rien créer** — comment tu construirais une
nouvelle section sur la page de mon choix, en appliquant les instructions du site.
