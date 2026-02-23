// supabase/functions/impact/index.ts
// Edge Function - Calcul d'impact territorial IN France
// Runtime: Deno (Supabase Edge Functions)
//
// POST /functions/v1/impact
// Body: { "siren": "123456789" }
//    ou { "naf": "C", "ca": 10000000 }

import { createClient } from "npm:@supabase/supabase-js@2";

// ─── Types ────────────────────────────────────────────────────────────────────

interface RatioRow {
  code_naf: string;
  libelle: string;
  taux_valeur_ajoutee: number | null;
  taux_excedent_brut_global: number | null;
  part_personnel: number | null;
  part_etat: number | null;
  part_preteurs: number | null;
  part_associes: number | null;
  part_entreprise: number | null;
}

interface LeontiefRow {
  section_source: string;
  section_cible: string;
  coefficient: number;
}

interface PmcRow {
  section_naf: string;
  pmc: number;
}

interface SireneEtablissement {
  siret: string;
  denominationUniteLegale?: string;
  activitePrincipaleUniteLegale?: string; // code NAF ex: "41.20B"
  trancheEffectifsUniteLegale?: string;
}

// ─── Productivite apparente du travail par section NAF (euros/emploi ETP) ────
// Source: INSEE ESANE 2022

const PRODUCTIVITE: Record<string, number> = {
  A: 48_000,  B: 95_000,  C: 72_000,  D: 210_000,
  E: 85_000,  F: 55_000,  G: 58_000,  H: 62_000,
  I: 38_000,  J: 105_000, K: 180_000, L: 95_000,
  M: 88_000,  N: 45_000,  O: 65_000,  P: 52_000,
  Q: 50_000,  R: 48_000,  S: 42_000,
};

// CA median par tranche d'effectifs (estimation pour estimation CA depuis SIRENE)
const CA_PAR_TRANCHE: Record<string, number> = {
  "00": 120_000,    // 0 salarie
  "01": 300_000,    // 1-2
  "02": 600_000,    // 3-5
  "03": 1_200_000,  // 6-9
  "11": 2_500_000,  // 10-19
  "12": 6_000_000,  // 20-49
  "21": 15_000_000, // 50-99
  "22": 40_000_000, // 100-199
  "31": 80_000_000, // 200-249
  "32": 150_000_000,// 250-499
  "41": 350_000_000,// 500-999
  "42": 750_000_000,// 1000-1999
  "51": 2_000_000_000, // 2000-4999
  "52": 5_000_000_000, // 5000+
  "53": 10_000_000_000,
};

// ─── Helpers ──────────────────────────────────────────────────────────────────

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
  };
}

function jsonResponse(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...corsHeaders(), "Content-Type": "application/json" },
  });
}

function errorResponse(message: string, status = 400) {
  return jsonResponse({ error: message }, status);
}

// Convertit un code NAF complet (ex: "41.20B") en section NAF (ex: "F")
function nafCodeToSection(nafCode: string): string | null {
  if (!nafCode) return null;
  const clean = nafCode.replace(".", "").toUpperCase();
  const num = parseInt(clean.slice(0, 2), 10);
  if (isNaN(num)) return null;

  if (num <= 3)              return "A";
  if (num <= 9)              return "B";
  if (num <= 33)             return "C";
  if (num === 35)            return "D";
  if (num <= 39)             return "E";
  if (num <= 43)             return "F";
  if (num <= 47)             return "G";
  if (num <= 53)             return "H";
  if (num <= 56)             return "I";
  if (num <= 63)             return "J";
  if (num <= 66)             return "K";
  if (num === 68)            return "L";
  if (num <= 75)             return "M";
  if (num <= 82)             return "N";
  if (num === 84)            return "O";
  if (num === 85)            return "P";
  if (num <= 88)             return "Q";
  if (num <= 93)             return "R";
  if (num <= 96)             return "S";
  return null;
}

// ─── Lookup SIRENE ────────────────────────────────────────────────────────────

