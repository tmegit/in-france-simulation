#!/usr/bin/env python3
"""Générateur de pages sectorielles IN France, SEO landing pages."""

import json, os

# ─── SECTOR DATA ─────────────────────────────────────────────────────────────

SECTORS = [
  {
    "code": "A", "slug": "agriculture",
    "label": "Agriculture, sylviculture et pêche",
    "short": "Agriculture",
    "emoji": "🌾",
    "nb_entreprises": "349 600", "nb_emplois": "663 000",
    "ca_cumule": "96,5 Md€", "pib_pct": "1,6",
    "source_nb": "Agreste 2023 · INSEE comptes nationaux 2023",
    "hero_sub": "Premier secteur agricole européen, l'agriculture française nourrit 67 millions d'habitants et exporte dans le monde entier. Chaque exploitation agricole génère un effet d'entraînement massif sur l'industrie agroalimentaire, le transport et le commerce.",
    "content_intro": "L'agriculture française représente un pilier historique de l'économie nationale. Avec 349 600 exploitations réparties sur tout le territoire (Agreste 2023), le secteur emploie directement 663 000 personnes en équivalent temps plein et génère une production de 96,5 milliards d'euros. La France est le premier producteur agricole de l'Union européenne.",
    "content_direct": "Les effets directs du secteur agricole se manifestent par la création d'emplois dans les exploitations (salariés permanents et saisonniers), la génération de valeur ajoutée à hauteur de 42,5 % du chiffre d'affaires, et des contributions fiscales représentant 5,3 % de la valeur ajoutée. La part des salaires dans la valeur ajoutée atteint 52,4 %.",
    "content_indirect": "L'agriculture active fortement l'industrie manufacturière (agroalimentaire), le commerce de gros, les transports et la logistique. Via la matrice de Leontief, on observe que pour 1 € de production agricole, 0,22 € de production manufacturière et 0,15 € de commerce sont générés dans la chaîne d'approvisionnement.",
    "content_induced": "Les salaires versés aux 700 000 employés du secteur alimentent la consommation locale : logement, alimentation, transports, loisirs. Cet effet induit représente un levier supplémentaire significatif pour l'économie des territoires ruraux.",
    "faq": [
      ("Combien d'emplois le secteur agricole génère-t-il en France ?", "Le secteur agricole emploie directement environ 700 000 personnes en France. Grâce à un multiplicateur d'emploi de 2,15×, chaque emploi direct génère 1,15 emploi supplémentaire dans l'économie, soit un total d'environ 1,5 million d'emplois soutenus."),
      ("Quel est le multiplicateur d'emploi de l'agriculture ?", "Le multiplicateur d'emploi du secteur agricole est de 2,15×, supérieur à la moyenne nationale de 1,82×. Cela signifie que pour chaque emploi agricole direct, 1,15 emplois supplémentaires sont créés dans les secteurs fournisseurs et par la consommation des ménages."),
      ("Comment mesurer l'impact territorial d'une exploitation agricole ?", "Notre simulateur utilise les données BdF FIBEN 2024, la matrice Leontief OCDE ICIO 2023 et les données Eurostat HBS 2020 pour calculer les effets directs (emplois, VA, taxes), indirects (chaîne d'approvisionnement) et induits (consommation des salariés) de toute exploitation agricole à partir de son SIREN et chiffre d'affaires.")
    ]
  },
  {
    "code": "B", "slug": "industries-extractives",
    "label": "Industries extractives",
    "short": "Industries extractives",
    "emoji": "⛏️",
    "nb_entreprises": "960", "nb_emplois": "14 391",
    "ca_cumule": "5,7 Md€", "pib_pct": "0,3",
    "source_nb": "INSEE ESANE 2023",
    "hero_sub": "Les industries extractives regroupent l'extraction de minerais, de pierres et de ressources naturelles. Un secteur à forte intensité capitalistique dont l'impact se propage à travers l'industrie manufacturière et la construction.",
    "content_intro": "Le secteur des industries extractives en France regroupe 960 entreprises spécialisées dans l'extraction de ressources minérales, de pierre, de sable et de gravier (INSEE ESANE 2023). Avec 14 391 salariés en EQTP et 5,7 milliards d'euros de chiffre d'affaires, ce secteur joue un rôle stratégique dans la chaîne de valeur industrielle française.",
    "content_direct": "Avec un taux de valeur ajoutée de 36,8 % du chiffre d'affaires, les industries extractives génèrent une part significative de richesse par euro produit. La part des salaires représente 50,5 % de la valeur ajoutée, tandis que les contributions fiscales atteignent 8,2 %.",
    "content_indirect": "Ce secteur alimente principalement l'industrie manufacturière (coefficient Leontief de 0,21) et le commerce (0,11). Les matériaux extraits constituent des intrants essentiels pour la construction, la chimie et la métallurgie.",
    "content_induced": "Malgré un nombre d'emplois directs limité, les salaires versés dans le secteur contribuent à l'économie locale des territoires d'extraction, souvent situés en zones rurales ou périurbaines.",
    "faq": [
      ("Combien d'entreprises extractives existent en France ?", "La France compte environ 3 500 entreprises dans le secteur des industries extractives, employant directement 30 000 personnes pour un chiffre d'affaires cumulé d'environ 8 milliards d'euros."),
      ("Quel est l'impact économique des carrières et mines en France ?", "Avec un multiplicateur d'emploi de 1,60× et un taux de valeur ajoutée de 36,8 %, chaque entreprise extractive génère des effets indirects significatifs dans l'industrie manufacturière, la construction et le transport."),
      ("Comment est calculé l'impact territorial d'une entreprise extractive ?", "Le simulateur IN France utilise les ratios sectoriels BdF FIBEN, la matrice Leontief OCDE et les données Eurostat pour calculer les trois couches d'impact : direct, indirect (chaîne d'approvisionnement) et induit (consommation des salariés).")
    ]
  },
  {
    "code": "C", "slug": "industrie-manufacturiere",
    "label": "Industrie manufacturière",
    "short": "Industrie manufacturière",
    "emoji": "🏭",
    "nb_entreprises": "266 068", "nb_emplois": "2 935 313",
    "ca_cumule": "1 247 Md€", "pib_pct": "10,0",
    "source_nb": "INSEE ESANE 2023",
    "hero_sub": "L'industrie manufacturière est le moteur de l'économie productive française. De l'agroalimentaire à l'aéronautique, ce secteur transforme les matières premières en produits finis et génère un effet d'entraînement considérable sur l'ensemble de l'économie.",
    "content_intro": "Avec 266 068 entreprises et 2 935 313 salariés en EQTP (INSEE ESANE 2023), l'industrie manufacturière française représente environ 10 % du PIB national et 1 247 milliards d'euros de chiffre d'affaires. Ce secteur englobe une grande diversité d'activités : agroalimentaire, chimie, pharmacie, automobile, aéronautique, métallurgie, textile et bien d'autres.",
    "content_direct": "Le taux de valeur ajoutée du secteur atteint 37,8 % du chiffre d'affaires. La part des salaires est élevée (73,4 % de la VA), reflétant l'intensité en main-d'œuvre qualifiée. Les contributions fiscales représentent 5,0 % de la VA.",
    "content_indirect": "L'industrie manufacturière est le secteur le plus interconnecté de l'économie française. Son coefficient Leontief intra-sectoriel de 1,25 montre un fort effet d'entraînement interne. Elle active massivement le commerce (0,13), les services spécialisés (0,06) et les transports (0,05).",
    "content_induced": "Avec 2,7 millions d'emplois et des salaires souvent supérieurs à la moyenne, l'effet induit de l'industrie manufacturière est considérable. Les ménages des salariés industriels injectent des milliards d'euros dans l'économie locale via leurs dépenses de consommation.",
    "faq": [
      ("Combien d'emplois l'industrie manufacturière crée-t-elle en France ?", "L'industrie manufacturière emploie directement 2,7 millions de personnes en France. Avec un multiplicateur d'emploi de 2,10×, elle soutient au total environ 5,7 millions d'emplois dans l'économie française."),
      ("Quel est le poids de l'industrie dans le PIB français ?", "L'industrie manufacturière représente environ 10 % du PIB français, soit plus de 1 100 milliards d'euros de chiffre d'affaires cumulé, répartis dans 230 000 entreprises."),
      ("Pourquoi l'industrie a-t-elle un fort multiplicateur d'emploi ?", "Avec un multiplicateur de 2,10×, l'industrie manufacturière génère de forts effets indirects car elle achète des intrants à de nombreux autres secteurs (matières premières, énergie, services, transport), créant des emplois dans toute la chaîne de valeur.")
    ]
  },
  {
    "code": "D", "slug": "energie",
    "label": "Production et distribution d'énergie",
    "short": "Énergie",
    "emoji": "⚡",
    "nb_entreprises": "42 764", "nb_emplois": "222 376",
    "ca_cumule": "240 Md€", "pib_pct": "2,5",
    "source_nb": "INSEE ESANE 2023",
    "hero_sub": "Le secteur énergétique français, dominé par le nucléaire et les énergies renouvelables, est un pilier stratégique. Forte intensité capitalistique, faible intensité en main-d'œuvre, mais un taux de valeur ajoutée parmi les plus élevés de l'économie.",
    "content_intro": "Le secteur de la production et distribution d'énergie en France compte 42 764 entreprises et 222 376 salariés en EQTP (INSEE ESANE 2023). Dominé par les grands acteurs du nucléaire, de l'hydroélectrique et des énergies renouvelables, ce secteur génère un chiffre d'affaires cumulé de 240 milliards d'euros.",
    "content_direct": "Avec un taux de valeur ajoutée exceptionnel de 71,6 % du chiffre d'affaires, le secteur énergétique est l'un des plus productifs. Les contributions fiscales sont élevées (12,6 % de la VA), tandis que la part des salaires est très faible, reflétant l'intensité capitalistique du secteur.",
    "content_indirect": "Le secteur énergétique approvisionne l'ensemble de l'économie. Ses achats intermédiaires se concentrent sur la construction (maintenance des infrastructures), l'industrie manufacturière (équipements) et les services spécialisés (ingénierie, conseil).",
    "content_induced": "Bien que le nombre d'emplois directs soit limité, les salaires du secteur énergétique sont parmi les plus élevés de l'économie, générant un effet induit significatif par employé.",
    "faq": [
      ("Quel est le taux de valeur ajoutée du secteur énergétique ?", "Le secteur énergétique affiche un taux de valeur ajoutée de 71,6 % du chiffre d'affaires, l'un des plus élevés de l'économie française, grâce à la forte intensité capitalistique et aux marges élevées de la production d'énergie."),
      ("Combien d'emplois par million d'euros dans le secteur énergie ?", "Le secteur énergétique génère environ 3,2 emplois par million d'euros de chiffre d'affaires, le ratio le plus faible de l'économie, en raison de sa forte intensité capitalistique et de sa productivité élevée par salarié."),
      ("Comment est calculé l'impact territorial d'un producteur d'énergie ?", "Le simulateur IN France prend en compte les spécificités du secteur énergétique : fort taux de VA (71,6 %), contributions fiscales élevées (12,6 %), et effets indirects via la matrice Leontief OCDE pour quantifier l'impact sur l'ensemble de l'économie.")
    ]
  },
  {
    "code": "E", "slug": "eau-dechets",
    "label": "Eau, assainissement et gestion des déchets",
    "short": "Eau et déchets",
    "emoji": "♻️",
    "nb_entreprises": "12 594", "nb_emplois": "196 821",
    "ca_cumule": "51,9 Md€", "pib_pct": "0,8",
    "source_nb": "INSEE ESANE 2023",
    "hero_sub": "Le secteur de l'eau et des déchets est au cœur de la transition écologique. Services essentiels aux collectivités et aux entreprises, ces activités combinent enjeux environnementaux et impact économique territorial significatif.",
    "content_intro": "Le secteur de l'eau, de l'assainissement et de la gestion des déchets en France regroupe 12 594 entreprises et 196 821 salariés en EQTP, pour un chiffre d'affaires de 51,9 milliards d'euros (INSEE ESANE 2023). Ce secteur essentiel assure la distribution d'eau potable, le traitement des eaux usées et la collecte, le tri et le recyclage des déchets.",
    "content_direct": "Le taux de valeur ajoutée atteint 36,1 % du chiffre d'affaires. La part des salaires (62,2 % de la VA) reflète l'intensité en main-d'œuvre des activités de collecte et de traitement. Les contributions fiscales représentent 5,8 % de la valeur ajoutée.",
    "content_indirect": "Le secteur eau et déchets active la construction (infrastructures de traitement), l'industrie manufacturière (équipements), les transports (collecte) et les services spécialisés (ingénierie environnementale).",
    "content_induced": "Les 180 000 emplois du secteur, répartis sur l'ensemble du territoire y compris en zones rurales, génèrent un effet induit local important par la consommation des ménages des salariés.",
    "faq": [
      ("Combien d'emplois le secteur eau et déchets crée-t-il ?", "Le secteur de l'eau et des déchets emploie directement 180 000 personnes en France. Avec un multiplicateur de 1,75×, il soutient environ 315 000 emplois au total dans l'économie."),
      ("Quel est le multiplicateur d'emploi du secteur eau et déchets ?", "Le multiplicateur d'emploi du secteur est de 1,75×, proche de la moyenne nationale (1,82×). Pour chaque emploi direct, 0,75 emploi supplémentaire est généré dans l'économie."),
      ("Comment le secteur eau et déchets contribue-t-il à l'économie locale ?", "Ce secteur est fortement ancré localement : les emplois ne sont pas délocalisables, les achats intermédiaires bénéficient souvent aux entreprises du territoire, et les salaires versés alimentent la consommation locale.")
    ]
  },
  {
    "code": "F", "slug": "construction",
    "label": "Construction",
    "short": "Construction",
    "emoji": "🏗️",
    "nb_entreprises": "587 898", "nb_emplois": "1 594 836",
    "ca_cumule": "405 Md€", "pib_pct": "5,5",
    "source_nb": "INSEE ESANE 2023",
    "hero_sub": "La construction est le secteur avec le plus fort multiplicateur d'emploi en France. Chaque chantier déclenche une chaîne de sous-traitance, d'achats de matériaux et de services qui irrigue l'ensemble de l'économie locale.",
    "content_intro": "Le secteur de la construction en France compte 587 898 entreprises, dont une majorité d'artisans et de PME, et emploie 1 594 836 salariés en EQTP (INSEE ESANE 2023). Avec 405 milliards d'euros de chiffre d'affaires, il représente 5,5 % du PIB français.",
    "content_direct": "Le taux de valeur ajoutée atteint 39,2 % du CA. La part des salaires est très élevée (78,1 % de la VA), reflétant l'intensité en main-d'œuvre du secteur. Les contributions fiscales représentent 4,4 % de la VA, un niveau modéré.",
    "content_indirect": "La construction est le secteur le plus multiplicateur de l'économie française. Elle active massivement l'industrie manufacturière (matériaux de construction, métallurgie), le commerce (négoce de matériaux), les services spécialisés (architectes, ingénieurs) et les transports.",
    "content_induced": "Avec 1,6 million d'emplois souvent locaux et non délocalisables, l'effet induit de la construction est considérable. Les salaires versés alimentent directement l'économie des territoires où les chantiers se déroulent.",
    "faq": [
      ("Pourquoi la construction a-t-elle le plus fort multiplicateur d'emploi ?", "Avec un multiplicateur de 2,25× (le plus élevé de tous les secteurs), la construction génère 1,25 emploi supplémentaire pour chaque emploi direct. Cela s'explique par une chaîne de sous-traitance très longue et diversifiée, mobilisant de nombreux secteurs fournisseurs."),
      ("Combien d'emplois la construction soutient-elle en France ?", "La construction emploie directement 1,6 million de personnes. Grâce à son multiplicateur de 2,25×, elle soutient au total environ 3,6 millions d'emplois dans l'économie française, soit plus de 12 % de l'emploi total."),
      ("Comment mesurer l'impact territorial d'une entreprise du BTP ?", "Notre simulateur calcule les trois couches d'impact d'une entreprise du BTP : emplois et VA directs, effets indirects via la chaîne d'approvisionnement (matériaux, sous-traitance), et effets induits par la consommation des salariés. Il suffit d'entrer le SIREN et le chiffre d'affaires.")
    ]
  },
  {
    "code": "G", "slug": "commerce",
    "label": "Commerce, réparation automobile et motocycle",
    "short": "Commerce",
    "emoji": "🛒",
    "nb_entreprises": "739 128", "nb_emplois": "3 041 393",
    "ca_cumule": "1 728 Md€", "pib_pct": "10,0",
    "source_nb": "INSEE ESANE 2023",
    "hero_sub": "Le commerce est le premier employeur privé de France. Du commerce de gros au détail, en passant par la réparation automobile, ce secteur irrigue l'ensemble du territoire et constitue le lien entre production et consommation.",
    "content_intro": "Le secteur du commerce en France regroupe 739 128 entreprises et emploie 3 041 393 salariés en EQTP, ce qui en fait le premier employeur privé du pays (INSEE ESANE 2023). Avec un chiffre d'affaires cumulé de 1 728 milliards d'euros, il représente environ 10 % du PIB français.",
    "content_direct": "Le taux de valeur ajoutée est de 20,2 % du CA, le plus faible de tous les secteurs, car le commerce est essentiellement une activité d'intermédiation. La part des salaires atteint 70 % de la VA, et les contributions fiscales 7,0 %.",
    "content_indirect": "Le commerce active principalement les transports et la logistique, l'industrie manufacturière (via les achats de marchandises), l'immobilier (surfaces commerciales) et les services administratifs (intérim, nettoyage).",
    "content_induced": "Avec 3,1 millions d'emplois répartis sur tout le territoire, l'effet induit du commerce est massif. Les salariés du secteur consomment localement, alimentant un cercle vertueux pour l'économie des centres-villes et des zones commerciales.",
    "faq": [
      ("Combien d'emplois le commerce représente-t-il en France ?", "Le commerce emploie directement 3,1 millions de personnes en France, ce qui en fait le premier employeur privé. Avec un multiplicateur de 1,95×, il soutient environ 6 millions d'emplois au total dans l'économie."),
      ("Pourquoi le taux de valeur ajoutée du commerce est-il faible ?", "Le commerce affiche un taux de VA de 20,2 % du CA, le plus bas de tous les secteurs, car il s'agit principalement d'une activité d'intermédiation : la majeure partie du CA correspond au coût d'achat des marchandises revendues."),
      ("Comment simuler l'impact d'un commerce sur son territoire ?", "Le simulateur IN France calcule l'impact territorial complet d'un commerce : emplois directs et indirects, valeur ajoutée, contributions fiscales, et effets induits par la consommation des salariés. Entrez simplement le SIREN et le chiffre d'affaires.")
    ]
  },
  {
    "code": "H", "slug": "transports",
    "label": "Transports et entreposage",
    "short": "Transports",
    "emoji": "🚛",
    "nb_entreprises": "193 101", "nb_emplois": "1 287 643",
    "ca_cumule": "267 Md€", "pib_pct": "4,5",
    "source_nb": "INSEE ESANE 2023",
    "hero_sub": "Le transport et la logistique sont les artères de l'économie française. Routier, ferroviaire, aérien ou maritime, ce secteur assure la circulation des marchandises et des personnes, connectant producteurs et consommateurs.",
    "content_intro": "Le secteur des transports et de l'entreposage en France compte 193 101 entreprises et emploie 1 287 643 salariés en EQTP (INSEE ESANE 2023). Avec un chiffre d'affaires de 267 milliards d'euros, il représente 4,5 % du PIB et constitue un maillon essentiel de toutes les chaînes de valeur.",
    "content_direct": "Le taux de valeur ajoutée atteint 43,2 % du CA. La part des salaires est élevée (76,4 % de la VA), reflétant l'importance du facteur humain dans les activités de transport. Les contributions fiscales s'élèvent à 3,8 % de la VA.",
    "content_indirect": "Le transport active principalement l'énergie (carburants), l'industrie manufacturière (véhicules, pièces détachées), les services spécialisés (maintenance, ingénierie) et l'immobilier (entrepôts, plateformes logistiques).",
    "content_induced": "Avec 1,4 million d'emplois répartis sur tout le territoire, des zones portuaires aux plateformes logistiques périurbaines, l'effet induit du transport est considérable et fortement ancré localement.",
    "faq": [
      ("Quel est le multiplicateur d'emploi du secteur transport ?", "Le multiplicateur d'emploi du transport est de 1,88×. Pour chaque emploi direct dans le transport, 0,88 emploi supplémentaire est créé dans l'économie via les achats intermédiaires et la consommation des salariés."),
      ("Combien d'emplois le transport génère-t-il en France ?", "Le secteur transport emploie directement 1,4 million de personnes. Avec son multiplicateur de 1,88×, il soutient environ 2,6 millions d'emplois au total dans l'économie française."),
      ("Comment mesurer l'impact d'une entreprise de transport ?", "Le simulateur IN France prend en compte les spécificités du secteur transport : forte intensité en main-d'œuvre (76,4 % de la VA en salaires), achats d'énergie, et effets d'entraînement sur la logistique et la maintenance.")
    ]
  },
  {
    "code": "I", "slug": "hebergement-restauration",
    "label": "Hébergement et restauration",
    "short": "Hébergement et restauration",
    "emoji": "🍽️",
    "nb_entreprises": "295 456", "nb_emplois": "1 060 329",
    "ca_cumule": "135,7 Md€", "pib_pct": "2,8",
    "source_nb": "INSEE ESANE 2023",
    "hero_sub": "L'hôtellerie-restauration est le secteur le plus intensif en emplois de l'économie française : 26 emplois par million d'euros de CA. Un ancrage territorial fort qui fait vivre les centres-villes, les stations touristiques et les zones rurales.",
    "content_intro": "Le secteur de l'hébergement et de la restauration en France compte 295 456 établissements et emploie 1 060 329 salariés en EQTP (INSEE ESANE 2023). Avec un chiffre d'affaires de 135,7 milliards d'euros, il est le secteur le plus créateur d'emplois par euro de chiffre d'affaires.",
    "content_direct": "Le taux de valeur ajoutée est élevé (48,7 % du CA). La part des salaires atteint 73,1 % de la VA, reflétant l'intensité en main-d'œuvre du secteur. Avec 26 emplois par million d'euros de CA, c'est le ratio le plus élevé de l'économie.",
    "content_indirect": "L'hôtellerie-restauration active fortement l'agriculture et l'agroalimentaire (approvisionnement), le commerce (fournitures), l'immobilier (locaux) et les services de nettoyage et d'entretien.",
    "content_induced": "Les 1,1 million de salariés du secteur consomment localement, renforçant l'économie des territoires touristiques et des centres urbains. L'effet induit est d'autant plus important que ces emplois sont non délocalisables.",
    "faq": [
      ("Pourquoi la restauration crée-t-elle autant d'emplois ?", "Avec 26 emplois par million d'euros de CA, l'hébergement-restauration est le secteur le plus intensif en main-d'œuvre. Cela s'explique par la nature du service (préparation, service en salle, accueil) qui nécessite beaucoup de personnel."),
      ("Quel est l'impact économique d'un restaurant sur son quartier ?", "Un restaurant génère un multiplicateur d'emploi de 2,05×. Au-delà de ses emplois directs, il active ses fournisseurs (agriculteurs, grossistes) et ses salariés consomment localement, irriguant l'économie du quartier."),
      ("Comment calculer l'impact territorial d'un hôtel ou restaurant ?", "Le simulateur IN France calcule l'impact complet : emplois directs (très nombreux dans ce secteur), effets indirects sur l'agroalimentaire et le commerce, et effets induits par la consommation des 1,1 million de salariés du secteur.")
    ]
  },
  {
    "code": "J", "slug": "information-communication",
    "label": "Information et communication",
    "short": "Information et communication",
    "emoji": "💻",
    "nb_entreprises": "218 069", "nb_emplois": "951 374",
    "ca_cumule": "270 Md€", "pib_pct": "5,0",
    "source_nb": "INSEE ESANE 2023",
    "hero_sub": "Le secteur numérique est le moteur de la transformation de l'économie française. Édition de logiciels, télécoms, conseil IT, production audiovisuelle : un secteur à forte valeur ajoutée qui irrigue tous les autres.",
    "content_intro": "Le secteur de l'information et de la communication en France regroupe 218 069 entreprises et 951 374 salariés en EQTP (INSEE ESANE 2023). Avec un chiffre d'affaires de 270 milliards d'euros et une croissance soutenue, il représente environ 5 % du PIB français et constitue un secteur stratégique pour la compétitivité nationale.",
    "content_direct": "Le taux de valeur ajoutée est très élevé (53 % du CA), reflétant la forte composante intellectuelle et technologique. La part des salaires atteint 79,1 % de la VA, la plus élevée après la construction, car la valeur est créée par les talents. Les contributions fiscales sont modérées (2,9 %).",
    "content_indirect": "Le secteur IT active principalement les services spécialisés (conseil, sous-traitance), l'immobilier (bureaux), l'énergie (data centers) et les télécommunications. Son coefficient d'impact indirect est de 28 %, inférieur à la moyenne, car c'est un secteur très « amont ».",
    "content_induced": "Avec des salaires parmi les plus élevés de l'économie, les 850 000 employés du secteur génèrent un effet induit par tête très supérieur à la moyenne. Leurs dépenses de consommation (logement, loisirs, restauration) irriguent fortement l'économie urbaine.",
    "faq": [
      ("Combien d'emplois le secteur numérique crée-t-il en France ?", "Le secteur de l'information et communication emploie 850 000 personnes directement. Avec un multiplicateur de 1,65×, il soutient environ 1,4 million d'emplois au total. Le ratio est de 9,5 emplois par million d'euros de CA, reflétant la haute productivité du secteur."),
      ("Quel est le taux de valeur ajoutée du secteur IT ?", "Le secteur affiche un taux de VA de 53 % du CA, bien supérieur à la moyenne nationale (32,1 %). Cela s'explique par la faible consommation de matières premières et la forte composante intellectuelle de la production."),
      ("Comment mesurer l'impact territorial d'une entreprise tech ?", "Notre simulateur prend en compte les spécificités du secteur IT : fort taux de VA, salaires élevés, et structure d'achats intermédiaires orientée vers les services. L'impact territorial d'une ESN ou d'un éditeur de logiciel se manifeste principalement par les salaires et la consommation de ses employés.")
    ]
  },
  {
    "code": "K", "slug": "finance-assurance",
    "label": "Activités financières et d'assurance",
    "short": "Finance et assurance",
    "emoji": "🏦",
    "nb_entreprises": "270 000", "nb_emplois": "860 000",
    "ca_cumule": "", "pib_pct": "3,8",
    "source_nb": "INSEE SIDE · Flores 2023 (est.)",
    "hero_sub": "Le secteur financier est un pilier de l'économie française, avec un taux de valeur ajoutée parmi les plus élevés. Banques, assurances, fintech : un secteur à forte productivité qui finance l'ensemble de l'économie réelle.",
    "content_intro": "Le secteur des activités financières et d'assurance en France regroupe environ 270 000 unités légales et emploie quelque 860 000 personnes (INSEE SIDE · Flores 2023). Il constitue un rouage essentiel de l'économie, finançant l'investissement et couvrant les risques des entreprises et des ménages.",
    "content_direct": "Le taux de valeur ajoutée est exceptionnel (82 % du CA), car le secteur financier transforme peu de matières premières. La part des salaires représente 38 % de la VA, et les contributions fiscales 18 %, un niveau élevé reflétant la forte rentabilité du secteur.",
    "content_indirect": "Le secteur financier active principalement les services spécialisés (conseil, audit, juridique), l'information et communication (systèmes IT), l'immobilier (sièges et agences) et les services administratifs.",
    "content_induced": "Avec des salaires parmi les plus élevés de l'économie, les employés du secteur financier génèrent un fort effet induit. Leurs dépenses de consommation sont supérieures à la moyenne, irriguant l'économie locale, en particulier dans les grandes métropoles.",
    "faq": [
      ("Quel est le multiplicateur d'emploi du secteur financier ?", "Le multiplicateur d'emploi du secteur financier est de 1,42×, l'un des plus faibles de l'économie. Cela s'explique par la forte productivité par salarié et le faible recours à la sous-traitance industrielle."),
      ("Combien d'emplois par million d'euros dans la finance ?", "Le secteur financier génère 5 emplois par million d'euros de CA, un ratio bas qui reflète la haute productivité et la forte intensité capitalistique du secteur. En contrepartie, la valeur ajoutée par emploi est très élevée."),
      ("Comment est calculé l'impact territorial d'une banque ?", "Le simulateur IN France utilise les benchmarks spécifiques au secteur K (finance) pour calculer l'impact : fort taux de VA (82 %), contributions fiscales élevées (18 %), et effets indirects principalement orientés vers les services et l'IT.")
    ]
  },
  {
    "code": "L", "slug": "immobilier",
    "label": "Activités immobilières",
    "short": "Immobilier",
    "emoji": "🏢",
    "nb_entreprises": "280 103", "nb_emplois": "244 676",
    "ca_cumule": "94,4 Md€", "pib_pct": "12,5",
    "source_nb": "INSEE ESANE 2023",
    "hero_sub": "L'immobilier est le secteur à la plus forte valeur ajoutée relative de l'économie. Gestion locative, promotion, agences : un secteur qui pèse lourd dans le PIB français malgré un nombre d'emplois directs limité.",
    "content_intro": "Le secteur des activités immobilières en France regroupe 280 103 entreprises et emploie 244 676 salariés en EQTP, pour un chiffre d'affaires de 94,4 milliards d'euros (INSEE ESANE 2023). Avec un poids dans le PIB d'environ 12,5 % (en incluant les loyers imputés), c'est l'un des secteurs les plus importants de l'économie, bien que son nombre d'emplois directs soit relativement limité.",
    "content_direct": "Le taux de valeur ajoutée est le plus élevé de l'économie (71,2 % du CA hors loyers imputés). La part des salaires est très faible (8,2 % de la VA), car la valeur est principalement captée par le capital immobilier. Les contributions fiscales atteignent 11,6 % de la VA.",
    "content_indirect": "L'immobilier active la construction (entretien, rénovation), les services spécialisés (notaires, architectes, géomètres), les services administratifs (syndics, gestion) et le secteur financier (prêts, assurances).",
    "content_induced": "Malgré un faible nombre d'emplois directs, le secteur immobilier génère des revenus locatifs qui alimentent l'investissement immobilier et la construction, créant un effet multiplicateur indirect significatif.",
    "faq": [
      ("Pourquoi l'immobilier a-t-il un faible multiplicateur d'emploi ?", "Le multiplicateur d'emploi de l'immobilier est de 1,38×, le plus faible de l'économie. Cela s'explique par la nature capitalistique du secteur : la valeur est principalement générée par les actifs immobiliers, avec très peu de main-d'œuvre directe (8,2 % de la VA en salaires)."),
      ("Quel est le poids de l'immobilier dans l'économie française ?", "L'immobilier représente environ 12,5 % du PIB français en incluant les loyers imputés, ce qui en fait l'un des plus gros secteurs. Il génère 95 milliards d'euros de chiffre d'affaires via 200 000 entreprises."),
      ("Comment mesurer l'impact territorial d'une agence immobilière ?", "Le simulateur IN France calcule l'impact spécifique d'une entreprise immobilière : forte valeur ajoutée, faible intensité en main-d'œuvre, et effets indirects orientés vers la construction, les services juridiques et la finance.")
    ]
  },
  {
    "code": "M", "slug": "services-specialises",
    "label": "Activités spécialisées, scientifiques et techniques",
    "short": "Services spécialisés",
    "emoji": "🔬",
    "nb_entreprises": "700 000", "nb_emplois": "1 720 000",
    "ca_cumule": "265 Md€", "pib_pct": "7,0",
    "source_nb": "INSEE ESANE 2023 (est. section M)",
    "hero_sub": "Conseil, ingénierie, R&D, comptabilité, juridique, publicité : les services spécialisés sont le système nerveux de l'économie. Un secteur à forte valeur ajoutée porté par les compétences et l'expertise.",
    "content_intro": "Le secteur des activités spécialisées, scientifiques et techniques regroupe environ 700 000 entreprises et 1 720 000 salariés en EQTP en France (INSEE ESANE 2023, estimation section M). Avec un chiffre d'affaires de 265 milliards d'euros, il englobe le conseil en management, l'ingénierie, la R&D, la comptabilité, le juridique, la publicité et le design.",
    "content_direct": "Le taux de valeur ajoutée est élevé (60,2 % du CA), car ces activités reposent principalement sur le capital humain. La part des salaires atteint 79,8 % de la VA, la plus élevée de l'économie, confirmant que la valeur est créée par les talents.",
    "content_indirect": "Les services spécialisés sont eux-mêmes des fournisseurs clés de tous les autres secteurs. Leurs propres achats intermédiaires se concentrent sur l'IT, l'immobilier (bureaux), les services administratifs et les télécommunications.",
    "content_induced": "Avec 1,5 million d'emplois qualifiés et des salaires supérieurs à la moyenne, l'effet induit du secteur est significatif. Les employés des cabinets de conseil, d'ingénierie et de R&D contribuent fortement à l'économie des métropoles.",
    "faq": [
      ("Combien d'emplois les services spécialisés créent-ils ?", "Les activités spécialisées emploient directement 1,5 million de personnes en France. Avec un multiplicateur de 1,72×, elles soutiennent environ 2,6 millions d'emplois au total dans l'économie."),
      ("Pourquoi la part des salaires est-elle si élevée dans ce secteur ?", "Avec 79,8 % de la valeur ajoutée consacrée aux salaires, ce secteur est le plus intensif en capital humain. La valeur créée repose quasi exclusivement sur les compétences et l'expertise des collaborateurs, avec très peu de consommation de matières premières."),
      ("Comment mesurer l'impact d'un cabinet de conseil ?", "Le simulateur IN France calcule l'impact territorial d'un cabinet de conseil en prenant en compte sa forte valeur ajoutée (60,2 % du CA), l'intensité en emplois qualifiés, et les effets indirects et induits générés par ses achats et les dépenses de ses salariés.")
    ]
  },
  {
    "code": "N", "slug": "services-administratifs",
    "label": "Services administratifs et de soutien",
    "short": "Services administratifs",
    "emoji": "📋",
    "nb_entreprises": "342 000", "nb_emplois": "1 199 000",
    "ca_cumule": "166 Md€", "pib_pct": "3,5",
    "source_nb": "INSEE ESANE 2023 (est. section N)",
    "hero_sub": "Intérim, nettoyage, sécurité, location, centres d'appels : les services de soutien emploient 1,2 million de personnes. Un secteur à forte intensité en main-d'œuvre, essentiel au fonctionnement de toutes les autres entreprises.",
    "content_intro": "Le secteur des services administratifs et de soutien en France regroupe environ 342 000 entreprises et emploie 1 199 000 salariés en EQTP, pour un chiffre d'affaires de 166 milliards d'euros (INSEE ESANE 2023, estimation section N). Il englobe le travail temporaire (intérim), le nettoyage industriel, la sécurité privée, la location de matériel et les centres d'appels.",
    "content_direct": "Le taux de valeur ajoutée atteint 63,7 % du CA. La part des salaires est la deuxième plus élevée de l'économie (85,3 % de la VA), car ces activités sont quasi exclusivement basées sur la main-d'œuvre. Les contributions fiscales représentent 3,5 %.",
    "content_indirect": "Les services administratifs activent principalement les transports, l'immobilier, les services spécialisés et l'information-communication. L'impact indirect est de 38 %, dans la moyenne nationale.",
    "content_induced": "Avec 1,8 million d'emplois souvent peu qualifiés mais essentiels, l'effet induit est important en volume. Ces emplois sont répartis sur tout le territoire et non délocalisables, renforçant l'économie locale des bassins d'emploi.",
    "faq": [
      ("Combien d'emplois les services de soutien génèrent-ils ?", "Les services administratifs emploient directement 1,8 million de personnes, ce qui en fait le deuxième employeur privé après le commerce. Avec un multiplicateur de 2,00×, ils soutiennent 3,6 millions d'emplois au total."),
      ("Quel est le ratio emplois par million d'euros dans ce secteur ?", "Le secteur génère 22 emplois par million d'euros de CA, le deuxième ratio le plus élevé après l'hébergement-restauration (26). Cela reflète la forte intensité en main-d'œuvre et les salaires relativement modérés du secteur."),
      ("Comment ce secteur contribue-t-il à l'économie territoriale ?", "Les services de soutien sont essentiels pour l'économie locale : emplois non délocalisables, répartis sur tout le territoire, et consommation des salariés qui irrigue les commerces et services de proximité.")
    ]
  },
  {
    "code": "O", "slug": "administration-publique",
    "label": "Administration publique",
    "short": "Administration publique",
    "emoji": "🏛️",
    "nb_entreprises": "", "nb_emplois": "5 832 600",
    "ca_cumule": "", "pib_pct": "18,0",
    "source_nb": "INSEE Première n°2052, 2023",
    "hero_sub": "L'administration publique est le premier employeur de France. État, collectivités territoriales, hôpitaux publics : un secteur dont l'impact territorial est structurant pour l'ensemble de l'économie.",
    "content_intro": "L'administration publique française emploie 5 832 600 agents répartis entre la fonction publique d'État (2 573 900), la fonction publique territoriale (2 017 800) et la fonction publique hospitalière (1 240 900), selon l'INSEE Première n°2052 (données fin 2023). C'est le premier employeur du pays.",
    "content_direct": "Le taux de valeur ajoutée est très élevé (95 % du CA), car l'administration publique produit principalement des services non marchands. La part des salaires atteint 78 % de la VA, et les contributions fiscales 20 %.",
    "content_indirect": "L'administration publique est le premier acheteur de l'économie française via la commande publique. Elle active la construction (infrastructures), les services spécialisés (conseil, ingénierie), l'industrie manufacturière (équipements) et les services informatiques.",
    "content_induced": "Avec 5,6 millions d'emplois répartis sur tout le territoire, l'effet induit de l'administration publique est considérable. Les fonctionnaires constituent souvent le pilier économique des petites villes et des zones rurales.",
    "faq": [
      ("Combien d'emplois l'administration publique représente-t-elle ?", "L'administration publique emploie 5,6 millions de personnes en France, soit environ 20 % de l'emploi total. C'est le premier employeur du pays, avec une présence sur l'ensemble du territoire."),
      ("Quel est le multiplicateur d'emploi de l'administration publique ?", "Le multiplicateur est de 1,80×, proche de la moyenne nationale. Pour chaque emploi public, 0,80 emploi supplémentaire est généré dans l'économie via la commande publique et la consommation des fonctionnaires."),
      ("Comment mesurer l'impact d'un organisme public sur son territoire ?", "Le simulateur IN France peut estimer l'impact territorial d'un organisme public en prenant en compte ses effectifs, sa masse salariale, ses achats de biens et services, et l'effet induit par la consommation de ses agents sur l'économie locale.")
    ]
  },
  {
    "code": "P", "slug": "enseignement",
    "label": "Enseignement",
    "short": "Enseignement",
    "emoji": "🎓",
    "nb_entreprises": "210 000", "nb_emplois": "115 000",
    "ca_cumule": "18 Md€", "pib_pct": "5,0",
    "source_nb": "INSEE ESANE 2023 (est. section P, privé marchand)",
    "hero_sub": "L'enseignement, public et privé, emploie plus d'un million de personnes en France. Un secteur à très forte intensité en main-d'œuvre dont l'impact va bien au-delà de la formation : il structure l'économie des territoires.",
    "content_intro": "Le secteur privé marchand de l'enseignement en France regroupe environ 210 000 entreprises et emploie 115 000 salariés en EQTP, pour un chiffre d'affaires de 18 milliards d'euros (INSEE ESANE 2023, estimation section P). L'enseignement public, comptabilisé dans l'administration publique (section O), emploie en complément plus d'un million d'agents.",
    "content_direct": "Le taux de valeur ajoutée est très élevé (92 % du CA), car l'enseignement est une activité de service pur. La part des salaires atteint 80 % de la VA, la plus élevée de tous les secteurs. Les contributions fiscales représentent 12 %.",
    "content_indirect": "L'enseignement active principalement l'immobilier (locaux), les services spécialisés (édition, recherche), l'information-communication (logiciels éducatifs, plateformes) et la restauration collective.",
    "content_induced": "Les 1,8 million d'emplois du secteur génèrent un effet induit massif. Dans de nombreuses villes moyennes, les établissements d'enseignement sont le premier employeur local et leurs salariés le premier moteur de la consommation.",
    "faq": [
      ("Combien d'emplois l'enseignement soutient-il en France ?", "L'enseignement emploie directement 1,8 million de personnes. Avec un multiplicateur de 1,85×, il soutient environ 3,3 millions d'emplois au total dans l'économie française."),
      ("Pourquoi l'enseignement a-t-il la plus forte part de salaires ?", "Avec 80 % de la valeur ajoutée consacrée aux salaires, l'enseignement est le secteur le plus intensif en main-d'œuvre. La quasi-totalité de la valeur est produite par les enseignants et personnels, avec très peu d'intrants matériels."),
      ("Quel est l'impact d'une université sur son territoire ?", "Une université est souvent le premier employeur de sa ville. Le simulateur IN France mesure l'impact total : emplois directs, achats auprès des fournisseurs locaux, et effet induit par les dépenses des 1,8 million de salariés du secteur et des étudiants.")
    ]
  },
  {
    "code": "Q", "slug": "sante",
    "label": "Santé humaine et action sociale",
    "short": "Santé et social",
    "emoji": "🏥",
    "nb_entreprises": "586 000", "nb_emplois": "669 000",
    "ca_cumule": "125 Md€", "pib_pct": "8,5",
    "source_nb": "INSEE ESANE 2023 (est. section Q, privé marchand)",
    "hero_sub": "La santé et l'action sociale représentent le deuxième employeur national. Hôpitaux, cliniques, EHPAD, aide à domicile : un secteur essentiel dont l'impact territorial est considérable.",
    "content_intro": "Le secteur privé marchand de la santé humaine et de l'action sociale en France regroupe environ 586 000 établissements et emploie 669 000 salariés en EQTP, pour un chiffre d'affaires de 125 milliards d'euros (INSEE ESANE 2023, estimation section Q). Le secteur public hospitalier, comptabilisé dans la fonction publique, emploie en complément 1 240 900 agents.",
    "content_direct": "Le taux de valeur ajoutée est élevé (67,6 % du CA). La part des salaires atteint 77,9 % de la VA, reflétant l'intensité en personnel soignant et social. Les contributions fiscales représentent 7,6 % de la VA.",
    "content_indirect": "La santé active l'industrie pharmaceutique et les dispositifs médicaux (industrie manufacturière), les services spécialisés (recherche, conseil), la construction (bâtiments hospitaliers) et les services administratifs (sous-traitance).",
    "content_induced": "Avec 3,9 millions d'emplois répartis sur tout le territoire, l'effet induit de la santé est parmi les plus importants. Les personnels de santé et du social sont souvent les piliers économiques des villes moyennes et des zones rurales.",
    "faq": [
      ("Combien d'emplois le secteur santé génère-t-il en France ?", "Le secteur santé et social emploie directement 3,9 millions de personnes, le deuxième effectif national. Avec un multiplicateur de 2,02×, il soutient environ 7,9 millions d'emplois au total dans l'économie."),
      ("Quel est le multiplicateur d'emploi de la santé ?", "Le multiplicateur est de 2,02×, supérieur à la moyenne nationale (1,82×). Pour chaque emploi dans la santé, un emploi supplémentaire est créé via les achats de médicaments, d'équipements et la consommation des soignants."),
      ("Comment mesurer l'impact d'un hôpital sur son territoire ?", "Le simulateur IN France calcule l'impact complet d'un établissement de santé : emplois directs (soignants, administratifs), effets indirects (pharmacie, équipements médicaux, construction), et effets induits par la consommation des milliers de salariés.")
    ]
  },
  {
    "code": "R", "slug": "arts-loisirs",
    "label": "Arts, spectacles et activités récréatives",
    "short": "Arts et loisirs",
    "emoji": "🎭",
    "nb_entreprises": "183 000", "nb_emplois": "105 000",
    "ca_cumule": "22 Md€", "pib_pct": "1,2",
    "source_nb": "INSEE ESANE 2023 (est. section R)",
    "hero_sub": "Spectacle vivant, cinéma, sport, parcs de loisirs, musées : le secteur culturel et récréatif anime les territoires et attire les touristes. Un fort multiplicateur d'emploi porté par l'intensité en main-d'œuvre.",
    "content_intro": "Le secteur des arts, spectacles et activités récréatives en France regroupe environ 183 000 entreprises et emploie 105 000 salariés en EQTP, pour un chiffre d'affaires de 22 milliards d'euros (INSEE ESANE 2023, estimation section R). Il englobe le spectacle vivant, le cinéma, le sport professionnel, les parcs de loisirs et les musées.",
    "content_direct": "Le taux de valeur ajoutée atteint 50,4 % du CA. La part des salaires représente 64,7 % de la VA. Le secteur génère 21 emplois par million d'euros de CA, un ratio élevé qui reflète l'intensité en main-d'œuvre des activités culturelles et récréatives.",
    "content_indirect": "Le secteur culturel active l'hébergement-restauration (tourisme), le commerce (billetterie, merchandising), les services spécialisés (production, communication) et les transports (déplacements du public).",
    "content_induced": "Les 400 000 emplois du secteur, concentrés dans les grandes villes et les zones touristiques, génèrent un effet induit local. De plus, les activités culturelles et récréatives attirent des visiteurs dont les dépenses (hébergement, restauration, commerce) amplifient l'impact économique.",
    "faq": [
      ("Combien d'emplois le secteur culturel crée-t-il ?", "Le secteur des arts et loisirs emploie directement 400 000 personnes (hors intermittents). Avec un multiplicateur de 1,95×, il soutient environ 780 000 emplois au total dans l'économie française."),
      ("Quel est l'impact économique d'un festival ou d'un spectacle ?", "Au-delà des emplois directs, un événement culturel génère des retombées via l'hébergement, la restauration, le transport et le commerce. Le multiplicateur d'emploi du secteur (1,95×) capture ces effets d'entraînement."),
      ("Comment calculer les retombées économiques d'un équipement culturel ?", "Le simulateur IN France mesure l'impact territorial d'un musée, théâtre ou équipement sportif en calculant les emplois directs, les achats aux fournisseurs locaux, et la consommation des salariés et des visiteurs.")
    ]
  },
  {
    "code": "S", "slug": "autres-services",
    "label": "Autres activités de services",
    "short": "Autres services",
    "emoji": "🤝",
    "nb_entreprises": "354 000", "nb_emplois": "284 000",
    "ca_cumule": "44 Md€", "pib_pct": "1,5",
    "source_nb": "INSEE ESANE 2023 (est. section S)",
    "hero_sub": "Associations, réparation, services à la personne, organisations professionnelles : une mosaïque d'activités de proximité qui maillent le territoire et créent du lien social tout en générant un impact économique significatif.",
    "content_intro": "Le secteur des autres activités de services en France regroupe environ 354 000 structures (entreprises, associations, organisations) et emploie 284 000 salariés en EQTP, pour un chiffre d'affaires de 44 milliards d'euros (INSEE ESANE 2023, estimation section S). Il englobe la réparation de biens, les services à la personne, les organisations professionnelles et les activités associatives.",
    "content_direct": "Le taux de valeur ajoutée est de 50,7 % du CA. La part des salaires atteint 77,1 % de la VA. Avec 23 emplois par million d'euros de CA, c'est l'un des secteurs les plus créateurs d'emplois par euro investi.",
    "content_indirect": "Ce secteur active le commerce (pièces détachées pour la réparation), les services spécialisés, les transports et l'immobilier. L'impact indirect est de 36 %, proche de la moyenne nationale.",
    "content_induced": "Les 600 000 emplois du secteur, très ancrés localement et non délocalisables, génèrent un effet induit important pour l'économie de proximité. Les services à la personne et les associations sont souvent les premiers employeurs des zones rurales.",
    "faq": [
      ("Combien d'emplois les services de proximité créent-ils ?", "Les autres services emploient directement 600 000 personnes en France. Avec un multiplicateur de 1,90×, ils soutiennent environ 1,14 million d'emplois au total dans l'économie."),
      ("Quel est le ratio emplois par million d'euros dans ce secteur ?", "Le secteur génère 23 emplois par million d'euros de CA, le troisième ratio le plus élevé de l'économie. Cela reflète l'intensité en main-d'œuvre des activités de service à la personne et de réparation."),
      ("Comment mesurer l'impact d'une association sur son territoire ?", "Le simulateur IN France peut calculer l'impact territorial d'une association ou d'un service de proximité en prenant en compte les emplois créés, les achats aux fournisseurs locaux, et la consommation des salariés.")
    ]
  },
]

