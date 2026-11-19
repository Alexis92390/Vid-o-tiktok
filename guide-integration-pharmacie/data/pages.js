/*
 * Pages libres (non médicales ou validées) : organisation, contacts, procédures...
 * Une page = un bloc { ... }. Elle est accessible à l'adresse index.html#/page/<id>.
 * "menu": true l'ajoute au menu principal ; false la laisse accessible par lien seulement.
 * Chaque section peut avoir "paragraphes" (liste de textes) et/ou "liste" (liste à puces).
 */
window.GUIDE = window.GUIDE || {};
GUIDE.pages = [
  {
    "id": "urgences",
    "titre": "Urgences et numéros utiles",
    "menu": true,
    "sections": [
      {
        "titre": "En cas d'urgence au comptoir",
        "paragraphes": [
          "Si un patient présente un signe de gravité (malaise, gêne respiratoire, douleur thoracique, confusion, saignement important), prévenez immédiatement le pharmacien. Ne laissez pas le patient seul."
        ],
        "liste": [
          "15 : SAMU, urgence médicale",
          "112 : numéro d'urgence européen",
          "114 : urgences pour les personnes sourdes, malentendantes ou ayant des difficultés à parler (SMS, visio, tchat)",
          "18 : pompiers",
          "3237 : trouver la pharmacie de garde"
        ]
      },
      {
        "titre": "Numéros de l'officine",
        "paragraphes": [],
        "liste": [
          "Centre antipoison de la région : À COMPLÉTER",
          "Médecins du secteur : À COMPLÉTER",
          "Grossiste-répartiteur : À COMPLÉTER",
          "Téléphone du pharmacien d'astreinte : À COMPLÉTER"
        ]
      }
    ]
  },
  {
    "id": "modele",
    "titre": "Modèle de page",
    "menu": false,
    "sections": [
      {
        "titre": "Titre de section : À COMPLÉTER",
        "paragraphes": [
          "À COMPLÉTER"
        ],
        "liste": [
          "À COMPLÉTER",
          "À COMPLÉTER"
        ]
      }
    ]
  }
];