async function lookupSirene(siren: string): Promise<{
  nom: string;
  naf_code: string;
  naf_section: string;
  ca_estime: number;
  tranche_effectifs: string;
} | null> {
  const url = `https://api.insee.fr/api-sirene/3.11/siren/${siren}`;

  const resp = await fetch(url, {
    headers: {
      "Accept": "application/json",
      // L'API INSEE est ouverte sans auth pour les requetes basiques
    },
  });

  if (!resp.ok) {
    // Fallback: API Recherche Entreprises (gouv.fr) - pas d'auth requise
    const fallback = await fetch(
      `https://recherche-entreprises.api.gouv.fr/search?q=${siren}&page=1&per_page=1`
    );

    if (!fallback.ok) return null;

    const data = await fallback.json();
    const result = data.results?.[0];
    if (!result) return null;

    const nafCode = result.activite_principale || "";
    const nafSection = nafCodeToSection(nafCode) || "C";
    const tranche = result.tranche_effectif_salarie || "11";
    const caEstime = CA_PAR_TRANCHE[tranche] ?? CA_PAR_TRANCHE["11"];

    return {
      nom:             result.nom_complet || result.siege?.siret || siren,
      naf_code:        nafCode,
      naf_section:     nafSection,
      ca_estime:       caEstime,
      tranche_effectifs: tranche,
    };
  }

  const data = await resp.json();
  const ul = data.uniteLegale;
  const nafCode = ul?.activitePrincipaleUniteLegale || "";
  const nafSection = nafCodeToSection(nafCode) || "C";
  const tranche = ul?.trancheEffectifsUniteLegale || "11";
  const caEstime = CA_PAR_TRANCHE[tranche] ?? CA_PAR_TRANCHE["11"];

  return {
    nom:             ul?.denominationUniteLegale || siren,
    naf_code:        nafCode,
    naf_section:     nafSection,
    ca_estime:       caEstime,
    tranche_effectifs: tranche,
  };
}

// ─── Moteur de calcul ─────────────────────────────────────────────────────────

function computeImpact(
  naf: string,
  ca: number,
  ratios: Record<string, RatioRow>,
  leontief: Record<string, Record<string, number>>,
  pmc: Record<string, number>
) {
  const r = ratios[naf];
  if (!r) throw new Error(`Section NAF '${naf}' non trouvee`);

  // Couche 1 : Direct
  const tauxVa      = (r.taux_valeur_ajoutee ?? 0) / 100;
  const va          = ca * tauxVa;
  const partPerso   = (r.part_personnel ?? 0) / 100;
  const partEtat    = (r.part_etat ?? 0) / 100;
  const salaires1   = va * partPerso;
  const taxes1      = va * partEtat;
  const productivite = PRODUCTIVITE[naf] ?? 65_000;
  const emplois1    = va / productivite;

  const direct = {
    valeur_ajoutee: Math.round(va),
    salaires:       Math.round(salaires1),
    taxes:          Math.round(taxes1),
    emplois:        Math.round(emplois1 * 10) / 10,
  };

  // Couche 2 : Indirect (Leontief)
  let va2 = 0, salaires2 = 0, taxes2 = 0, emplois2 = 0;
  const productionInduite: Record<string, number> = {};

  for (const [sj, coefs] of Object.entries(leontief)) {
    const coef = coefs[naf] ?? 0;
    if (coef <= 0) continue;

    const prodInduite = sj === naf
      ? ca * (coef - 1.0)   // enlever l'effet direct
      : ca * coef;

    if (prodInduite <= 0) continue;

    productionInduite[sj] = Math.round(prodInduite);

    const rj       = ratios[sj];
    const tauxVaJ  = ((rj?.taux_valeur_ajoutee ?? 0) / 100);
    const vaJ      = prodInduite * tauxVaJ;
    const ppJ      = ((rj?.part_personnel ?? 0) / 100);
    const peJ      = ((rj?.part_etat ?? 0) / 100);
    const prodJ    = PRODUCTIVITE[sj] ?? 65_000;

    va2       += vaJ;
    salaires2 += vaJ * ppJ;
    taxes2    += vaJ * peJ;
    emplois2  += vaJ / prodJ;
  }

  const indirect = {
    valeur_ajoutee:        Math.round(va2),
    salaires:              Math.round(salaires2),
    taxes:                 Math.round(taxes2),
    emplois:               Math.round(emplois2 * 10) / 10,
    production_par_section: productionInduite,
  };

  // Couche 3 : Induit (consommation des ménages)
  const revenus = salaires1 + salaires2;
  let va3 = 0, salaires3 = 0, taxes3 = 0, emplois3 = 0;
  const consoParSection: Record<string, number> = {};

  for (const [sk, propension] of Object.entries(pmc)) {
    const conso = revenus * propension;
    consoParSection[sk] = Math.round(conso);

    const rk    = ratios[sk];
    const tauxVaK = ((rk?.taux_valeur_ajoutee ?? 0) / 100);
    const vaK   = conso * tauxVaK;
    const ppK   = ((rk?.part_personnel ?? 0) / 100);
    const peK   = ((rk?.part_etat ?? 0) / 100);
    const prodK = PRODUCTIVITE[sk] ?? 65_000;

    va3       += vaK;
    salaires3 += vaK * ppK;
    taxes3    += vaK * peK;
    emplois3  += vaK / prodK;
  }

  const induit = {
    valeur_ajoutee:          Math.round(va3),
    salaires:                Math.round(salaires3),
    taxes:                   Math.round(taxes3),
    emplois:                 Math.round(emplois3 * 10) / 10,
    revenus_menages_base:    Math.round(revenus),
    consommation_par_section: consoParSection,
  };

  const totalEmplois = direct.emplois + indirect.emplois + induit.emplois;

  const total = {
    valeur_ajoutee: direct.valeur_ajoutee + indirect.valeur_ajoutee + induit.valeur_ajoutee,
    salaires:       direct.salaires + indirect.salaires + induit.salaires,
    taxes:          direct.taxes + indirect.taxes + induit.taxes,
    emplois:        Math.round(totalEmplois * 10) / 10,
    multiplicateur_emploi: direct.emplois > 0
      ? Math.round((totalEmplois / direct.emplois) * 100) / 100
      : null,
  };

  return { direct, indirect, induit, total };
}