# ─── BENCH DATA ──────────────────────────────────────────────────────────────

BENCH_SEC = {
  "A": {"multiplicateur":2.15,"va_sur_ca":28.0,"emplois_par_mca":21.0,"part_salaires":44.0,"part_taxes":10.0,"indirect_pct":40.0},
  "B": {"multiplicateur":1.60,"va_sur_ca":45.0,"emplois_par_mca":10.5,"part_salaires":42.0,"part_taxes":14.0,"indirect_pct":32.0},
  "C": {"multiplicateur":2.10,"va_sur_ca":28.5,"emplois_par_mca":13.8,"part_salaires":58.0,"part_taxes":11.0,"indirect_pct":42.0},
  "D": {"multiplicateur":1.45,"va_sur_ca":72.0,"emplois_par_mca":3.2,"part_salaires":15.0,"part_taxes":28.0,"indirect_pct":25.0},
  "E": {"multiplicateur":1.75,"va_sur_ca":38.0,"emplois_par_mca":13.0,"part_salaires":52.0,"part_taxes":15.0,"indirect_pct":35.0},
  "F": {"multiplicateur":2.25,"va_sur_ca":38.5,"emplois_par_mca":19.5,"part_salaires":68.0,"part_taxes":9.5,"indirect_pct":45.0},
  "G": {"multiplicateur":1.95,"va_sur_ca":22.0,"emplois_par_mca":17.0,"part_salaires":62.0,"part_taxes":11.0,"indirect_pct":38.0},
  "H": {"multiplicateur":1.88,"va_sur_ca":32.0,"emplois_par_mca":16.2,"part_salaires":64.0,"part_taxes":12.0,"indirect_pct":37.0},
  "I": {"multiplicateur":2.05,"va_sur_ca":45.0,"emplois_par_mca":26.0,"part_salaires":72.0,"part_taxes":8.5,"indirect_pct":40.0},
  "J": {"multiplicateur":1.65,"va_sur_ca":62.0,"emplois_par_mca":9.5,"part_salaires":68.0,"part_taxes":10.0,"indirect_pct":28.0},
  "K": {"multiplicateur":1.42,"va_sur_ca":82.0,"emplois_par_mca":5.0,"part_salaires":38.0,"part_taxes":18.0,"indirect_pct":22.0},
  "L": {"multiplicateur":1.38,"va_sur_ca":88.0,"emplois_par_mca":4.5,"part_salaires":18.0,"part_taxes":14.0,"indirect_pct":20.0},
  "M": {"multiplicateur":1.72,"va_sur_ca":55.0,"emplois_par_mca":10.8,"part_salaires":72.0,"part_taxes":10.5,"indirect_pct":33.0},
  "N": {"multiplicateur":2.00,"va_sur_ca":48.0,"emplois_par_mca":22.0,"part_salaires":75.0,"part_taxes":9.0,"indirect_pct":38.0},
  "O": {"multiplicateur":1.80,"va_sur_ca":95.0,"emplois_par_mca":15.0,"part_salaires":78.0,"part_taxes":20.0,"indirect_pct":30.0},
  "P": {"multiplicateur":1.85,"va_sur_ca":92.0,"emplois_par_mca":19.0,"part_salaires":80.0,"part_taxes":12.0,"indirect_pct":32.0},
  "Q": {"multiplicateur":2.02,"va_sur_ca":78.0,"emplois_par_mca":20.0,"part_salaires":76.0,"part_taxes":11.0,"indirect_pct":36.0},
  "R": {"multiplicateur":1.95,"va_sur_ca":50.0,"emplois_par_mca":21.0,"part_salaires":65.0,"part_taxes":10.0,"indirect_pct":37.0},
  "S": {"multiplicateur":1.90,"va_sur_ca":55.0,"emplois_par_mca":23.0,"part_salaires":68.0,"part_taxes":9.5,"indirect_pct":36.0},
}

