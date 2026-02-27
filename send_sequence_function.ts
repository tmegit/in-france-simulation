// supabase/functions/send-sequence/index.ts
// Edge Function cron — séquence email nurturing IN France
// Appelée toutes les heures par le cron Supabase
//
// Séquence :
//   J0   — email résumé simulation (envoyé par la fonction impact)
//   J+3  — "Que signifient vos chiffres ?" + cas d'usage similaire
//   J+7  — "Passez au rapport certifié" + témoignage + urgence douce

import { createClient } from "npm:@supabase/supabase-js@2";

// ─── Types ────────────────────────────────────────────────────────────────────

interface Lead {
  id: number;
  email: string;
  nom_entreprise: string | null;
  naf_section: string | null;
  simulation_count: number;
  next_step: 2 | 3;
  rdv_url_token: string;
}

// ─── Mapping NAF → cas d'usage similaire ─────────────────────────────────────

const NAF_CAS_USAGE: Record<string, { client: string; url: string; desc: string }> = {
  A: { client: "Groupe Groupama", url: "https://www.in-france.fr/impact/cas-usage/groupe-groupama", desc: "comment un acteur agricole ancré dans les régions a valorisé son impact territorial" },
  C: { client: "Amazon Logistique France", url: "https://www.in-france.fr/impact/cas-usage/amazon-logistique-france", desc: "comment un site industriel a objectivé ses retombées économiques locales" },
  G: { client: "Amazon Logistique France", url: "https://www.in-france.fr/impact/cas-usage/amazon-logistique-france", desc: "comment une plateforme de distribution a mesuré son ancrage territorial" },
  K: { client: "France Invest", url: "https://www.in-france.fr/impact/cas-usage", desc: "comment des acteurs financiers démontrent leur contribution à l'économie réelle" },
  M: { client: "Carbone 4", url: "https://www.in-france.fr/impact/cas-usage/carbone-4", desc: "comment un cabinet de conseil a modélisé l'impact territorial de ses recommandations" },
  R: { client: "24h du Mans — ACO", url: "https://www.in-france.fr/impact/cas-usage/24h-du-mans", desc: "comment un organisateur d'événements mesure ses retombées touristiques et fiscales" },
};

const DEFAULT_CAS_USAGE = {
  client: "Nos clients",
  url: "https://www.in-france.fr/impact/cas-usage",
  desc: "comment des entreprises de tous secteurs valorisent leur impact territorial",
};

function getCasUsage(nafSection: string | null) {
  return (nafSection && NAF_CAS_USAGE[nafSection]) || DEFAULT_CAS_USAGE;
}

// ─── Templates email ──────────────────────────────────────────────────────────

