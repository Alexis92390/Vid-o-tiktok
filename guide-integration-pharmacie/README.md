# Guide d'intégration – apprentis préparateurs

Site interne, sans serveur ni installation. **Ouvrir `index.html` en double-cliquant dessus.**

- Aucun cookie, aucun outil de suivi, aucune requête vers Internet (bloquées par la page elle-même).
- Les scores des quiz sont enregistrés uniquement dans le navigateur de l'appareil (localStorage). Bouton « Effacer mes résultats » sur la page Quiz.
- Tout texte contenant **À COMPLÉTER** apparaît surligné en jaune : c'est la liste visuelle de ce qui manque.

## Organisation des fichiers

```
index.html          page unique du site (ne pas modifier sauf besoin)
css/style.css       apparence
js/app.js           fonctionnement (ne pas modifier pour changer le contenu)
data/               TOUT LE CONTENU, modifiable avec un éditeur de texte
  site.js           nom de l'officine, nom de la pharmacienne, texte d'accueil
  fiches.js         fiches par situation
  medicaments.js    tableau « Types de médicaments »
  animations.js     animations étape par étape
  quiz.js           quiz J0 et J30
  sources.js        sources de chaque contenu
  pages.js          pages libres supplémentaires
```

### Pourquoi des fichiers `.js` et pas `.json` ?

Les navigateurs interdisent de lire un fichier `.json` quand la page est ouverte par double-clic (adresse `file://`). Chaque fichier de `data/` contient donc du JSON précédé d'une ligne `GUIDE.xxx = ` et suivi d'un `;`. **Entre les deux, la syntaxe est exactement celle du JSON.**

### Règles d'édition (à respecter dans tous les fichiers `data/`)

1. Ouvrir le fichier avec un éditeur de texte (Bloc-notes, TextEdit en mode texte brut, VS Code). Pas avec Word.
2. Modifier uniquement le texte **entre guillemets droits** `"..."`.
3. Pour mettre un guillemet droit dans un texte, écrire `\"`. Les guillemets français « » s'écrivent normalement.
4. Séparer les éléments d'une liste par une virgule, **sans virgule après le dernier**.
5. Enregistrer en UTF-8, puis recharger la page (F5).
6. Si la page reste blanche ou affiche une erreur : il manque une virgule, un guillemet ou une accolade. Revenir à la dernière modification. Astuce : coller le contenu situé entre `=` et `;` sur un validateur JSON hors ligne (VS Code signale les erreurs directement).

## Modifier une fiche

Fichier : `data/fiches.js`. Une fiche :

```js
{
  "id": "situation-1",
  "titre": "Titre de la situation",
  "motif": "Description de la demande du patient.",
  "questions": ["Question 1", "Question 2"],
  "orientations": ["Orientation 1", "Orientation 2"],
  "vigilance": ["Point de vigilance 1"],
  "passerLaMain": ["Critère 1 : appeler le pharmacien si ..."],
  "validation": { "par": "Nom", "le": "2026-11-17" }
}
```

- **Modifier** : changer les textes entre guillemets.
- **Ajouter une fiche** : copier un bloc `{ ... }` entier, le coller après le dernier (avec une virgule entre les deux), changer l'`id` (court, sans espace ni accent, unique) et les textes. La fiche apparaît automatiquement dans la liste.
- **Supprimer une fiche** : effacer son bloc `{ ... }` et la virgule qui le sépare du voisin. Supprimer aussi ses sources dans `data/sources.js`.
- **Ajouter les sources d'une fiche** : dans `data/sources.js`, sous `"parFiche"`, utiliser l'`id` de la fiche comme clé.

Le tableau `data/medicaments.js` et les animations `data/animations.js` se modifient de la même façon (instructions en tête de chaque fichier). Zones disponibles pour les animations : `bouche`, `estomac`, `intestin`, `foie`, `sang`, `coeur`, `poumons`, `cible`, `rein`, `peau`.

## Modifier une question de quiz

Fichier : `data/quiz.js`. Une question :

```js
{
  "question": "Texte de la question ?",
  "choix": ["Réponse A", "Réponse B", "Réponse C", "Réponse D"],
  "bonneReponse": 2,
  "explication": "Pourquoi C est la bonne réponse."
}
```

- **`bonneReponse` compte à partir de 0** : 0 = première réponse, 1 = deuxième, 2 = troisième, 3 = quatrième. C'est l'erreur la plus fréquente : vérifier chaque question après modification en faisant le quiz.
- `choix` accepte de 2 à 6 réponses.
- Pour ajouter une question : copier un bloc `{ ... }`, le coller dans la liste `"questions"` avec une virgule. Le nombre de questions s'adapte automatiquement.
- Si vous changez beaucoup un quiz, les anciens scores restent affichés : demander aux apprentis de cliquer sur « Effacer mes résultats ».

## Ajouter une nouvelle page

Pour une page de texte (organisation, contacts, procédures) : fichier `data/pages.js`.

```js
{
  "id": "organisation",
  "titre": "Organisation du comptoir",
  "menu": true,
  "sections": [
    {
      "titre": "Ouverture",
      "paragraphes": ["Premier paragraphe.", "Deuxième paragraphe."],
      "liste": ["Point 1", "Point 2"]
    }
  ]
}
```

- `"menu": true` ajoute la page dans le menu ; `false` la rend accessible seulement par son adresse `index.html#/page/organisation`.
- Un exemple (`"id": "modele"`, hors menu) est déjà présent : on peut le copier.

Pour une page d'un type nouveau (autre chose que du texte, des listes ou les modèles existants), il faut ajouter une fonction d'affichage dans `js/app.js` (voir `viewPage` comme modèle) et une ligne dans la fonction `route`. Cela demande des notions de JavaScript.

## Avant mise en service

1. Remplacer tous les « À COMPLÉTER » (ouvrir chaque page : il ne doit plus rien rester en jaune).
2. Faire valider chaque fiche, le tableau, l'animation et les deux quiz par la pharmacienne, et remplir les champs `"validation"`.
3. Tester sur l'ordinateur et la tablette du comptoir, au clavier (touche Tab) et en faisant les deux quiz jusqu'au bout.