BENCH_NAT = {"multiplicateur":1.82,"va_sur_ca":32.1,"emplois_par_mca":14.2,"part_salaires":55.4,"part_taxes":12.8,"indirect_pct":38.2}

# Load Leontief matrix for supply chain connections
with open("data/icio/leontief_france_naf.json") as f:
    LEONTIEF = json.load(f)

NAF_LABELS = {
  "A":"Agriculture","B":"Ind. extractives","C":"Industrie manufacturière",
  "D":"Énergie","E":"Eau & déchets","F":"Construction","G":"Commerce",
  "H":"Transports","I":"Héberg. & restauration","J":"Info. & communication",
  "K":"Finance","L":"Immobilier","M":"Services spécialisés",
  "N":"Services admin.","O":"Administration","P":"Enseignement",
  "Q":"Santé & social","R":"Arts & loisirs","S":"Autres services"
}


def get_top_sectors(code, n=5):
    """Get top N connected sectors from Leontief matrix (excluding self)."""
    if code not in LEONTIEF:
        return []
    coeffs = LEONTIEF[code]
    items = [(k, v) for k, v in coeffs.items() if k != code]
    items.sort(key=lambda x: x[1], reverse=True)
    return items[:n]


def bench_comparison(val, ref):
    diff = ((val - ref) / ref) * 100
    sign = "+" if diff >= 0 else ""
    color = "#002395" if diff >= 0 else "#ED2939"
    return f'{sign}{diff:.0f}%'