// ─── Handler principal ────────────────────────────────────────────────────────

Deno.serve(async (req: Request) => {
  // CORS preflight
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders() });
  }

  if (req.method !== "POST") {
    return errorResponse("Methode non supportee. Utilisez POST.", 405);
  }

  // Parse le body
  let body: { siren?: string; naf?: string; ca?: number };
  try {
    body = await req.json();
  } catch {
    return errorResponse("Body JSON invalide");
  }

  const supabaseUrl  = Deno.env.get("SUPABASE_URL")!;
  const supabaseKey  = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const supabase     = createClient(supabaseUrl, supabaseKey);

  // ─── Chargement des donnees ────────────────────────────────────────────────

  const [r1, r2, r3] = await Promise.all([
    supabase.from("secteurs_naf_ratios").select("*"),
    supabase.from("leontief_france_naf").select("*"),
    supabase.from("consommation_menages_naf").select("*"),
  ]);

  if (r1.error) return errorResponse(`Erreur DB ratios: ${r1.error.message}`, 500);
  if (r2.error) return errorResponse(`Erreur DB leontief: ${r2.error.message}`, 500);
  if (r3.error) return errorResponse(`Erreur DB pmc: ${r3.error.message}`, 500);

  const ratios: Record<string, RatioRow> = Object.fromEntries(
    (r1.data as RatioRow[]).map(row => [row.code_naf, row])
  );

  const leontief: Record<string, Record<string, number>> = {};
  for (const row of r2.data as LeontiefRow[]) {
    if (!leontief[row.section_source]) leontief[row.section_source] = {};
    leontief[row.section_source][row.section_cible] = Number(row.coefficient);
  }

  const pmc: Record<string, number> = Object.fromEntries(
    (r3.data as PmcRow[]).map(row => [row.section_naf, Number(row.pmc)])
  );

  // ─── Determination du NAF et CA ───────────────────────────────────────────

  let nafSection: string;
  let chiffreAffaires: number;
  let entrepriseInfo: Record<string, unknown> = {};

  if (body.siren) {
    // Mode SIREN: lookup automatique
    const siren = body.siren.replace(/\s/g, "");
    if (!/^\d{9}$/.test(siren)) {
      return errorResponse("SIREN invalide (9 chiffres attendus)");
    }

    const info = await lookupSirene(siren);
    if (!info) {
      return errorResponse(`SIREN ${siren} introuvable dans SIRENE/Recherche Entreprises`);
    }

    nafSection      = info.naf_section;
    chiffreAffaires = body.ca ?? info.ca_estime;
    entrepriseInfo  = {
      siren,
      nom:              info.nom,
      naf_code:         info.naf_code,
      naf_section:      info.naf_section,
      ca_source:        body.ca ? "fourni_par_utilisateur" : "estime_tranche_effectifs",
      tranche_effectifs: info.tranche_effectifs,
    };

  } else if (body.naf && body.ca) {
    // Mode direct: NAF + CA fournis
    nafSection      = body.naf.toUpperCase();
    chiffreAffaires = body.ca;
    entrepriseInfo  = { naf_section: nafSection, ca_source: "fourni_par_utilisateur" };

  } else {
    return errorResponse(
      "Fournir soit { siren } soit { naf, ca }. " +
      "Exemple: { \"siren\": \"123456789\" } ou { \"naf\": \"F\", \"ca\": 5000000 }"
    );
  }

  if (!ratios[nafSection]) {
    return errorResponse(`Section NAF '${nafSection}' non reconnue`);
  }

  // ─── Calcul d'impact ───────────────────────────────────────────────────────

  let impact;
  try {
    impact = computeImpact(nafSection, chiffreAffaires, ratios, leontief, pmc);
  } catch (e: unknown) {
    return errorResponse(`Erreur de calcul: ${(e as Error).message}`, 500);
  }

  // ─── Persistance ───────────────────────────────────────────────────────────
  // On enregistre la simulation et l'email (si fourni) de façon non-bloquante.
  // Les erreurs d'insertion ne bloquent pas la réponse à l'utilisateur.

  const emailSaisi = typeof body.email === "string" && body.email.includes("@")
    ? body.email.trim().toLowerCase()
    : null;

  const responsePayload = {
    entreprise:  entrepriseInfo,
    secteur: {
      section_naf: nafSection,
      libelle:     ratios[nafSection].libelle,
    },
    chiffre_affaires: chiffreAffaires,
    impact,
    meta: {
      version:    "1.0.0",
      sources:    ["BdF FIBEN 2024", "OCDE ICIO 2023", "Eurostat HBS 2020"],
      calcule_le: new Date().toISOString(),
    },
  };

  // Save simulation (fire-and-forget)
  supabase.from("simulations").insert({
    siren:               entrepriseInfo.siren ?? null,
    nom_entreprise:      entrepriseInfo.nom ?? null,
    naf_section:         nafSection,
    naf_libelle:         ratios[nafSection].libelle,
    chiffre_affaires:    chiffreAffaires,
    emplois_total:       impact.total.emplois,
    va_total:            impact.total.valeur_ajoutee,
    taxes_total:         impact.total.taxes,
    multiplicateur:      impact.total.multiplicateur_emploi,
    emplois_direct:      impact.direct.emplois,
    emplois_indirect:    impact.indirect.emplois,
    emplois_induit:      impact.induit.emplois,
    email:               emailSaisi,
    ip_hash:             null, // Possible d'ajouter un hash IP pour analytics
    created_at:          new Date().toISOString(),
  }).then(({ error }) => {
    if (error) console.error("Erreur save simulation:", error.message);
  });

  // Save lead email séparément (si nouveau)
  if (emailSaisi) {
    supabase.from("leads").upsert({
      email:           emailSaisi,
      nom_entreprise:  entrepriseInfo.nom ?? null,
      siren:           entrepriseInfo.siren ?? null,
      naf_section:     nafSection,
      first_seen_at:   new Date().toISOString(),
      last_seen_at:    new Date().toISOString(),
      simulation_count: 1,
    }, {
      onConflict: "email",
      ignoreDuplicates: false,
    }).then(({ error }) => {
      if (error) console.error("Erreur save lead:", error.message);
    });

    // Incrémente simulation_count sur le lead existant
    supabase.rpc("increment_lead_simulations", { p_email: emailSaisi })
      .then(({ error }) => {
        if (error) console.error("Erreur increment lead:", error.message);
      });
  }

  // ─── Email Resend ──────────────────────────────────────────────────────────
  // Envoi non-bloquant : une erreur d'envoi ne bloque pas la réponse.

  if (emailSaisi) {
    const resendKey = Deno.env.get("RESEND_API_KEY");
    if (resendKey) {
      const nomEntreprise = entrepriseInfo.nom ?? "votre entreprise";
      const secteurLibelle = ratios[nafSection].libelle;
      const caFormate = new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(chiffreAffaires);
      const emailHtml = buildEmailHtml({
        nomEntreprise,
        secteurLibelle,
        nafSection,
        caFormate,
        impact,
      });

      fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${resendKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          from: "IN France <onboarding@resend.dev>", // TODO: remettre contact@in-france.fr après vérification domaine
          to:   [emailSaisi],
          subject: `Votre simulation d'impact territorial — ${nomEntreprise}`,
          html: emailHtml,
        }),
      }).then(async (r) => {
        if (!r.ok) {
          const err = await r.text();
          console.error("Erreur Resend:", r.status, err);
        }
      }).catch((e) => console.error("Erreur fetch Resend:", e));
    } else {
      console.warn("RESEND_API_KEY non définie — email non envoyé");
    }
  }

  // ─── Réponse ───────────────────────────────────────────────────────────────

  return jsonResponse(responsePayload);
});

