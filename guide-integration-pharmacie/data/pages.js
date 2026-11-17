/*
 * Pages libres (non médicales ou validées) : organisation, contacts, procédures...
 * Une page = un bloc { ... }. Elle est accessible à l'adresse index.html#/page/<id>.
 * "menu": true l'ajoute au menu principal ; false la laisse accessible par lien seulement.
 * Chaque section peut avoir "paragraphes" (liste de textes) et/ou "liste" (liste à puces).
 */
window.GUIDE = window.GUIDE || {};
GUIDE.pages = [
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