function buildStep2Email(lead: Lead): string {
  const nom = lead.nom_entreprise ?? "votre entreprise";
  const cas = getCasUsage(lead.naf_section);
  const rdvUrl = `https://www.in-france.fr/demo?token=${lead.rdv_url_token}`;

  return `<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Que signifient vos chiffres d'impact ?</title>
</head>
<body style="margin:0;padding:0;background:#f3f5f9;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f5f9;padding:32px 16px">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%">

  <!-- Tricolore haut -->
  <tr><td><table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td width="33%" height="4" style="background:#002395;font-size:0">&nbsp;</td>
    <td width="34%" height="4" style="background:#e8e8e8;font-size:0">&nbsp;</td>
    <td width="33%" height="4" style="background:#ED2939;font-size:0">&nbsp;</td>
  </tr></table></td></tr>

  <!-- Header -->
  <tr><td style="background:#ffffff;padding:28px 32px 24px">
    <span style="font-size:20px;font-weight:700;color:#002395">IN</span><span style="font-size:20px;font-weight:700;color:#ED2939">France</span>
    <span style="font-size:11px;color:#94a3b8;margin-left:8px;font-family:monospace;border:1px solid #dde3ee;padding:2px 7px;border-radius:10px">Séquence impact</span>
  </td></tr>

  <!-- Intro -->
  <tr><td style="background:#ffffff;padding:0 32px 28px;border-bottom:1px solid #dde3ee">
    <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:#64748b;margin-bottom:10px">Il y a 3 jours, vous avez simulé l'impact de ${nom}</div>
    <div style="font-size:24px;font-weight:700;letter-spacing:-0.6px;color:#0d1b2a;line-height:1.2;margin-bottom:14px">Que signifient vraiment vos chiffres ?</div>
    <div style="font-size:14px;color:#475569;line-height:1.7">Le simulateur vous a donné des estimations. Voici comment les lire, les utiliser — et ce qu'elles peuvent déclencher concrètement.</div>
  </td></tr>

  <!-- Explication multiplicateur -->
  <tr><td style="background:#ffffff;padding:24px 32px">
    <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:#64748b;margin-bottom:14px">Le multiplicateur d'emploi — l'indicateur clé</div>
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#eef1ff;border-radius:8px">
      <tr><td style="padding:20px">
        <div style="font-size:13px;color:#002395;font-weight:600;margin-bottom:8px">Qu'est-ce que ça veut dire concrètement ?</div>
        <div style="font-size:13px;color:#475569;line-height:1.7;margin-bottom:12px">Un multiplicateur de <strong style="color:#002395">2,4×</strong> signifie que pour chaque emploi que vous créez directement, l'économie locale génère 1,4 emplois supplémentaires chez vos fournisseurs et dans la consommation des ménages.</div>
        <div style="font-size:13px;color:#475569;line-height:1.7">C'est cet effet de levier que vos parties prenantes — élus, investisseurs, partenaires ESG — veulent voir démontré avec des chiffres certifiés.</div>
      </td></tr>
    </table>
  </td></tr>

  <!-- 3 usages -->
  <tr><td style="background:#f3f5f9;padding:2px 0"></td></tr>
  <tr><td style="background:#ffffff;padding:24px 32px">
    <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:#64748b;margin-bottom:16px">3 façons d'utiliser ces indicateurs</div>

    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:12px">
      <tr>
        <td width="36" valign="top" style="padding-top:1px">
          <div style="width:28px;height:28px;border-radius:50%;background:#002395;display:inline-flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#fff;text-align:center;line-height:28px">1</div>
        </td>
        <td style="padding-left:12px">
          <div style="font-size:13px;font-weight:600;color:#0d1b2a;margin-bottom:3px">Dialogue avec les élus et territoires</div>
          <div style="font-size:13px;color:#475569;line-height:1.6">Présentez votre contribution fiscale et vos emplois indirects à votre commune, département ou région. Ces chiffres crédibilisent vos demandes de soutien ou de foncier.</div>
        </td>
      </tr>
    </table>

    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:12px">
      <tr>
        <td width="36" valign="top" style="padding-top:1px">
          <div style="width:28px;height:28px;border-radius:50%;background:#002395;display:inline-flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#fff;text-align:center;line-height:28px">2</div>
        </td>
        <td style="padding-left:12px">
          <div style="font-size:13px;font-weight:600;color:#0d1b2a;margin-bottom:3px">Rapport CSRD et stratégie RSE</div>
          <div style="font-size:13px;color:#475569;line-height:1.6">Les effets indirects et induits font partie des indicateurs attendus dans le reporting de durabilité. Intégrez-les à votre rapport annuel avec une méthodologie traçable.</div>
        </td>
      </tr>
    </table>

    <table width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td width="36" valign="top" style="padding-top:1px">
          <div style="width:28px;height:28px;border-radius:50%;background:#ED2939;display:inline-flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#fff;text-align:center;line-height:28px">3</div>
        </td>
        <td style="padding-left:12px">
          <div style="font-size:13px;font-weight:600;color:#0d1b2a;margin-bottom:3px">Communication institutionnelle et marketing</div>
          <div style="font-size:13px;color:#475569;line-height:1.6">Valorisez votre ancrage territorial auprès de vos clients, partenaires et médias avec des chiffres sourcés et indépendants — bien plus percutants qu'un discours.</div>
        </td>
      </tr>
    </table>
  </td></tr>

  <!-- Cas d'usage similaire -->
  <tr><td style="background:#f3f5f9;padding:2px 0"></td></tr>
  <tr><td style="background:#ffffff;padding:24px 32px">
    <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:#64748b;margin-bottom:14px">Nos clients</div>
    <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #dde3ee;border-radius:6px">
      <tr><td style="padding:18px">
        <div style="font-size:13px;font-weight:600;color:#0d1b2a;margin-bottom:6px">${cas.client}</div>
        <div style="font-size:13px;color:#475569;line-height:1.6;margin-bottom:14px">Découvrez ${cas.desc}.</div>
        <a href="${cas.url}" style="font-size:13px;font-weight:600;color:#002395;text-decoration:none">Lire le cas d'usage →</a>
      </td></tr>
    </table>
    <!-- Logos clients -->
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:16px">
      <tr>
        <td style="padding:0 0 12px;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:#64748b">Ils nous font confiance</td>
      </tr>
      <tr>
        <td>
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="padding:6px 8px 6px 0;vertical-align:middle">
                <img src="https://www.google.com/s2/favicons?domain=amazon.fr&sz=32" width="28" height="28" alt="Amazon" style="border-radius:4px;display:block">
              </td>
              <td style="padding:6px 8px;vertical-align:middle">
                <img src="https://www.google.com/s2/favicons?domain=groupama.fr&sz=32" width="28" height="28" alt="Groupama" style="border-radius:4px;display:block">
              </td>
              <td style="padding:6px 8px;vertical-align:middle">
                <img src="https://www.google.com/s2/favicons?domain=interieur.gouv.fr&sz=32" width="28" height="28" alt="Ministère Intérieur" style="border-radius:4px;display:block">
              </td>
              <td style="padding:6px 8px;vertical-align:middle">
                <img src="https://www.google.com/s2/favicons?domain=24h-lemans.com&sz=32" width="28" height="28" alt="24h du Mans" style="border-radius:4px;display:block">
              </td>
              <td style="padding:6px 8px;vertical-align:middle">
                <img src="https://www.google.com/s2/favicons?domain=carbone4.com&sz=32" width="28" height="28" alt="Carbone 4" style="border-radius:4px;display:block">
              </td>
              <td style="padding:6px 8px;vertical-align:middle;font-size:12px;color:#94a3b8">+85 organisations</td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </td></tr>

  <!-- CTA -->
  <tr><td style="background:#f3f5f9;padding:2px 0"></td></tr>
  <tr><td style="background:#002395;padding:28px 32px">
    <div style="font-size:18px;font-weight:700;color:#ffffff;letter-spacing:-0.3px;margin-bottom:8px">Prêt à aller plus loin avec ${nom} ?</div>
    <div style="font-size:13px;color:rgba(255,255,255,0.55);margin-bottom:20px;line-height:1.55">Un rapport complet transforme ces estimations en indicateurs certifiés, territorialisés et prêts à être partagés. Livraison en 72h.</div>
    <a href="${rdvUrl}" style="display:inline-block;background:#ED2939;color:#ffffff;text-decoration:none;padding:11px 24px;border-radius:6px;font-size:13px;font-weight:600">Prendre rendez-vous →</a>
  </td></tr>

  <!-- Footer -->
  <tr><td style="background:#f3f5f9;padding:18px 32px;border-radius:0 0 8px 8px">
    <div style="font-size:12px;color:#94a3b8;line-height:1.6">
      <strong style="color:#64748b">IN France</strong> · Groupe Société.com · Fabriqué en 🇫🇷<br>
      <a href="https://simulateur.in-france.fr/methodologie" style="color:#002395;text-decoration:none">Méthodologie</a> ·
      <a href="https://simulateur.in-france.fr/unsubscribe?email=${encodeURIComponent(lead.email)}" style="color:#94a3b8;text-decoration:none">Se désabonner</a>
    </div>
  </td></tr>

  <!-- Tricolore bas -->
  <tr><td><table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td width="33%" height="3" style="background:#002395;font-size:0">&nbsp;</td>
    <td width="34%" height="3" style="background:#e8e8e8;font-size:0">&nbsp;</td>
    <td width="33%" height="3" style="background:#ED2939;font-size:0">&nbsp;</td>
  </tr></table></td></tr>

</table>
</td></tr></table>
</body>
</html>`;
}

