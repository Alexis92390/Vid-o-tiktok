/*
 * Sources : notices, bases officielles, documents de référence.
 * "generales" : sources valables pour tout le guide.
 * "parFiche" : sources par contenu. La clé (ex. "situation-1") doit être l'"id" d'une fiche
 *   ou d'une animation, ou "medicaments", "quiz-j0", "quiz-j30".
 * "type" : par exemple notice, base officielle, recommandation, document interne.
 * "lien" : adresse web commençant par https:// (laisser "" si aucune).
 * "consulteLe" : date de consultation, par exemple "2026-11-17".
 */
window.GUIDE = window.GUIDE || {};
GUIDE.sources = {
  "generales": [
    {
      "titre": "Base de données publique des médicaments (notices et RCP)",
      "type": "Base officielle",
      "lien": "https://base-donnees-publique.medicaments.gouv.fr/",
      "consulteLe": "À COMPLÉTER"
    },
    {
      "titre": "ANSM – Agence nationale de sécurité du médicament",
      "type": "Base officielle",
      "lien": "https://ansm.sante.fr/",
      "consulteLe": "À COMPLÉTER"
    },
    {
      "titre": "HAS – Haute Autorité de santé (recommandations)",
      "type": "Recommandation",
      "lien": "https://www.has-sante.fr/",
      "consulteLe": "À COMPLÉTER"
    },
    {
      "titre": "Cespharm – Comité d'éducation sanitaire et sociale de la pharmacie française",
      "type": "Document de référence",
      "lien": "https://www.cespharm.fr/",
      "consulteLe": "À COMPLÉTER"
    },
    {
      "titre": "Meddispar – Médicaments à dispensation particulière",
      "type": "Base officielle",
      "lien": "https://www.meddispar.fr/",
      "consulteLe": "À COMPLÉTER"
    },
    {
      "titre": "Ordre national des pharmaciens",
      "type": "Document de référence",
      "lien": "https://www.ordre.pharmacien.fr/",
      "consulteLe": "À COMPLÉTER"
    }
  ],
  "parFiche": {
    "mal-de-gorge": [
      {
        "titre": "Notices des médicaments cités dans la fiche (pastilles et sprays pour la gorge, paracétamol)",
        "type": "Notice",
        "lien": "",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "Ordre national des pharmaciens – Délivrance sans ordonnance d'antibiotiques suite à un test positif",
        "type": "Document de référence",
        "lien": "https://www.ordre.pharmacien.fr/les-communications/focus-sur/les-actualites/delivrance-sans-ordonnance-d-antibiotiques-suite-a-un-test-positif-par-les-pharmaciens-d-officine-publication-des-textes",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "Ordre national des pharmaciens – Dispensation de médicaments suite à un TROD : évolution des modalités",
        "type": "Document de référence",
        "lien": "https://www.ordre.pharmacien.fr/les-communications/focus-sur/les-actualites/dispensation-de-medicaments-suite-a-un-trod-a-l-officine-evolution-des-modalites-de-prise-en-charge-et-de-formation",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "Base de données publique des médicaments (notices et RCP)",
        "type": "Base officielle",
        "lien": "https://base-donnees-publique.medicaments.gouv.fr/",
        "consulteLe": "À COMPLÉTER"
      }
    ],
    "toux": [
      {
        "titre": "Notices des médicaments cités dans la fiche (antitussifs, mucolytiques)",
        "type": "Notice",
        "lien": "",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "ANSM – Antitussifs opiacés (codéine, dextrométhorphane...) : délivrance sur prescription depuis juillet 2017",
        "type": "Base officielle",
        "lien": "https://ansm.sante.fr/",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "ANSM – Mucolytiques : contre-indication chez l'enfant de moins de 2 ans",
        "type": "Base officielle",
        "lien": "https://ansm.sante.fr/",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "Base de données publique des médicaments (notices et RCP)",
        "type": "Base officielle",
        "lien": "https://base-donnees-publique.medicaments.gouv.fr/",
        "consulteLe": "À COMPLÉTER"
      }
    ],
    "rhume": [
      {
        "titre": "ANSM – Rhume : ordonnance obligatoire pour toute dispensation de médicament à base de pseudoéphédrine (10/12/2024)",
        "type": "Base officielle",
        "lien": "https://ansm.sante.fr/actualites/rhume-ordonnance-obligatoire-pour-toute-dispensation-de-medicament-a-base-de-pseudoephedrine",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "Notices des médicaments cités dans la fiche (sérum physiologique, paracétamol, antihistaminiques)",
        "type": "Notice",
        "lien": "",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "Base de données publique des médicaments (notices et RCP)",
        "type": "Base officielle",
        "lien": "https://base-donnees-publique.medicaments.gouv.fr/",
        "consulteLe": "À COMPLÉTER"
      }
    ],
    "douleur-fievre": [
      {
        "titre": "ANSM – Dossier thématique : le paracétamol",
        "type": "Base officielle",
        "lien": "https://ansm.sante.fr/dossiers-thematiques/le-paracetamol",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "ANSM – Paracétamol, ibuprofène, aspirine : fin du libre accès (janvier 2020)",
        "type": "Base officielle",
        "lien": "https://ansm.sante.fr/",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "ANSM – AINS et grossesse : contre-indication à partir du 6e mois",
        "type": "Base officielle",
        "lien": "https://ansm.sante.fr/",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "ANSM – AINS et risque d'aggravation des infections",
        "type": "Base officielle",
        "lien": "https://ansm.sante.fr/",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "Notices des médicaments cités dans la fiche (paracétamol, ibuprofène, aspirine)",
        "type": "Notice",
        "lien": "",
        "consulteLe": "À COMPLÉTER"
      }
    ],
    "diarrhee": [
      {
        "titre": "Notices des médicaments cités dans la fiche (lopéramide, racécadotril, diosmectite, SRO)",
        "type": "Notice",
        "lien": "",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "ANSM – Diosmectite : plus recommandée chez l'enfant de moins de 2 ans et la femme enceinte ou allaitante",
        "type": "Base officielle",
        "lien": "https://ansm.sante.fr/",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "Base de données publique des médicaments (notices et RCP)",
        "type": "Base officielle",
        "lien": "https://base-donnees-publique.medicaments.gouv.fr/",
        "consulteLe": "À COMPLÉTER"
      }
    ],
    "brulures-estomac": [
      {
        "titre": "Notices des médicaments cités dans la fiche (alginates, antiacides, IPP 20 mg)",
        "type": "Notice",
        "lien": "",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "HAS – Haute Autorité de santé (recommandations)",
        "type": "Recommandation",
        "lien": "https://www.has-sante.fr/",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "Base de données publique des médicaments (notices et RCP)",
        "type": "Base officielle",
        "lien": "https://base-donnees-publique.medicaments.gouv.fr/",
        "consulteLe": "À COMPLÉTER"
      }
    ],
    "medicaments": [
      {
        "titre": "Base de données publique des médicaments (notices et RCP)",
        "type": "Base officielle",
        "lien": "https://base-donnees-publique.medicaments.gouv.fr/",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "Meddispar – Médicaments à dispensation particulière",
        "type": "Base officielle",
        "lien": "https://www.meddispar.fr/",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "ANSM – Dossier thématique : le paracétamol",
        "type": "Base officielle",
        "lien": "https://ansm.sante.fr/dossiers-thematiques/le-paracetamol",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "ANSM – Rhume : ordonnance obligatoire pour toute dispensation de médicament à base de pseudoéphédrine (10/12/2024)",
        "type": "Base officielle",
        "lien": "https://ansm.sante.fr/actualites/rhume-ordonnance-obligatoire-pour-toute-dispensation-de-medicament-a-base-de-pseudoephedrine",
        "consulteLe": "À COMPLÉTER"
      }
    ],
    "ains": [
      {
        "titre": "Notices des médicaments cités dans la fiche (ibuprofène)",
        "type": "Notice",
        "lien": "",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "Base de données publique des médicaments (notices et RCP)",
        "type": "Base officielle",
        "lien": "https://base-donnees-publique.medicaments.gouv.fr/",
        "consulteLe": "À COMPLÉTER"
      }
    ],
    "ipp": [
      {
        "titre": "Notices des médicaments cités dans la fiche (oméprazole)",
        "type": "Notice",
        "lien": "",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "Base de données publique des médicaments (notices et RCP)",
        "type": "Base officielle",
        "lien": "https://base-donnees-publique.medicaments.gouv.fr/",
        "consulteLe": "À COMPLÉTER"
      }
    ],
    "quiz-j0": [
      {
        "titre": "Fiches du guide : douleur et fièvre, toux, diarrhée, brûlures d'estomac, mal de gorge",
        "type": "Document interne",
        "lien": "",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "ANSM – Dossier thématique : le paracétamol",
        "type": "Base officielle",
        "lien": "https://ansm.sante.fr/dossiers-thematiques/le-paracetamol",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "Ordre national des pharmaciens – Délivrance sans ordonnance d'antibiotiques suite à un test positif",
        "type": "Document de référence",
        "lien": "https://www.ordre.pharmacien.fr/les-communications/focus-sur/les-actualites/delivrance-sans-ordonnance-d-antibiotiques-suite-a-un-test-positif-par-les-pharmaciens-d-officine-publication-des-textes",
        "consulteLe": "À COMPLÉTER"
      }
    ],
    "quiz-j30": [
      {
        "titre": "Fiches du guide, tableau des médicaments et animations",
        "type": "Document interne",
        "lien": "",
        "consulteLe": "À COMPLÉTER"
      },
      {
        "titre": "ANSM – Rhume : ordonnance obligatoire pour toute dispensation de médicament à base de pseudoéphédrine (10/12/2024)",
        "type": "Base officielle",
        "lien": "https://ansm.sante.fr/actualites/rhume-ordonnance-obligatoire-pour-toute-dispensation-de-medicament-a-base-de-pseudoephedrine",
        "consulteLe": "À COMPLÉTER"
      }
    ]
  }
};