// ─── Template email HTML ──────────────────────────────────────────────────────

function buildEmailHtml(p: {
  nomEntreprise: string;
  secteurLibelle: string;
  nafSection: string;
  caFormate: string;
  impact: {
    direct:   { emplois: number; valeur_ajoutee: number; taxes: number };
    indirect: { emplois: number; valeur_ajoutee: number; taxes: number };
    induit:   { emplois: number; valeur_ajoutee: number; taxes: number };
    total:    { emplois: number; valeur_ajoutee: number; taxes: number; multiplicateur_emploi: number };
  };
}): string {
  const fmt  = (n: number) => new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 }).format(n);
  const fmtE = (n: number) => n < 1 ? n.toFixed(1) : fmt(Math.round(n));
  const fmtM = (n: number) => n.toFixed(2) + "×";
  const vaM  = (n: number) => {
    if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + " M€";
    if (n >= 1_000)     return (n / 1_000).toFixed(0) + " k€";
    return n.toFixed(0) + " €";
  };

  const { direct, indirect, induit, total } = p.impact;

  const pctDirect   = total.emplois > 0 ? Math.round((direct.emplois   / total.emplois) * 100) : 0;
  const pctIndirect = total.emplois > 0 ? Math.round((indirect.emplois / total.emplois) * 100) : 0;
  const pctInduit   = 100 - pctDirect - pctIndirect;

  return `<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Votre simulation d'impact territorial — IN France</title>
</head>
<body style="margin:0;padding:0;background:#f3f5f9;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased">

<table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f5f9;padding:32px 16px">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%">

  <!-- Header tricolore -->
  <tr>
    <td style="padding:0">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td width="33%" height="4" style="background:#002395;font-size:0">&nbsp;</td>
          <td width="34%" height="4" style="background:#e8e8e8;font-size:0">&nbsp;</td>
          <td width="33%" height="4" style="background:#ED2939;font-size:0">&nbsp;</td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Logo + header -->
  <tr>
    <td style="background:#002395;padding:28px 32px 24px;border-radius:0">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td>
            <span style="font-size:22px;font-weight:700;letter-spacing:-0.5px;color:#ffffff">IN</span><span style="font-size:22px;font-weight:700;letter-spacing:-0.5px;color:#ED2939">France</span>
            <span style="font-size:11px;color:rgba(255,255,255,0.45);margin-left:10px;font-family:monospace;border:1px solid rgba(255,255,255,0.2);padding:2px 7px;border-radius:10px">Simulateur d'impact</span>
          </td>
        </tr>
        <tr><td style="padding-top:20px">
          <div style="font-size:11px;font-weight:500;letter-spacing:0.08em;text-transform:uppercase;color:rgba(255,255,255,0.45);margin-bottom:8px">Votre simulation d'impact territorial</div>
          <div style="font-size:26px;font-weight:700;letter-spacing:-0.8px;color:#ffffff;line-height:1.15">${p.nomEntreprise}</div>
          <div style="font-size:13px;color:rgba(255,255,255,0.55);margin-top:6px">${p.secteurLibelle} · Section ${p.nafSection} · CA ${p.caFormate}</div>
        </td></tr>
      </table>
    </td>
  </tr>

  <!-- KPIs principaux -->
  <tr>
    <td style="background:#ffffff;padding:28px 32px 0">
      <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:#64748b;margin-bottom:16px">Impact total généré</div>
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td width="25%" style="text-align:center;padding:0 8px 20px 0">
            <div style="font-size:28px;font-weight:700;color:#002395;letter-spacing:-1px;font-variant-numeric:tabular-nums">${fmtE(total.emplois)}</div>
            <div style="font-size:11px;color:#64748b;margin-top:3px;line-height:1.4">Emplois<br>générés</div>
          </td>
          <td width="25%" style="text-align:center;padding:0 8px 20px">
            <div style="font-size:28px;font-weight:700;color:#002395;letter-spacing:-1px">${vaM(total.valeur_ajoutee)}</div>
            <div style="font-size:11px;color:#64748b;margin-top:3px;line-height:1.4">Valeur<br>ajoutée</div>
          </td>
          <td width="25%" style="text-align:center;padding:0 8px 20px">
            <div style="font-size:28px;font-weight:700;color:#002395;letter-spacing:-1px">${vaM(total.taxes)}</div>
            <div style="font-size:11px;color:#64748b;margin-top:3px;line-height:1.4">Contributions<br>fiscales</div>
          </td>
          <td width="25%" style="text-align:center;padding:0 0 20px 8px">
            <div style="font-size:28px;font-weight:700;color:#ED2939;letter-spacing:-1px">${fmtM(total.multiplicateur_emploi)}</div>
            <div style="font-size:11px;color:#64748b;margin-top:3px;line-height:1.4">Multiplicateur<br>d'emploi</div>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Barre de décomposition -->
  <tr>
    <td style="background:#ffffff;padding:0 32px 28px">
      <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:#64748b;margin-bottom:10px">Décomposition des emplois</div>
      <table width="100%" cellpadding="0" cellspacing="0" style="border-radius:4px;overflow:hidden">
        <tr>
          <td width="${pctDirect}%"   height="10" style="background:#002395;font-size:0">&nbsp;</td>
          <td width="${pctIndirect}%" height="10" style="background:#7088b8;font-size:0">&nbsp;</td>
          <td width="${pctInduit}%"   height="10" style="background:#ED2939;font-size:0">&nbsp;</td>
        </tr>
      </table>
      <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:10px">
        <tr>
          <td style="font-size:12px;color:#64748b"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#002395;margin-right:5px;vertical-align:middle"></span>Directs ${pctDirect}%</td>
          <td style="font-size:12px;color:#64748b;text-align:center"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#7088b8;margin-right:5px;vertical-align:middle"></span>Indirects ${pctIndirect}%</td>
          <td style="font-size:12px;color:#64748b;text-align:right"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#ED2939;margin-right:5px;vertical-align:middle"></span>Induits ${pctInduit}%</td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Détail 3 couches -->
  <tr>
    <td style="background:#f3f5f9;padding:2px 0"></td>
  </tr>
  <tr>
    <td style="background:#ffffff;padding:24px 32px">
      <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:#64748b;margin-bottom:14px">Détail par couche</div>
      <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #dde3ee;border-radius:6px;overflow:hidden">
        <tr style="background:#f3f5f9">
          <td style="padding:9px 14px;font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.06em">Couche</td>
          <td style="padding:9px 14px;font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.06em;text-align:right">Emplois</td>
          <td style="padding:9px 14px;font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.06em;text-align:right">Valeur ajoutée</td>
          <td style="padding:9px 14px;font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.06em;text-align:right">Taxes</td>
        </tr>
        <tr style="border-top:1px solid #dde3ee">
          <td style="padding:11px 14px;font-size:13px"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#002395;margin-right:7px;vertical-align:middle"></span><strong>Directs</strong></td>
          <td style="padding:11px 14px;font-size:13px;font-family:monospace;text-align:right;color:#002395;font-weight:600">${fmtE(direct.emplois)}</td>
          <td style="padding:11px 14px;font-size:13px;font-family:monospace;text-align:right">${vaM(direct.valeur_ajoutee)}</td>
          <td style="padding:11px 14px;font-size:13px;font-family:monospace;text-align:right">${vaM(direct.taxes)}</td>
        </tr>
        <tr style="border-top:1px solid #dde3ee;background:#fafbfd">
          <td style="padding:11px 14px;font-size:13px"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#7088b8;margin-right:7px;vertical-align:middle"></span>Indirects</td>
          <td style="padding:11px 14px;font-size:13px;font-family:monospace;text-align:right;color:#7088b8;font-weight:600">${fmtE(indirect.emplois)}</td>
          <td style="padding:11px 14px;font-size:13px;font-family:monospace;text-align:right">${vaM(indirect.valeur_ajoutee)}</td>
          <td style="padding:11px 14px;font-size:13px;font-family:monospace;text-align:right">${vaM(indirect.taxes)}</td>
        </tr>
        <tr style="border-top:1px solid #dde3ee">
          <td style="padding:11px 14px;font-size:13px"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#ED2939;margin-right:7px;vertical-align:middle"></span>Induits</td>
          <td style="padding:11px 14px;font-size:13px;font-family:monospace;text-align:right;color:#ED2939;font-weight:600">${fmtE(induit.emplois)}</td>
          <td style="padding:11px 14px;font-size:13px;font-family:monospace;text-align:right">${vaM(induit.valeur_ajoutee)}</td>
          <td style="padding:11px 14px;font-size:13px;font-family:monospace;text-align:right">${vaM(induit.taxes)}</td>
        </tr>
        <tr style="border-top:2px solid #dde3ee;background:#f3f5f9">
          <td style="padding:11px 14px;font-size:13px;font-weight:700">Total</td>
          <td style="padding:11px 14px;font-size:13px;font-family:monospace;text-align:right;font-weight:700;color:#002395">${fmtE(total.emplois)}</td>
          <td style="padding:11px 14px;font-size:13px;font-family:monospace;text-align:right;font-weight:700">${vaM(total.valeur_ajoutee)}</td>
          <td style="padding:11px 14px;font-size:13px;font-family:monospace;text-align:right;font-weight:700">${vaM(total.taxes)}</td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Multiplicateur explication -->
  <tr>
    <td style="background:#f3f5f9;padding:2px 0"></td>
  </tr>
  <tr>
    <td style="background:#ffffff;padding:20px 32px">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#eef1ff;border-radius:6px;padding:16px">
        <tr>
          <td style="padding:16px">
            <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:#002395;margin-bottom:6px">Multiplicateur d'emploi</div>
            <div style="font-size:32px;font-weight:700;color:#002395;letter-spacing:-1px;margin-bottom:6px">${fmtM(total.multiplicateur_emploi)}</div>
            <div style="font-size:13px;color:#475569;line-height:1.55">Pour chaque emploi direct créé, <strong>${fmtM(total.multiplicateur_emploi)}</strong> emplois sont générés au total dans l'économie française — via les achats intermédiaires et la consommation des ménages.</div>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- CTA -->
  <tr>
    <td style="background:#f3f5f9;padding:2px 0"></td>
  </tr>
  <tr>
    <td style="background:#002395;padding:28px 32px;border-radius:0 0 0 0">
      <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:rgba(255,255,255,0.45);margin-bottom:10px">Passez à l'étape suivante</div>
      <div style="font-size:18px;font-weight:700;color:#ffffff;letter-spacing:-0.3px;margin-bottom:8px">Transformez cette simulation en rapport complet</div>
      <div style="font-size:13px;color:rgba(255,255,255,0.55);margin-bottom:20px;line-height:1.55">Nos experts analysent la structure réelle de ${p.nomEntreprise} et produisent un rapport d'impact territorial sur-mesure — pour vos investisseurs, collectivités ou partenaires.</div>
      <a href="https://www.in-france.fr/demo" style="display:inline-block;background:#ED2939;color:#ffffff;text-decoration:none;padding:11px 24px;border-radius:6px;font-size:13px;font-weight:600;letter-spacing:-0.1px">Prendre rendez-vous →</a>
    </td>
  </tr>

  <!-- Footer -->
  <tr>
    <td style="background:#f3f5f9;padding:20px 32px;border-radius:0 0 8px 8px">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td style="font-size:12px;color:#94a3b8;line-height:1.6">
            <strong style="color:#64748b">IN France</strong> · Groupe Société.com · Fabriqué en 🇫🇷<br>
            Ces résultats sont des estimations basées sur des ratios sectoriels moyens (BdF FIBEN 2024, OCDE ICIO 2023, Eurostat HBS 2020).<br>
            <a href="https://simulateur.in-france.fr/methodologie" style="color:#002395;text-decoration:none">Voir la méthodologie complète</a> · 
            <a href="https://www.in-france.fr/politique-confidentialite" style="color:#94a3b8;text-decoration:none">Se désabonner</a>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Tricolore bas -->
  <tr>
    <td style="padding:0">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td width="33%" height="3" style="background:#002395;font-size:0">&nbsp;</td>
          <td width="34%" height="3" style="background:#e8e8e8;font-size:0">&nbsp;</td>
          <td width="33%" height="3" style="background:#ED2939;font-size:0">&nbsp;</td>
        </tr>
      </table>
    </td>
  </tr>

</table>
</td></tr>
</table>
</body>
</html>`;
}