function buildStep3Email(lead: Lead): string {
  const nom = lead.nom_entreprise ?? "votre entreprise";
  const rdvUrl = `https://www.in-france.fr/demo?token=${lead.rdv_url_token}`;
  const simulations = lead.simulation_count;

  return `<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Passez au rapport certifié — IN France</title>
</head>
<body style="margin:0;padding:0;background:#f3f5f9;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f5f9;padding:32px 16px">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%">

  <!-- Tricolore haut -->
  <tr><td><table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td width="33%" height="4" style="background:#002395;font-size:0">&nbsp;</td>
    <td width="34%" height="4" style="background:#e8e8e8;font-size:0">&nbsp;</td>
    <td width="33%" height="4" style="background:#ED2939;font-size:0">&nbsp;</td>
  </tr></table></td></tr>

  <!-- Header -->
  <tr><td style="background:#ffffff;padding:28px 32px 24px">
    <span style="font-size:20px;font-weight:700;color:#002395">IN</span><span style="font-size:20px;font-weight:700;color:#ED2939">France</span>
    <span style="font-size:11px;color:#94a3b8;margin-left:8px;font-family:monospace;border:1px solid #dde3ee;padding:2px 7px;border-radius:10px">Dernier message</span>
  </td></tr>

  <!-- Intro personnalisée -->
  <tr><td style="background:#ffffff;padding:0 32px 24px;border-bottom:1px solid #dde3ee">
    <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:#64748b;margin-bottom:10px">${simulations > 1 ? `Vous avez effectué ${simulations} simulations` : "Il y a 7 jours, vous avez simulé votre impact"}</div>
    <div style="font-size:24px;font-weight:700;letter-spacing:-0.6px;color:#0d1b2a;line-height:1.2;margin-bottom:14px">La simulation, c'est bien.<br>Le rapport certifié, c'est ce qui convainc.</div>
    <div style="font-size:14px;color:#475569;line-height:1.7">Voici exactement ce que vous obtenez en plus avec un rapport d'impact territorial complet sur ${nom}.</div>
  </td></tr>

  <!-- Comparaison simulation vs rapport -->
  <tr><td style="background:#ffffff;padding:24px 32px">
    <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #dde3ee;border-radius:6px;overflow:hidden">
      <tr style="background:#f3f5f9">
        <td style="padding:10px 14px;font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.06em;width:40%">Fonctionnalité</td>
        <td style="padding:10px 14px;font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.06em;text-align:center">Simulateur gratuit</td>
        <td style="padding:10px 14px;font-size:11px;font-weight:600;color:#002395;text-transform:uppercase;letter-spacing:0.06em;text-align:center">Rapport certifié</td>
      </tr>
      ${[
        ["Indicateurs directs / indirects / induits", "✓", "✓"],
        ["Données sectorielles moyennes", "✓", "✓"],
        ["Données réelles de l'entreprise", "—", "✓"],
        ["Déclinaison par territoire (communes, EPCI...)", "—", "✓"],
        ["Lecture fine par code NAF", "—", "✓"],
        ["Interface web interactive", "—", "✓"],
        ["Rapport PDF prêt à partager", "—", "✓"],
        ["Méthodologie certifiable (CSRD, RSE)", "—", "✓"],
        ["Livraison", "Instantané", "72h"],
      ].map(([feat, sim, rapport]) => `
      <tr style="border-top:1px solid #dde3ee">
        <td style="padding:10px 14px;font-size:13px;color:#475569">${feat}</td>
        <td style="padding:10px 14px;font-size:13px;text-align:center;color:${sim === "✓" ? "#16a34a" : "#94a3b8"}">${sim}</td>
        <td style="padding:10px 14px;font-size:13px;text-align:center;color:${rapport === "✓" || rapport === "72h" ? "#002395" : "#94a3b8"};font-weight:${rapport === "✓" || rapport === "72h" ? "600" : "400"}">${rapport}</td>
      </tr>`).join("")}
    </table>
  </td></tr>

  <!-- Témoignage -->
  <tr><td style="background:#f3f5f9;padding:2px 0"></td></tr>
  <tr><td style="background:#ffffff;padding:24px 32px">
    <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:#64748b;margin-bottom:14px">Nos clients</div>
    <table width="100%" cellpadding="0" cellspacing="0" style="border-left:3px solid #002395;background:#f8faff;border-radius:0 6px 6px 0">
      <tr><td style="padding:18px 20px">
        <div style="font-size:14px;color:#0d1b2a;line-height:1.7;font-style:italic;margin-bottom:12px">« Cette plateforme est un outil de pilotage structurant, qui alimente nos analyses, nos orientations d'achat et notre capacité à démontrer concrètement la performance publique. »</div>
        <div style="font-size:12px;font-weight:600;color:#64748b">— Julien Fischer, Chef de section pilotage de la performance des achats<br><span style="font-weight:400">Ministère de l'Intérieur · 175 000+ fournisseurs analysés</span></div>
      </td></tr>
    </table>
  </td></tr>

  <!-- Stats réassurance -->
  <tr><td style="background:#f3f5f9;padding:2px 0"></td></tr>
  <tr><td style="background:#ffffff;padding:24px 32px">
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td style="text-align:center;padding:0 8px">
          <div style="font-size:28px;font-weight:700;color:#002395;letter-spacing:-1px">340+</div>
          <div style="font-size:12px;color:#64748b;margin-top:3px">Rapports effectués</div>
        </td>
        <td style="text-align:center;padding:0 8px;border-left:1px solid #dde3ee;border-right:1px solid #dde3ee">
          <div style="font-size:28px;font-weight:700;color:#002395;letter-spacing:-1px">90+</div>
          <div style="font-size:12px;color:#64748b;margin-top:3px">Clients en UE</div>
        </td>
        <td style="text-align:center;padding:0 8px">
          <div style="font-size:28px;font-weight:700;color:#ED2939;letter-spacing:-1px">72h</div>
          <div style="font-size:12px;color:#64748b;margin-top:3px">Délai de livraison</div>
        </td>
      </tr>
    </table>
  </td></tr>

  <!-- CTA final -->
  <tr><td style="background:#f3f5f9;padding:2px 0"></td></tr>
  <tr><td style="background:#002395;padding:28px 32px">
    <div style="font-size:18px;font-weight:700;color:#ffffff;letter-spacing:-0.3px;margin-bottom:8px">Obtenez le rapport complet pour ${nom}</div>
    <div style="font-size:13px;color:rgba(255,255,255,0.55);margin-bottom:20px;line-height:1.55">30 minutes d'échange suffisent pour cadrer l'analyse. Livraison sous 72h.</div>
    <a href="${rdvUrl}" style="display:inline-block;background:#ED2939;color:#ffffff;text-decoration:none;padding:11px 24px;border-radius:6px;font-size:13px;font-weight:600;margin-right:10px">Prendre rendez-vous →</a>
    <a href="https://www.in-france.fr/impact/cas-usage" style="display:inline-block;color:rgba(255,255,255,0.6);text-decoration:none;font-size:13px;margin-top:12px">Voir tous les cas d'usage</a>
  </td></tr>

  <!-- Footer -->
  <tr><td style="background:#f3f5f9;padding:18px 32px;border-radius:0 0 8px 8px">
    <div style="font-size:12px;color:#94a3b8;line-height:1.6">
      <strong style="color:#64748b">IN France</strong> · Groupe Société.com · Fabriqué en 🇫🇷<br>
      C'est notre dernier email — promis 🙂<br>
      <a href="https://simulateur.in-france.fr/methodologie" style="color:#002395;text-decoration:none">Méthodologie</a> ·
      <a href="https://simulateur.in-france.fr/unsubscribe?email=${encodeURIComponent(lead.email)}" style="color:#94a3b8;text-decoration:none">Se désabonner</a>
    </div>
  </td></tr>

  <!-- Tricolore bas -->
  <tr><td><table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td width="33%" height="3" style="background:#002395;font-size:0">&nbsp;</td>
    <td width="34%" height="3" style="background:#e8e8e8;font-size:0">&nbsp;</td>
    <td width="33%" height="3" style="background:#ED2939;font-size:0">&nbsp;</td>
  </tr></table></td></tr>

</table>
</td></tr></table>
</body>
</html>`;
}

