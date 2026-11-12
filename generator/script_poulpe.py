"""Texte de la voix off : (scène, phrase(s) prononcée(s)). Une entrée = une scène animée."""
LINES = [
    ("hook", "Cet animal a trois cœurs. Et du sang bleu."),
    ("reveal", "C'est le poulpe. Et ce n'est que le début."),
    ("cuivre", "Son sang est bleu parce qu'il transporte l'oxygène avec du cuivre. Nous, on utilise du fer."),
    ("coeurs", "Deux de ses cœurs envoient le sang vers les branchies. Le troisième irrigue tout le reste du corps."),
    ("nage", "Quand il nage, ce troisième cœur s'arrête de battre. Voilà pourquoi il préfère ramper."),
    ("neurones", "Il possède environ cinq cents millions de neurones. Et les deux tiers sont dans ses bras."),
    ("bras", "Chaque bras peut toucher, goûter, et réagir sans attendre le cerveau."),
    ("couleurs", "Il change de couleur en une fraction de seconde. Pourtant, ses yeux ne voient probablement pas les couleurs."),
    ("bocal", "Il dévisse des bocaux, s'échappe des aquariums, et reconnaît certains humains."),
    ("vie", "Et malgré tout ça, la plupart des poulpes ne vivent qu'un ou deux ans."),
    ("outro", "Abonne-toi pour d'autres faits qui vont te retourner le cerveau."),
]

# mots mis en valeur dans les sous-titres (en jaune, plus gros)
KEYWORDS = {
    "trois", "cœurs.", "bleu.", "poulpe.", "début.", "cuivre.", "fer.", "branchies.", "troisième",
    "s'arrête", "ramper.", "cinq", "cents", "millions", "bras.", "goûter,", "cerveau.", "couleur",
    "seconde.", "couleurs.", "bocaux,", "aquariums,", "humains.", "deux", "ans.", "Abonne-toi",
}