def generate_dropdown_items():
    """Generate HTML for the sector dropdown menu items."""
    html = ""
    for s in SECTORS:
        html += f'''          <a class="nav-dropdown-item" href="/secteur/{s["slug"]}">
            <span class="nav-dropdown-item-code">{s["code"]}</span>
            <span class="nav-dropdown-item-label">{s["short"]}</span>
          </a>\n'''
    return html


def generate_page(sector):
    code = sector["code"]
    slug = sector["slug"]
    bs = BENCH_SEC[code]
    top_sectors = get_top_sectors(code)

    # Supply chain HTML
    supply_chain_html = ""
    for sc_code, sc_coeff in top_sectors:
        label = NAF_LABELS.get(sc_code, sc_code)
        cents = int(sc_coeff * 100)
        supply_chain_html += f'''
            <div class="sc-item">
              <div class="sc-left">
                <span class="sc-pill">{sc_code}</span>
                <span class="sc-label">{label}</span>
              </div>
              <div class="sc-bar-wrap">
                <div class="sc-bar" style="width:{min(sc_coeff * 300, 100):.0f}%"></div>
              </div>
              <span class="sc-val">{sc_coeff:.3f}</span>
            </div>'''

    # FAQ schema.org
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a}
            }
            for q, a in sector["faq"]
        ]
    }

    # FAQ HTML
    faq_html = ""
    for q, a in sector["faq"]:
        faq_html += f'''
          <div class="faq-item">
            <button class="faq-q" onclick="this.parentElement.classList.toggle('open')">
              <span>{q}</span>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
            </button>
            <div class="faq-a"><p>{a}</p></div>
          </div>'''

    # Bench comparisons
    mult_vs_nat = bench_comparison(bs["multiplicateur"], BENCH_NAT["multiplicateur"])
    va_vs_nat = bench_comparison(bs["va_sur_ca"], BENCH_NAT["va_sur_ca"])
    emp_vs_nat = bench_comparison(bs["emplois_par_mca"], BENCH_NAT["emplois_par_mca"])

    html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<!-- SEO -->