// ─── Handler principal ────────────────────────────────────────────────────────

Deno.serve(async () => {
  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const resendKey   = Deno.env.get("RESEND_API_KEY");

  if (!resendKey) {
    console.error("RESEND_API_KEY manquante");
    return new Response(JSON.stringify({ error: "RESEND_API_KEY manquante" }), { status: 500 });
  }

  const supabase = createClient(supabaseUrl, supabaseKey);

  // Récupérer les leads qui ont besoin du prochain email
  const { data: leads, error } = await supabase
    .from("v_leads_to_contact")
    .select("*");

  if (error) {
    console.error("Erreur lecture leads:", error.message);
    return new Response(JSON.stringify({ error: error.message }), { status: 500 });
  }

  if (!leads || leads.length === 0) {
    console.log("Aucun lead à contacter.");
    return new Response(JSON.stringify({ sent: 0 }), { status: 200 });
  }

  const FROM = "IN France <contact@in-france.fr>";

  let sent = 0;
  let errors = 0;

  for (const lead of leads as Lead[]) {
    const step = lead.next_step;
    let subject: string;
    let html: string;

    if (step === 2) {
      subject = `Que signifient vraiment vos chiffres d'impact, ${lead.nom_entreprise ?? ""} ?`.trim();
      html    = buildStep2Email(lead);
    } else if (step === 3) {
      subject = `Le rapport certifié pour ${lead.nom_entreprise ?? "votre entreprise"} — dernière étape`;
      html    = buildStep3Email(lead);
    } else {
      continue;
    }

    try {
      const res = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${resendKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ from: FROM, to: [lead.email], subject, html }),
      });

      if (res.ok) {
        // Marquer le step comme envoyé en base
        await supabase.rpc("mark_email_step_sent", {
          p_lead_id: lead.id,
          p_step:    step,
        });
        console.log(`✓ Step ${step} envoyé à ${lead.email}`);
        sent++;
      } else {
        const err = await res.text();
        console.error(`✗ Erreur Resend step ${step} → ${lead.email}:`, err);
        errors++;
      }
    } catch (e) {
      console.error(`✗ Exception step ${step} → ${lead.email}:`, e);
      errors++;
    }
  }

  return new Response(JSON.stringify({ sent, errors, total: leads.length }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
});
