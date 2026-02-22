# IN France — Simulateur d'impact territorial

Outil de simulation de l'impact économique territorial d'une entreprise française.  
Déployé sur Vercel · API sur Supabase Edge Functions.

🔗 **Production** : [simulateur.in-france.fr](https://simulateur.in-france.fr)  
📖 **Site vitrine** : [in-france.fr](https://www.in-france.fr)

---

## Structure du projet

```
/
├── index.html              # Simulateur principal
├── methodologie.html       # Page de documentation scientifique
├── vercel.json             # Config Vercel (rewrites, headers)
├── README.md
│
└── api/                    # Edge Function Supabase (déployée séparément)
    └── impact_function.ts  # supabase/functions/impact/index.ts
    └── supabase_tables.sql # Tables simulations + leads
```

## Modèle économique — 3 couches

| Couche | Méthode | Source |
|--------|---------|--------|
| Effets directs | Ratios sectoriels | BdF FIBEN 2024 |
| Effets indirects | Matrice Leontief | OCDE ICIO 2023 |
| Effets induits | Propensité à consommer | Eurostat HBS 2020 |

---

## Déploiement

### Frontend — Vercel

```bash
# 1. Cloner le repo
git clone https://github.com/your-org/in-france-simulateur.git
cd in-france-simulateur

# 2. Installer Vercel CLI
npm i -g vercel

# 3. Déployer
vercel --prod
```

Ou via l'interface : importer le repo sur [vercel.com/new](https://vercel.com/new), aucune config build nécessaire (site statique).

**Domaine custom** : Dans Vercel > Settings > Domains, ajouter `simulateur.in-france.fr` et configurer le CNAME chez votre registrar.

### API — Supabase Edge Functions

```bash
# 1. Installer Supabase CLI
npm i -g supabase

# 2. Lier au projet
supabase login
supabase link --project-ref obdxlomdseakyefovwvt

# 3. Déployer la fonction
mkdir -p supabase/functions/impact
cp api/impact_function.ts supabase/functions/impact/index.ts
supabase functions deploy impact --no-verify-jwt
```

### Base de données

Exécuter `api/supabase_tables.sql` dans l'éditeur SQL Supabase :
[https://supabase.com/dashboard/project/obdxlomdseakyefovwvt/sql](https://supabase.com/dashboard/project/obdxlomdseakyefovwvt/sql)

---

## Variables d'environnement

Aucune variable d'environnement côté frontend (site statique).

La Edge Function utilise les variables injectées automatiquement par Supabase :
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

---

## Sources de données

- **BdF FIBEN** — [https://www.banque-france.fr/fr/statistiques/entreprises](https://www.banque-france.fr/fr/statistiques/entreprises)
- **OCDE ICIO** — [https://www.oecd.org/sti/ind/inter-country-input-output.htm](https://www.oecd.org/sti/ind/inter-country-input-output.htm)
- **Eurostat HBS** — [https://ec.europa.eu/eurostat/web/household-budget-surveys](https://ec.europa.eu/eurostat/web/household-budget-surveys)
- **INSEE ESANE** — [https://www.insee.fr/fr/statistiques/serie/001654101](https://www.insee.fr/fr/statistiques/serie/001654101)
- **API Recherche Entreprises** — [https://recherche-entreprises.api.gouv.fr](https://recherche-entreprises.api.gouv.fr)