<title>Impact territorial du secteur {sector["short"]} en France | IN France</title>
<meta name="description" content="Calculez l'impact économique de votre entreprise dans le secteur {sector["label"].lower()}. {sector["nb_entreprises"]} entreprises, {sector["nb_emplois"]} emplois, multiplicateur {bs["multiplicateur"]:.2f}×. Simulation gratuite.">
<meta name="keywords" content="impact territorial {sector["short"].lower()}, {sector["label"].lower()} France, multiplicateur emploi {sector["short"].lower()}, valeur ajoutée {sector["short"].lower()}, emplois {sector["short"].lower()} France, simulateur impact {sector["short"].lower()}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://simulateur.in-france.fr/secteur/{slug}">

<!-- Open Graph -->
<meta property="og:type" content="website">
<meta property="og:url" content="https://simulateur.in-france.fr/secteur/{slug}">
<meta property="og:title" content="Impact territorial · {sector["short"]} | IN France">
<meta property="og:description" content="{sector["nb_entreprises"]} entreprises, {sector["nb_emplois"]} emplois, multiplicateur {bs["multiplicateur"]:.2f}×. Simulez l'impact de votre entreprise.">
<meta property="og:image" content="https://simulateur.in-france.fr/og-image.png">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="IN France">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Impact territorial · {sector["short"]} | IN France">
<meta name="twitter:description" content="Simulez l'impact économique de votre entreprise dans le secteur {sector["short"].lower()} : emplois, VA, taxes.">

<!-- Schema.org FAQPage -->
<script type="application/ld+json">
{json.dumps(faq_schema, ensure_ascii=False, indent=2)}
</script>

<!-- Favicon -->
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">

