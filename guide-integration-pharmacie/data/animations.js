/*
 * Animations « Comment agit une classe de médicaments ».
 * Une animation = un bloc { ... } ; elle s'affiche seule sur sa propre page.
 * Chaque étape met en surbrillance une zone du schéma. Zones disponibles :
 *   "bouche", "estomac", "intestin", "foie", "sang", "coeur", "poumons", "cible", "rein", "peau"
 * Une même zone peut servir à plusieurs étapes (ex : "estomac" au début et à la fin pour les IPP).
 */
window.GUIDE = window.GUIDE || {};
GUIDE.animations = [
  {
    "id": "ains",
    "titre": "Comment agit un anti-inflammatoire (AINS), exemple de l'ibuprofène",
    "classe": "Anti-inflammatoires non stéroïdiens (AINS)",
    "introduction": "Cette animation suit un comprimé d'ibuprofène depuis la prise jusqu'à l'élimination. Elle montre aussi d'où viennent les principaux risques des AINS, utiles à connaître au comptoir.",
    "validation": {
      "par": "À COMPLÉTER",
      "le": "À COMPLÉTER"
    },
    "etapes": [
      {
        "zone": "bouche",
        "titre": "Étape 1 : la prise",
        "texte": "Le comprimé est avalé avec un verre d'eau, de préférence pendant un repas pour limiter l'irritation de l'estomac."
      },
      {
        "zone": "estomac",
        "titre": "Étape 2 : l'estomac, premier point de vigilance",
        "texte": "Les prostaglandines protègent normalement la paroi de l'estomac. En les diminuant partout dans le corps, les AINS fragilisent cette protection : c'est l'origine du risque de brûlures, d'ulcère et de saignement digestif."
      },
      {
        "zone": "intestin",
        "titre": "Étape 3 : l'absorption",
        "texte": "Le médicament passe de l'intestin vers le sang."
      },
      {
        "zone": "sang",
        "titre": "Étape 4 : le transport",
        "texte": "Le sang transporte le médicament dans tout le corps. L'effet sur la douleur apparaît en général dans l'heure qui suit la prise."
      },
      {
        "zone": "cible",
        "titre": "Étape 5 : l'action sur la douleur et l'inflammation",
        "texte": "Là où il y a douleur ou inflammation, des enzymes appelées COX fabriquent des prostaglandines, qui entretiennent la douleur, l'inflammation et la fièvre. L'AINS bloque les COX : moins de prostaglandines, donc moins de douleur, d'inflammation et de fièvre."
      },
      {
        "zone": "rein",
        "titre": "Étape 6 : l'élimination, second point de vigilance",
        "texte": "Le médicament, transformé par le foie, est éliminé dans les urines. Les prostaglandines aident aussi les reins à bien fonctionner : en cas de déshydratation, de maladie des reins ou d'association avec certains traitements de la tension ou diurétiques, l'AINS peut abîmer les reins."
      }
    ]
  },
  {
    "id": "ipp",
    "titre": "Comment agit un inhibiteur de la pompe à protons (IPP)",
    "classe": "Inhibiteurs de la pompe à protons (IPP)",
    "introduction": "Cette animation explique pourquoi un IPP ne soulage pas tout de suite et pourquoi il se prend avant un repas. Exemple : oméprazole.",
    "validation": {
      "par": "À COMPLÉTER",
      "le": "À COMPLÉTER"
    },
    "etapes": [
      {
        "zone": "bouche",
        "titre": "Étape 1 : la prise",
        "texte": "La gélule ou le comprimé est avalé entier, sans le croquer ni l'écraser, avant un repas (souvent le matin)."
      },
      {
        "zone": "estomac",
        "titre": "Étape 2 : traverser l'estomac sans être détruit",
        "texte": "Le médicament est fragile dans l'acide. Son enrobage gastro-résistant le protège pendant la traversée de l'estomac : c'est pourquoi il ne faut pas le croquer."
      },
      {
        "zone": "intestin",
        "titre": "Étape 3 : l'absorption",
        "texte": "L'enrobage se dissout dans l'intestin, moins acide, et le médicament passe dans le sang."
      },
      {
        "zone": "foie",
        "titre": "Étape 4 : le foie",
        "texte": "Le foie transforme le médicament grâce à des enzymes. Ces mêmes enzymes servent à d'autres médicaments, ce qui explique certaines interactions, par exemple entre l'oméprazole et le clopidogrel."
      },
      {
        "zone": "sang",
        "titre": "Étape 5 : le transport",
        "texte": "Le sang amène le médicament jusqu'aux cellules de la paroi de l'estomac qui fabriquent l'acide."
      },
      {
        "zone": "estomac",
        "titre": "Étape 6 : l'action sur les pompes à acide",
        "texte": "Ces cellules libèrent l'acide grâce à des « pompes à protons », activées par les repas. L'IPP bloque les pompes actives : moins d'acide, donc moins de brûlures. Toutes les pompes ne sont pas actives en même temps, d'où un effet complet après quelques jours. Pour un soulagement immédiat, un antiacide ou un alginate est plus adapté."
      }
    ]
  }
];