<!-- Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
:root{{--bg:#fff;--fg:#0d1b2a;--card:#fff;--muted:#f3f5f9;--muted-fg:#64748b;--border:#dde3ee;--radius:6px;--fr-blue:#002395;--fr-red:#ED2939;--green:#16a34a}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--fg);font-family:'Geist',-apple-system,sans-serif;font-size:14px;line-height:1.6;-webkit-font-smoothing:antialiased}}

/* Header */
.site-header{{border-bottom:1px solid var(--border);height:52px;display:flex;align-items:center;padding:0 32px;gap:24px;position:sticky;top:0;background:rgba(255,255,255,.94);backdrop-filter:blur(10px);z-index:100}}
.logo{{display:flex;align-items:baseline;gap:5px;text-decoration:none}}
.logo-in{{font-size:16px;font-weight:700;letter-spacing:-.4px;color:var(--fr-blue)}}
.logo-france{{font-size:16px;font-weight:700;letter-spacing:-.4px;color:var(--fr-red)}}
.header-sep{{width:1px;height:18px;background:var(--border)}}
.site-nav{{display:flex;gap:2px}}
.nav-link{{padding:4px 10px;font-size:13px;color:var(--muted-fg);border-radius:4px;text-decoration:none;transition:all .12s}}
.nav-link:hover,.nav-link.active{{background:var(--muted);color:var(--fg);font-weight:500}}
.header-right{{margin-left:auto;display:flex;align-items:center;gap:10px}}
.chip{{display:inline-flex;align-items:center;gap:5px;padding:2px 9px;border:1px solid var(--border);border-radius:20px;font-size:11px;color:var(--muted-fg);font-family:'Geist Mono',monospace}}
.chip-dot{{width:5px;height:5px;border-radius:50%;background:var(--green)}}
.btn-demo{{display:inline-flex;align-items:center;height:32px;padding:0 14px;background:var(--fr-blue);color:#fff;border:none;border-radius:var(--radius);font-family:'Geist',sans-serif;font-size:13px;font-weight:500;text-decoration:none;transition:all .15s;white-space:nowrap}}
.btn-demo:hover{{background:#001c7a;transform:translateY(-1px)}}

/* Dropdown */
.nav-dropdown{{position:relative}}
.nav-dropdown-toggle{{padding:4px 10px;font-size:13px;color:var(--muted-fg);border-radius:4px;cursor:pointer;transition:all .12s;display:flex;align-items:center;gap:4px;background:none;border:none;font-family:'Geist',sans-serif}}
.nav-dropdown-toggle:hover,.nav-dropdown.open .nav-dropdown-toggle{{background:var(--muted);color:var(--fg);font-weight:500}}
.nav-dropdown-toggle svg{{transition:transform .2s}}
.nav-dropdown.open .nav-dropdown-toggle svg{{transform:rotate(180deg)}}
.nav-dropdown-menu{{display:none;position:absolute;top:calc(100% + 8px);left:50%;transform:translateX(-50%);background:#fff;border:1px solid var(--border);border-radius:8px;box-shadow:0 12px 40px rgba(0,0,0,.12);z-index:200;width:540px;padding:16px;max-height:70vh;overflow-y:auto}}
.nav-dropdown.open .nav-dropdown-menu{{display:block}}
.nav-dropdown-grid{{display:grid;grid-template-columns:1fr 1fr;gap:4px}}
.nav-dropdown-item{{display:flex;align-items:center;gap:8px;padding:8px 10px;border-radius:var(--radius);text-decoration:none;color:var(--fg);font-size:13px;transition:background .1s}}
.nav-dropdown-item:hover{{background:var(--muted)}}
.nav-dropdown-item-code{{font-family:'Geist Mono',monospace;font-size:10px;font-weight:600;color:var(--fr-blue);background:var(--muted);border:1px solid var(--border);width:22px;height:22px;border-radius:4px;display:grid;place-items:center;flex-shrink:0}}
.nav-dropdown-item-label{{line-height:1.3}}
.nav-dropdown-item-sub{{font-size:10px;color:var(--muted-fg);display:block}}
.nav-dropdown-backdrop{{display:none;position:fixed;inset:0;z-index:150}}
.nav-dropdown.open .nav-dropdown-backdrop{{display:block}}
@media(max-width:768px){{
  .nav-dropdown-menu{{width:calc(100vw - 32px);left:auto;right:-60px;transform:none}}
  .nav-dropdown-grid{{grid-template-columns:1fr}}
}}

/* Hero */
.hero{{background:var(--bg);position:relative;overflow:hidden;border-bottom:1px solid var(--border)}}
.tricolor-top{{display:flex;height:3px}}
.tricolor-top div:nth-child(1){{flex:1;background:var(--fr-blue)}}
.tricolor-top div:nth-child(2){{flex:1;background:#e8e8e8}}
.tricolor-top div:nth-child(3){{flex:1;background:var(--fr-red)}}
.hero-bg{{position:absolute;inset:0;background-image:linear-gradient(var(--border) 1px,transparent 1px),linear-gradient(90deg,var(--border) 1px,transparent 1px);background-size:52px 52px;opacity:.28;pointer-events:none}}
.hero-glow{{position:absolute;bottom:-30%;left:-5%;width:500px;height:500px;background:radial-gradient(ellipse,rgba(0,35,149,.05) 0%,transparent 68%);pointer-events:none}}
.hero-inner{{max-width:920px;margin:0 auto;padding:56px 32px 60px;position:relative;z-index:1;display:grid;grid-template-columns:1fr 380px;gap:48px;align-items:start}}
.hero-eyebrow{{display:inline-flex;align-items:center;gap:8px;font-size:11px;font-weight:500;letter-spacing:.1em;text-transform:uppercase;color:var(--muted-fg);margin-bottom:16px}}
.hero-eyebrow-bar{{width:20px;height:1px;background:var(--border)}}
.hero h1{{font-size:clamp(24px,3.5vw,36px);font-weight:700;letter-spacing:-1px;line-height:1.12;margin-bottom:16px}}
.h1-accent{{background:linear-gradient(120deg,var(--fr-blue) 0%,var(--fr-red) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
.hero-sub{{font-size:15px;font-weight:300;color:var(--muted-fg);line-height:1.7;margin-bottom:24px;max-width:420px}}
.hero-stats{{display:flex;gap:20px;flex-wrap:wrap}}
.hero-stat{{display:flex;flex-direction:column;gap:2px}}
.hero-stat-val{{font-size:20px;font-weight:700;letter-spacing:-.5px;color:var(--fg);font-family:'Geist Mono',monospace}}
.hero-stat-label{{font-size:11px;color:var(--muted-fg);text-transform:uppercase;letter-spacing:.06em}}
.hero-source{{font-size:11px;color:var(--muted-fg);margin-top:12px;font-style:italic}}

/* Form card */
.hero-form-card{{background:var(--card);border:1px solid var(--border);border-radius:10px;box-shadow:0 4px 24px rgba(0,35,149,.06),0 1px 4px rgba(0,0,0,.04);padding:24px 20px}}
.hero-form-card-title{{font-size:15px;font-weight:600;margin-bottom:4px}}
.hero-form-card-sub{{font-size:12px;color:var(--muted-fg);margin-bottom:18px;display:flex;align-items:center;gap:6px}}
.free-badge{{display:inline-flex;align-items:center;gap:4px;background:#f0fdf4;border:1px solid #bbf7d0;color:#15803d;font-size:10px;font-weight:600;padding:1px 7px;border-radius:20px;letter-spacing:.06em;text-transform:uppercase}}
.hf-field{{display:flex;flex-direction:column;gap:5px;margin-bottom:12px}}
.hf-label{{font-size:11px;font-weight:500;color:var(--muted-fg);letter-spacing:.06em;text-transform:uppercase}}
.hf-input-wrap{{position:relative}}
.hf-input{{width:100%;height:38px;padding:0 38px 0 12px;background:var(--bg);border:1px solid var(--border);border-radius:var(--radius);font-family:'Geist',sans-serif;font-size:13px;color:var(--fg);outline:none;transition:border-color .15s,box-shadow .15s}}
.hf-input::placeholder{{color:#a0aec0}}
.hf-input:focus{{border-color:var(--fr-blue);box-shadow:0 0 0 3px rgba(0,35,149,.08)}}
.hf-input-icon{{position:absolute;right:10px;top:50%;transform:translateY(-50%);font-size:11px;color:var(--muted-fg);font-family:'Geist Mono',monospace;pointer-events:none}}
.hf-input-icon.ok{{color:var(--green)}}
.hf-input-icon.err{{color:var(--fr-red)}}
.hf-input-icon.spin{{animation:blink .8s steps(1) infinite}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.2}}}}
.hf-dropdown{{position:absolute;top:calc(100% + 4px);left:0;right:0;background:#fff;border:1px solid var(--border);border-radius:var(--radius);box-shadow:0 8px 24px rgba(0,0,0,.14);z-index:300;max-height:200px;overflow-y:auto;display:none}}
.hf-dropdown.open{{display:block}}
.hf-ac-item{{padding:9px 12px;cursor:pointer;border-bottom:1px solid var(--border);transition:background .1s}}
.hf-ac-item:last-child{{border-bottom:none}}
.hf-ac-item:hover,.hf-ac-item.focused{{background:var(--muted)}}
.hf-ac-name{{font-size:13px;font-weight:500}}
.hf-ac-meta{{font-size:11px;color:var(--muted-fg);font-family:'Geist Mono',monospace;margin-top:1px;display:flex;gap:8px}}
.hf-ac-empty{{padding:12px;font-size:13px;color:var(--muted-fg);text-align:center}}
.hf-company-chip{{display:none;align-items:center;gap:6px;padding:5px 10px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:4px;font-size:12px;color:#15803d;margin-top:4px}}
.hf-company-chip.show{{display:flex}}
.hf-company-chip-dot{{width:5px;height:5px;border-radius:50%;background:var(--green);flex-shrink:0}}
.hf-company-chip-naf{{margin-left:auto;font-family:'Geist Mono',monospace;font-size:10px;background:#dcfce7;color:#15803d;padding:1px 6px;border-radius:3px}}
.hf-input-mono{{font-family:'Geist Mono',monospace}}
.hf-email-note{{font-size:11px;color:var(--muted-fg);margin-top:3px;display:flex;align-items:center;gap:4px}}
.cta-btn{{width:100%;height:42px;background:var(--fr-red);color:#fff;border:none;border-radius:var(--radius);font-family:'Geist',sans-serif;font-size:14px;font-weight:600;cursor:pointer;transition:all .15s;display:flex;align-items:center;justify-content:center;gap:8px;margin-top:16px}}
.cta-btn:hover{{background:#d42233;transform:translateY(-1px);box-shadow:0 4px 16px rgba(237,41,57,.35)}}
.cta-privacy{{text-align:center;font-size:11px;color:var(--muted-fg);margin-top:8px}}
.hf-alert{{display:none;align-items:flex-start;gap:7px;padding:8px 11px;background:#fff0f1;border:1px solid #fcc;border-radius:4px;font-size:12px;color:var(--fr-red);margin-top:10px;line-height:1.4}}
.hf-alert.show{{display:flex}}

/* Trust bar */
.trust-bar{{background:#f8f9fc;border-bottom:1px solid var(--border);padding:14px 32px;display:flex;align-items:center;justify-content:center;gap:32px;flex-wrap:wrap}}
.trust-item{{display:flex;align-items:center;gap:7px;font-size:12px;color:var(--muted-fg)}}
.trust-item strong{{color:var(--fg);font-weight:600}}
.trust-dot{{width:4px;height:4px;border-radius:50%;background:var(--border)}}

/* Metrics section */
.metrics-section{{max-width:920px;margin:0 auto;padding:56px 32px}}
.metrics-section h2{{font-size:clamp(20px,3vw,28px);font-weight:700;letter-spacing:-.6px;margin-bottom:8px}}
.metrics-sub{{font-size:14px;color:var(--muted-fg);margin-bottom:32px;max-width:600px;line-height:1.65}}
.metrics-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--border);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden}}
.metric-card{{background:var(--bg);padding:24px}}
.metric-label{{font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:.07em;color:var(--muted-fg);margin-bottom:8px;display:flex;align-items:center;gap:6px}}
.metric-dot{{width:6px;height:6px;border-radius:50%;flex-shrink:0}}
.metric-value{{font-size:28px;font-weight:700;letter-spacing:-.8px;line-height:1;margin-bottom:6px;font-variant-numeric:tabular-nums}}
.metric-desc{{font-size:12px;color:var(--muted-fg);line-height:1.5}}
.metric-bench{{margin-top:6px;font-size:11px;font-family:'Geist Mono',monospace}}
.metric-bench .above{{color:var(--fr-blue)}}
.metric-bench .below{{color:var(--fr-red)}}

/* Content section */
.content-section{{border-top:1px solid var(--border);background:var(--muted)}}
.content-inner{{max-width:920px;margin:0 auto;padding:56px 32px;display:grid;grid-template-columns:1fr 320px;gap:48px;align-items:start}}
.content-main h2{{font-size:clamp(18px,2.5vw,24px);font-weight:700;letter-spacing:-.5px;margin-bottom:16px}}
.content-main h3{{font-size:16px;font-weight:600;margin:28px 0 10px;display:flex;align-items:center;gap:8px}}
.content-main h3::before{{content:'';width:3px;height:16px;background:var(--fr-blue);border-radius:2px;flex-shrink:0}}
.content-main p{{font-size:14px;color:var(--muted-fg);line-height:1.75;margin-bottom:12px}}

/* Supply chain sidebar */
.sc-card{{border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);padding:20px}}
.sc-card-title{{font-size:13px;font-weight:600;margin-bottom:4px}}
.sc-card-sub{{font-size:11px;color:var(--muted-fg);margin-bottom:16px}}
.sc-item{{display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid var(--border)}}
.sc-item:last-child{{border-bottom:none}}
.sc-left{{display:flex;align-items:center;gap:6px;min-width:140px}}
.sc-pill{{display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;background:var(--muted);border:1px solid var(--border);border-radius:4px;font-size:10px;font-weight:600;font-family:'Geist Mono',monospace;color:var(--fr-blue);flex-shrink:0}}
.sc-label{{font-size:12px;color:var(--fg)}}
.sc-bar-wrap{{flex:1;height:6px;background:var(--muted);border-radius:3px;overflow:hidden}}
.sc-bar{{height:100%;background:linear-gradient(90deg,var(--fr-blue),#4a6dd8);border-radius:3px}}
.sc-val{{font-size:11px;font-family:'Geist Mono',monospace;color:var(--muted-fg);min-width:40px;text-align:right}}

/* CTA section */
.sector-cta{{border-top:1px solid var(--border);background:var(--bg)}}
.sector-cta-inner{{max-width:920px;margin:0 auto;padding:56px 32px;text-align:center}}
.sector-cta-inner h2{{font-size:clamp(18px,2.5vw,24px);font-weight:700;letter-spacing:-.5px;margin-bottom:8px}}
.sector-cta-inner p{{font-size:14px;color:var(--muted-fg);margin-bottom:24px;max-width:500px;margin-left:auto;margin-right:auto;line-height:1.65}}
.cta-link{{display:inline-flex;align-items:center;gap:8px;height:44px;padding:0 28px;background:var(--fr-red);color:#fff;border-radius:var(--radius);font-size:14px;font-weight:600;text-decoration:none;transition:all .15s}}
.cta-link:hover{{background:#d42233;transform:translateY(-1px);box-shadow:0 4px 16px rgba(237,41,57,.35)}}
.cta-secondary{{display:inline-flex;align-items:center;gap:6px;margin-left:12px;height:44px;padding:0 20px;background:var(--bg);color:var(--fg);border:1px solid var(--border);border-radius:var(--radius);font-size:13px;font-weight:500;text-decoration:none;transition:all .15s}}
.cta-secondary:hover{{border-color:var(--fr-blue);color:var(--fr-blue)}}

/* FAQ */
.faq-section{{border-top:1px solid var(--border)}}
.faq-inner{{max-width:920px;margin:0 auto;padding:56px 32px}}
.faq-inner h2{{font-size:clamp(18px,2.5vw,24px);font-weight:700;letter-spacing:-.5px;margin-bottom:24px}}
.faq-item{{border:1px solid var(--border);border-radius:var(--radius);margin-bottom:8px;overflow:hidden;background:var(--bg)}}
.faq-q{{width:100%;padding:16px 20px;background:none;border:none;font-family:'Geist',sans-serif;font-size:14px;font-weight:500;color:var(--fg);cursor:pointer;display:flex;align-items:center;justify-content:space-between;gap:12px;text-align:left}}
.faq-q svg{{flex-shrink:0;transition:transform .2s;color:var(--muted-fg)}}
.faq-item.open .faq-q svg{{transform:rotate(180deg)}}
.faq-a{{max-height:0;overflow:hidden;transition:max-height .3s ease}}
.faq-item.open .faq-a{{max-height:300px}}
.faq-a p{{padding:0 20px 16px;font-size:14px;color:var(--muted-fg);line-height:1.75}}

/* Other sectors */
.other-sectors{{border-top:1px solid var(--border);background:var(--muted)}}
.other-sectors-inner{{max-width:920px;margin:0 auto;padding:48px 32px}}
.other-sectors-inner h3{{font-size:16px;font-weight:600;margin-bottom:16px}}
.sector-links{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px}}
.sector-link{{display:flex;align-items:center;gap:8px;padding:10px 14px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);text-decoration:none;color:var(--fg);font-size:13px;transition:border-color .15s,box-shadow .15s}}
.sector-link:hover{{border-color:var(--fr-blue);box-shadow:0 2px 8px rgba(0,35,149,.08)}}
.sector-link-code{{font-family:'Geist Mono',monospace;font-size:11px;font-weight:600;color:var(--fr-blue);background:var(--muted);border:1px solid var(--border);width:24px;height:24px;border-radius:4px;display:grid;place-items:center;flex-shrink:0}}

/* Footer */
.site-footer{{border-top:1px solid var(--border);padding:40px 32px}}
.footer-inner{{max-width:920px;margin:0 auto;display:grid;grid-template-columns:1.5fr 1fr 1fr;gap:40px}}
.footer-logo{{display:flex;align-items:baseline;gap:5px;margin-bottom:8px}}
.footer-sub{{font-size:12px;color:var(--muted-fg);line-height:1.55;max-width:220px}}
.footer-made{{margin-top:10px;font-size:11px;color:var(--muted-fg)}}
.footer-col-title{{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.07em;margin-bottom:10px}}
.footer-links{{display:flex;flex-direction:column;gap:7px}}
.footer-link{{font-size:13px;color:var(--muted-fg);text-decoration:none;transition:color .12s}}
.footer-link:hover{{color:var(--fg)}}
.footer-bottom{{max-width:920px;margin:24px auto 0;padding-top:20px;border-top:1px solid var(--border);display:flex;justify-content:space-between;font-size:12px;color:var(--muted-fg)}}

/* Responsive */
@media(max-width:768px){{
  .site-header{{padding:0 16px}}
  .site-nav .nav-link:not(.active){{display:none}}
  .hero-inner{{grid-template-columns:1fr;padding:36px 16px 40px;gap:28px}}
  .hero-stats{{gap:16px}}
  .metrics-section{{padding:36px 16px}}
  .metrics-grid{{grid-template-columns:1fr}}
  .content-inner{{grid-template-columns:1fr;padding:36px 16px}}
  .sector-cta-inner{{padding:36px 16px}}
  .faq-inner{{padding:36px 16px}}
  .other-sectors-inner{{padding:36px 16px}}
  .sector-links{{grid-template-columns:1fr}}
  .trust-bar{{padding:12px 16px;gap:16px}}
  .footer-inner{{grid-template-columns:1fr}}
  .footer-bottom{{flex-direction:column;gap:6px}}
}}
</style>
</head>
<body>

<!-- Header -->
<header class="site-header">
  <a class="logo" href="/">
    <span class="logo-in">IN</span>
    <span class="logo-france">FRANCE</span>
  </a>
  <div class="header-sep"></div>
  <nav class="site-nav">
    <a class="nav-link" href="/">Simulateur</a>
    <div class="nav-dropdown" id="secDropdown">
      <div class="nav-dropdown-backdrop" onclick="document.getElementById('secDropdown').classList.remove('open')"></div>
      <button class="nav-dropdown-toggle" onclick="this.parentElement.classList.toggle('open')">
        Secteurs
        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
      </button>
      <div class="nav-dropdown-menu">
        <div class="nav-dropdown-grid">
''' + generate_dropdown_items() + f'''        </div>
      </div>
    </div>
    <a class="nav-link" href="/methodologie">Methodologie</a>
    <a class="nav-link" href="/a-propos">A propos</a>
  </nav>
  <div class="header-right">
    <div class="chip"><div class="chip-dot"></div>API live</div>
    <a class="btn-demo" href="/contact">Prendre rendez-vous &rarr;</a>
  </div>
</header>

<!-- Hero -->
<section class="hero">
  <div class="tricolor-top"><div></div><div></div><div></div></div>
  <div class="hero-bg"></div>
  <div class="hero-glow"></div>

  <div class="hero-inner">
    <div class="hero-left">
      <div class="hero-eyebrow">
        <div class="hero-eyebrow-bar"></div>
        Impact territorial &middot; Secteur {code}
      </div>
      <h1>{sector["emoji"]} {sector["label"]}</h1>
      <p class="hero-sub">{sector["hero_sub"]}</p>
      <div class="hero-stats">
''' + (f'''        <div class="hero-stat">
          <div class="hero-stat-val">{sector["nb_entreprises"]}</div>
          <div class="hero-stat-label">Entreprises</div>
        </div>
''' if sector["nb_entreprises"] else '') + f'''        <div class="hero-stat">
          <div class="hero-stat-val">{sector["nb_emplois"]}</div>
          <div class="hero-stat-label">Emplois{"" if sector["code"] == "O" else " (EQTP)"}</div>
        </div>
        <div class="hero-stat">
          <div class="hero-stat-val">{bs["multiplicateur"]:.2f}&times;</div>
          <div class="hero-stat-label">Multiplicateur</div>
        </div>
''' + (f'''        <div class="hero-stat">
          <div class="hero-stat-val">{sector["ca_cumule"]}</div>
          <div class="hero-stat-label">CA cumule</div>
        </div>
''' if sector["ca_cumule"] else '') + f'''      </div>
      <div class="hero-source">Source : {sector.get("source_nb", "INSEE")}</div>
    </div>

    <!-- Form -->
    <div class="hero-form-card">
      <div class="hero-form-card-title">Simulez l'impact de votre entreprise</div>
      <div class="hero-form-card-sub">
        <span class="free-badge">&#10022; Gratuit</span>
        Resultats instantanes
      </div>

      <div class="hf-field">
        <label class="hf-label" for="searchInput">Entreprise (nom ou SIREN)</label>
        <div class="hf-input-wrap">
          <input class="hf-input" type="text" id="searchInput" placeholder="Ex : Bouygues ou 572015246" autocomplete="off" spellcheck="false">
          <span class="hf-input-icon" id="searchIcon"></span>
          <div class="hf-dropdown" id="acDropdown"></div>
        </div>
        <div class="hf-company-chip" id="companyChip">
          <div class="hf-company-chip-dot"></div>
          <span id="chipName"></span>
          <span class="hf-company-chip-naf" id="chipNaf"></span>
        </div>
      </div>

      <div class="hf-field">
        <label class="hf-label" for="caInput">Chiffre d'affaires annuel HT</label>
        <div class="hf-input-wrap">
          <input class="hf-input hf-input-mono" type="text" id="caInput" placeholder="5 000 000">
          <span class="hf-input-icon">&euro;</span>
        </div>
      </div>

      <div class="hf-field">
        <label class="hf-label" for="emailInput">Email (recevez vos resultats)</label>
        <div class="hf-input-wrap">
          <input class="hf-input" type="email" id="emailInput" placeholder="vous@entreprise.fr">
          <span class="hf-input-icon">&#9993;</span>
        </div>
        <div class="hf-email-note">&#128274; Confidentiel &middot; Jamais revendu</div>
      </div>

      <button class="cta-btn" id="ctaBtn" onclick="goSimulate()">
        Simuler l'impact &rarr;
      </button>
      <div class="cta-privacy">Simulation 100 % gratuite &middot; Donnees BdF, OCDE &amp; Eurostat</div>

      <div class="hf-alert" id="heroAlert">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex-shrink:0;margin-top:1px">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <span id="alertText"></span>
      </div>
    </div>
  </div>
</section>

<!-- Trust bar -->
<div class="trust-bar">
  <div class="trust-item"><strong>BdF FIBEN</strong> <span>Ratios sectoriels 2024</span></div>
  <div class="trust-dot"></div>
  <div class="trust-item"><strong>OCDE ICIO</strong> <span>Matrices Leontief 2023</span></div>
  <div class="trust-dot"></div>
  <div class="trust-item"><strong>Eurostat HBS</strong> <span>Consommation menages 2020</span></div>
  <div class="trust-dot"></div>
  <div class="trust-item"><strong>INSEE SIRENE</strong> <span>Base entreprises officielle</span></div>
</div>

<!-- Key Metrics -->
<section class="metrics-section">
  <h2>Chiffres cles du secteur {sector["short"]} en France</h2>
  <p class="metrics-sub">Donnees issues de la Banque de France (FIBEN 2024), de l'OCDE (ICIO 2023) et d'Eurostat (HBS 2020).</p>

  <div class="metrics-grid">
    <div class="metric-card">
      <div class="metric-label"><div class="metric-dot" style="background:var(--fr-blue)"></div>Multiplicateur d'emploi</div>
      <div class="metric-value">{bs["multiplicateur"]:.2f}&times;</div>
      <div class="metric-desc">Pour 1 emploi direct, {bs["multiplicateur"] - 1:.2f} emplois supplementaires generes</div>
      <div class="metric-bench">vs. national : <span class="{"above" if bs["multiplicateur"] >= BENCH_NAT["multiplicateur"] else "below"}">{mult_vs_nat}</span></div>
    </div>
    <div class="metric-card">
      <div class="metric-label"><div class="metric-dot" style="background:#7088b8"></div>Valeur ajoutee / CA</div>
      <div class="metric-value">{bs["va_sur_ca"]:.0f} %</div>
      <div class="metric-desc">Taux de valeur ajoutee sectoriel</div>
      <div class="metric-bench">vs. national : <span class="{"above" if bs["va_sur_ca"] >= BENCH_NAT["va_sur_ca"] else "below"}">{va_vs_nat}</span></div>
    </div>
    <div class="metric-card">
      <div class="metric-label"><div class="metric-dot" style="background:var(--fr-red)"></div>Emplois par M&euro; de CA</div>
      <div class="metric-value">{bs["emplois_par_mca"]:.1f}</div>
      <div class="metric-desc">Intensite en main-d'oeuvre du secteur</div>
      <div class="metric-bench">vs. national : <span class="{"above" if bs["emplois_par_mca"] >= BENCH_NAT["emplois_par_mca"] else "below"}">{emp_vs_nat}</span></div>
    </div>
    <div class="metric-card">
      <div class="metric-label"><div class="metric-dot" style="background:var(--green)"></div>Part des salaires</div>
      <div class="metric-value">{bs["part_salaires"]:.0f} %</div>
      <div class="metric-desc">Part de la VA redistribuee en salaires</div>
      <div class="metric-bench">vs. national : <span class="{"above" if bs["part_salaires"] >= BENCH_NAT["part_salaires"] else "below"}">{bench_comparison(bs["part_salaires"], BENCH_NAT["part_salaires"])}</span></div>
    </div>
    <div class="metric-card">
      <div class="metric-label"><div class="metric-dot" style="background:#e4a853"></div>Contributions fiscales</div>
      <div class="metric-value">{bs["part_taxes"]:.1f} %</div>
      <div class="metric-desc">Part de la VA versee en taxes</div>
      <div class="metric-bench">vs. national : <span class="{"above" if bs["part_taxes"] >= BENCH_NAT["part_taxes"] else "below"}">{bench_comparison(bs["part_taxes"], BENCH_NAT["part_taxes"])}</span></div>
    </div>
    <div class="metric-card">
      <div class="metric-label"><div class="metric-dot" style="background:#8b5cf6"></div>Impact indirect</div>
      <div class="metric-value">{bs["indirect_pct"]:.0f} %</div>
      <div class="metric-desc">Part de l'impact total generee par la chaine d'approvisionnement</div>
      <div class="metric-bench">vs. national : <span class="{"above" if bs["indirect_pct"] >= BENCH_NAT["indirect_pct"] else "below"}">{bench_comparison(bs["indirect_pct"], BENCH_NAT["indirect_pct"])}</span></div>
    </div>
  </div>
</section>

<!-- Content + Supply chain -->
<section class="content-section">
  <div class="content-inner">
    <div class="content-main">
      <h2>L'impact territorial du secteur {sector["short"].lower()} en France</h2>
      <p>{sector["content_intro"]}</p>

      <h3>Effets directs</h3>
      <p>{sector["content_direct"]}</p>

      <h3>Effets indirects (chaine d'approvisionnement)</h3>
      <p>{sector["content_indirect"]}</p>

      <h3>Effets induits (consommation des menages)</h3>
      <p>{sector["content_induced"]}</p>
    </div>

    <div class="content-sidebar">
      <div class="sc-card">
        <div class="sc-card-title">Secteurs actives par {sector["short"].lower()}</div>
        <div class="sc-card-sub">Coefficients Leontief OCDE ICIO 2023</div>
        {supply_chain_html}
      </div>
    </div>
  </div>
</section>

<!-- FAQ -->
<section class="faq-section">
  <div class="faq-inner">
    <h2>Questions frequentes sur le secteur {sector["short"]}</h2>
    {faq_html}
  </div>
</section>

<!-- CTA -->
<section class="sector-cta">
  <div class="sector-cta-inner">
    <h2>Mesurez l'impact de votre entreprise</h2>
    <p>Calculez en 30 secondes les emplois, la valeur ajoutee et les taxes generees par votre entreprise dans le secteur {sector["short"].lower()}.</p>
    <a class="cta-link" href="/">Lancer la simulation &rarr;</a>
    <a class="cta-secondary" href="/contact">Prendre rendez-vous</a>
  </div>
</section>

<!-- Other sectors -->
<section class="other-sectors">
  <div class="other-sectors-inner">
    <h3>Decouvrir les autres secteurs</h3>
    <div class="sector-links">
''' + generate_other_sectors_links(slug) + '''
    </div>
  </div>
</section>

<!-- Footer -->
<footer class="site-footer">
  <div class="footer-inner">
    <div>
      <div class="footer-logo">
        <span class="logo-in">IN</span>
        <span class="logo-france">FRANCE</span>
      </div>
      <p class="footer-sub">Simulateur d'impact territorial. Mesurez la valeur economique reelle de votre entreprise en France.</p>
      <p class="footer-made">Donnees BdF FIBEN 2024 &middot; OCDE ICIO 2023 &middot; Eurostat HBS 2020</p>
    </div>
    <div>
      <div class="footer-col-title">Produit</div>
      <div class="footer-links">
        <a class="footer-link" href="/">Simulateur</a>
        <a class="footer-link" href="/methodologie">Methodologie</a>
        <a class="footer-link" href="/cas-usage">Cas d'usage</a>
        <a class="footer-link" href="/contact">Contact</a>
      </div>
    </div>
    <div>
      <div class="footer-col-title">Secteurs</div>
      <div class="footer-links">
        <a class="footer-link" href="/secteur/construction">Construction</a>
        <a class="footer-link" href="/secteur/commerce">Commerce</a>
        <a class="footer-link" href="/secteur/industrie-manufacturiere">Industrie</a>
        <a class="footer-link" href="/secteur/sante">Sante</a>
      </div>
    </div>
  </div>
  <div class="footer-bottom">
    <span>&copy; 2025 IN France. Tous droits reserves.</span>
    <span>Mentions legales &middot; Politique de confidentialite</span>
  </div>
</footer>

<script>
/* ─── AUTOCOMPLETE ─── */
let acTimer = null, acFocusIdx = -1, selectedSiren = null;
const searchInput = document.getElementById('searchInput');
const acDropdown = document.getElementById('acDropdown');

searchInput.addEventListener('input', function() {{
  clearTimeout(acTimer);
  const q = this.value.trim();
  selectedSiren = null;
  document.getElementById('companyChip').classList.remove('show');
  document.getElementById('searchIcon').className = 'hf-input-icon';
  document.getElementById('searchIcon').textContent = '';

  if (!q) {{ acDropdown.classList.remove('open'); return; }}
  if (/^\\d{{9}}$/.test(q)) {{ lookupBySiren(q); return; }}
  if (q.length < 2) return;

  acTimer = setTimeout(() => searchByName(q), 250);
}});

searchInput.addEventListener('keydown', function(e) {{
  const items = acDropdown.querySelectorAll('.hf-ac-item');
  if (!items.length) return;
  if (e.key === 'ArrowDown') {{ e.preventDefault(); acFocusIdx = Math.min(acFocusIdx + 1, items.length - 1); updateFocus(items); }}
  else if (e.key === 'ArrowUp') {{ e.preventDefault(); acFocusIdx = Math.max(acFocusIdx - 1, 0); updateFocus(items); }}
  else if (e.key === 'Enter' && acFocusIdx >= 0) {{ e.preventDefault(); items[acFocusIdx].click(); }}
  else if (e.key === 'Escape') {{ acDropdown.classList.remove('open'); acFocusIdx = -1; }}
}});

function updateFocus(items) {{
  items.forEach((el, i) => el.classList.toggle('focused', i === acFocusIdx));
}}

async function searchByName(q) {{
  const icon = document.getElementById('searchIcon');
  icon.className = 'hf-input-icon spin'; icon.textContent = '...';
  try {{
    const r = await fetch('https://recherche-entreprises.api.gouv.fr/search?q=' + encodeURIComponent(q) + '&per_page=6');
    const d = await r.json();
    icon.className = 'hf-input-icon'; icon.textContent = '';
    renderAC(d.results || []);
  }} catch(e) {{ icon.className = 'hf-input-icon err'; icon.textContent = '!'; }}
}}

async function lookupBySiren(siren) {{
  const icon = document.getElementById('searchIcon');
  icon.className = 'hf-input-icon spin'; icon.textContent = '...';
  try {{
    const r = await fetch('https://recherche-entreprises.api.gouv.fr/search?q=' + siren + '&per_page=1');
    const d = await r.json();
    if (d.results && d.results.length) {{ pickCompany(d.results[0]); }}
    else {{ icon.className = 'hf-input-icon err'; icon.textContent = '?'; }}
  }} catch(e) {{ icon.className = 'hf-input-icon err'; icon.textContent = '!'; }}
}}

function renderAC(results) {{
  acFocusIdx = -1;
  if (!results.length) {{
    acDropdown.innerHTML = '<div class="hf-ac-empty">Aucun resultat</div>';
    acDropdown.classList.add('open');
    return;
  }}
  acDropdown.innerHTML = results.map((r, i) => {{
    const name = r.nom_complet || r.nom_raison_sociale || '';
    const siren = r.siren || '';
    const naf = r.activite_principale || '';
    const ville = r.siege && r.siege.libelle_commune ? r.siege.libelle_commune : '';
    return '<div class="hf-ac-item" data-idx="' + i + '" onclick="pickCompany(acResults[' + i + '])">' +
      '<div class="hf-ac-name">' + name + '</div>' +
      '<div class="hf-ac-meta"><span>' + siren + '</span><span>' + naf + '</span><span>' + ville + '</span></div></div>';
  }}).join('');
  acDropdown.classList.add('open');
  window.acResults = results;
}}

function pickCompany(company) {{
  const name = company.nom_complet || company.nom_raison_sociale || '';
  const siren = company.siren || '';
  const naf = company.activite_principale || '';
  const section = naf ? naf.charAt(0) : '';

  selectedSiren = siren;
  searchInput.value = name;
  acDropdown.classList.remove('open');

  const icon = document.getElementById('searchIcon');
  icon.className = 'hf-input-icon ok'; icon.textContent = '\\u2713';

  const chip = document.getElementById('companyChip');
  document.getElementById('chipName').textContent = name;
  document.getElementById('chipNaf').textContent = naf + ' \\u2014 ' + section;
  chip.classList.add('show');
}}

document.addEventListener('click', function(e) {{
  if (!e.target.closest('.hf-input-wrap')) acDropdown.classList.remove('open');
}});

/* CA formatter */
const caInput = document.getElementById('caInput');
caInput.addEventListener('input', function() {{
  let v = this.value.replace(/[^\\d]/g, '');
  if (v) this.value = parseInt(v).toLocaleString('fr-FR');
}});

/* Submit → redirect to homepage with params */
function goSimulate() {{
  const siren = selectedSiren;
  const ca = caInput.value.replace(/[\\s\\u00A0\\u202F,]/g, '');
  const email = document.getElementById('emailInput').value.trim();
  const alert = document.getElementById('heroAlert');
  const alertText = document.getElementById('alertText');

  if (!siren) {{
    alert.classList.add('show');
    alertText.textContent = 'Veuillez selectionner une entreprise dans la liste.';
    return;
  }}
  if (!ca || parseInt(ca) <= 0) {{
    alert.classList.add('show');
    alertText.textContent = 'Veuillez saisir un chiffre d\\'affaires valide.';
    return;
  }}

  alert.classList.remove('show');
  let url = '/?siren=' + encodeURIComponent(siren) + '&ca=' + encodeURIComponent(ca);
  if (email) url += '&email=' + encodeURIComponent(email);
  url += '&auto=1';
  window.location.href = url;
}}
</script>

</body>
</html>'''
    return html


def generate_other_sectors_links(current_slug):
    links = ""
    for s in SECTORS:
        if s["slug"] == current_slug:
            continue
        links += f'''      <a class="sector-link" href="/secteur/{s["slug"]}">
        <span class="sector-link-code">{s["code"]}</span>
        {s["short"]}
      </a>\n'''
    return links


def main():
    os.makedirs(".", exist_ok=True)
    for sector in SECTORS:
        filename = f'secteur-{sector["slug"]}.html'
        html = generate_page(sector)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  Generated {filename}")

    print(f"\n  {len(SECTORS)} sector pages generated.")


if __name__ == "__main__":
    main()
