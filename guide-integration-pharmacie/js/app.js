/*
 * Guide d'intégration — code du site.
 * Le contenu est dans le dossier data/ ; ce fichier ne contient que l'affichage.
 * Aucune requête réseau, aucun cookie. Seuls les scores des quiz sont gardés
 * dans le navigateur (localStorage), sur cet appareil uniquement.
 */
(function () {
  "use strict";

  var G = window.GUIDE || {};
  var site = G.site || {};
  var TODO = "À COMPLÉTER";
  var STORE_KEY = "guide-integration:quiz:v1";
  var app = document.getElementById("app");
  var SITE_TITLE = (site.nomOfficine || TODO) + " - Guide d'intégration";

  /* ---------- Construction du DOM (jamais d'innerHTML : le contenu est toujours traité comme du texte) ---------- */

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        var v = attrs[k];
        if (v === null || v === undefined || v === false) return;
        if (k === "class") node.className = v;
        else if (k.slice(0, 2) === "on" && typeof v === "function") node.addEventListener(k.slice(2), v);
        else if (v === true) node.setAttribute(k, "");
        else node.setAttribute(k, String(v));
      });
    }
    add(node, children);
    return node;
  }

  function add(node, c) {
    if (c === null || c === undefined || c === false) return;
    if (Array.isArray(c)) { c.forEach(function (x) { add(node, x); }); return; }
    if (typeof c === "string" || typeof c === "number") {
      var s = String(c);
      if (s.indexOf(TODO) !== -1) {
        // Les zones à compléter sont surlignées pour être repérées facilement.
        var m = document.createElement("mark");
        m.className = "todo";
        m.textContent = s;
        node.appendChild(m);
      } else {
        node.appendChild(document.createTextNode(s));
      }
      return;
    }
    node.appendChild(c);
  }

  function svg(tag, attrs, children) {
    var node = document.createElementNS("http://www.w3.org/2000/svg", tag);
    Object.keys(attrs || {}).forEach(function (k) { node.setAttribute(k, attrs[k]); });
    (children || []).forEach(function (c) {
      node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    });
    return node;
  }

  function list(items, ordered, cls) {
    items = Array.isArray(items) && items.length ? items : [TODO];
    return el(ordered ? "ol" : "ul", { class: cls }, items.map(function (t) { return el("li", null, t); }));
  }

  function shuffle(arr) {
    for (var i = arr.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = arr[i]; arr[i] = arr[j]; arr[j] = t;
    }
    return arr;
  }

  function hasTodo(obj) {
    return JSON.stringify(obj || "").indexOf(TODO) !== -1;
  }

  function validationLine(v) {
    v = v || {};
    return el("p", { class: "meta" }, ["Validé par : ", v.par || TODO, " — le : ", v.le || TODO]);
  }

  function todoBanner(text) {
    return el("p", { class: "callout callout-todo", role: "note" }, text);
  }

  function findById(arr, id) {
    return (arr || []).filter(function (x) { return x.id === id; })[0];
  }

  function card(href, title, text) {
    return el("li", null, el("a", { class: "card", href: href }, [el("span", { class: "card-title" }, title), text ? el("span", { class: "card-text" }, text) : null]));
  }

  // Saut vers une section de la page sans modifier l'adresse (le # sert au routage).
  function jumpTo(id) {
    return function (e) {
      var t = document.getElementById(id);
      if (!t) return;
      e.preventDefault();
      t.focus();
      t.scrollIntoView({ block: "start" });
    };
  }

  /* ---------- Stockage local des scores ---------- */

  function readScores() {
    try {
      var raw = window.localStorage.getItem(STORE_KEY);
      var data = raw ? JSON.parse(raw) : {};
      return data && typeof data === "object" ? data : {};
    } catch (e) { return {}; }
  }

  function saveScore(quizId, score, total) {
    try {
      var all = readScores();
      var entry = all[quizId] || { essais: [] };
      entry.essais = (entry.essais || []).concat([{ date: new Date().toISOString(), score: score, total: total }]).slice(-10);
      all[quizId] = entry;
      window.localStorage.setItem(STORE_KEY, JSON.stringify(all));
      return true;
    } catch (e) { return false; }
  }

  function clearScores() {
    try { window.localStorage.removeItem(STORE_KEY); } catch (e) { /* stockage indisponible */ }
  }

  function formatDate(iso) {
    try {
      return new Date(iso).toLocaleString("fr-FR", { dateStyle: "short", timeStyle: "short" });
    } catch (e) { return iso; }
  }

  /* ---------- Navigation ---------- */

  var NAV = [
    { href: "#/", label: "Accueil", key: "" },
    { href: "#/fiches", label: "Fiches par situation", key: "fiches" },
    { href: "#/medicaments", label: "Types de médicaments", key: "medicaments" },
    { href: "#/animations", label: "Animations", key: "animations" },
    { href: "#/quiz", label: "Quiz", key: "quiz" },
    { href: "#/sources", label: "Sources", key: "sources" }
  ];
  (G.pages || []).forEach(function (p) {
    if (p.menu) NAV.push({ href: "#/page/" + encodeURIComponent(p.id), label: p.titre, key: "page/" + p.id });
  });

  var SECTION_OF = { fiche: "fiches", animation: "animations" };

  function buildNav() {
    var ul = document.getElementById("nav-list");
    NAV.forEach(function (n) {
      ul.appendChild(el("li", null, el("a", { href: n.href, "data-key": n.key }, n.label)));
    });
    var toggle = document.querySelector(".nav-toggle");
    var nav = document.getElementById("main-nav");
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      nav.classList.toggle("open", !open);
    });
    nav.addEventListener("click", function (e) {
      if (e.target.tagName === "A") { toggle.setAttribute("aria-expanded", "false"); nav.classList.remove("open"); }
    });
    document.getElementById("brand").textContent = SITE_TITLE;
    document.getElementById("footer-text").textContent = avertissement();
  }

  function setCurrentNav(key) {
    document.querySelectorAll("#nav-list a").forEach(function (a) {
      if (a.getAttribute("data-key") === key) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
  }

  function avertissement() {
    return (site.avertissement || "Contenu à usage interne, validé par {pharmacienne}. Ne pas diffuser aux patients.")
      .replace("{pharmacienne}", site.nomPharmacienne || TODO);
  }

  /* ---------- Vues ---------- */

  function viewHome() {
    return {
      title: "Accueil",
      node: el("div", null, [
        el("h1", null, SITE_TITLE),
        el("p", { class: "callout callout-warning", role: "note" }, [el("strong", null, "Avertissement : "), avertissement()]),
        site.brouillon ? el("p", { class: "callout callout-todo", role: "note" }, el("strong", null, site.brouillon)) : null,
        el("p", { class: "lead" }, site.presentation || TODO),
        el("h2", null, "Mode d'emploi"),
        list(site.modeEmploi, true, "steps-list"),
        el("h2", null, "Accès rapide"),
        el("ul", { class: "cards" }, [
          card("#/fiches", "Fiches par situation", "Questions à poser, orientations, quand passer la main."),
          card("#/medicaments", "Types de médicaments", "Classes, rôles, exemples, vigilance."),
          card("#/animations", "Animations", "Comment agit une classe de médicaments, étape par étape."),
          card("#/quiz", "Quiz J0 et J30", "Vérifiez vos acquis. Les scores restent sur cet appareil."),
          card("#/sources", "Sources", "Notices et documents de référence.")
        ])
      ])
    };
  }

  function viewFiches() {
    var fiches = G.fiches || [];
    return {
      title: "Fiches par situation",
      node: el("div", null, [
        el("h1", null, "Fiches par situation"),
        el("p", null, "Choisissez la situation qui correspond à la demande du patient."),
        fiches.length
          ? el("ul", { class: "cards" }, fiches.map(function (f) { return card("#/fiche/" + encodeURIComponent(f.id), f.titre || TODO, f.motif); }))
          : todoBanner(TODO + " : aucune fiche dans data/fiches.js.")
      ])
    };
  }

  function viewFiche(id) {
    var fiches = G.fiches || [];
    var f = findById(fiches, id);
    if (!f) return viewNotFound();
    var i = fiches.indexOf(f);
    var prev = fiches[i - 1], next = fiches[i + 1];
    return {
      title: f.titre || "Fiche",
      section: "fiches",
      node: el("article", { class: "fiche" }, [
        el("p", { class: "breadcrumb" }, el("a", { href: "#/fiches" }, "← Toutes les fiches")),
        el("h1", null, f.titre || TODO),
        validationLine(f.validation),
        hasTodo(f) ? todoBanner("Cette fiche contient des éléments à compléter. Ne l'utilisez pas au comptoir avant validation par la pharmacienne.") : null,
        el("p", null, el("a", { href: "#passer-la-main", class: "jump", onclick: jumpTo("passer-la-main") }, "Aller directement à « Quand passer la main au pharmacien »")),
        el("section", { "aria-labelledby": "h-motif" }, [el("h2", { id: "h-motif" }, "Motif de la demande"), el("p", null, f.motif || TODO)]),
        el("section", { "aria-labelledby": "h-questions" }, [el("h2", { id: "h-questions" }, "Questions à poser au patient"), list(f.questions, true)]),
        el("section", { "aria-labelledby": "h-orient" }, [el("h2", { id: "h-orient" }, "Orientations possibles"), list(f.orientations)]),
        el("section", { class: "callout callout-warning", "aria-labelledby": "h-vigil" }, [el("h2", { id: "h-vigil" }, "Points de vigilance"), list(f.vigilance)]),
        el("section", { class: "callout callout-alert", id: "passer-la-main", tabindex: "-1", "aria-labelledby": "h-main" }, [
          el("h2", { id: "h-main" }, "Quand passer la main au pharmacien"),
          list(f.passerLaMain)
        ]),
        el("p", null, el("a", { href: "#/sources/" + encodeURIComponent(f.id) }, "Voir les sources de cette fiche")),
        el("nav", { class: "pager", "aria-label": "Fiches précédente et suivante" }, [
          prev ? el("a", { href: "#/fiche/" + encodeURIComponent(prev.id), rel: "prev" }, "← " + (prev.titre || "Précédente")) : el("span"),
          next ? el("a", { href: "#/fiche/" + encodeURIComponent(next.id), rel: "next" }, (next.titre || "Suivante") + " →") : el("span")
        ])
      ])
    };
  }

  function viewMedicaments() {
    var m = G.medicaments || {};
    var rows = m.lignes || [];
    return {
      title: "Types de médicaments",
      node: el("div", null, [
        el("h1", null, "Types de médicaments"),
        validationLine(m.validation),
        hasTodo(m) ? todoBanner("Ce tableau contient des éléments à compléter.") : null,
        m.introduction ? el("p", null, m.introduction) : null,
        el("div", { class: "table-wrap", role: "region", "aria-labelledby": "tab-caption", tabindex: "0" },
          el("table", null, [
            el("caption", { id: "tab-caption" }, "Classes de médicaments : rôle, exemples et points de vigilance"),
            el("thead", null, el("tr", null, ["Classe", "Rôle", "Exemples de médicaments", "Points de vigilance"].map(function (h) {
              return el("th", { scope: "col" }, h);
            }))),
            el("tbody", null, rows.map(function (r) {
              return el("tr", null, [
                el("th", { scope: "row" }, r.classe || TODO),
                el("td", { "data-label": "Rôle" }, r.role || TODO),
                el("td", { "data-label": "Exemples" }, list(r.exemples, false, "compact")),
                el("td", { "data-label": "Vigilance" }, list(r.vigilance, false, "compact"))
              ]);
            }))
          ])
        ),
        el("p", null, el("a", { href: "#/sources/medicaments" }, "Voir les sources de ce tableau"))
      ])
    };
  }

  function viewAnimations() {
    var anims = G.animations || [];
    return {
      title: "Animations",
      node: el("div", null, [
        el("h1", null, "Animations"),
        el("p", null, "Chaque animation montre, étape par étape, comment agit une classe de médicaments. Avancez à votre rythme avec les boutons ou les flèches du clavier."),
        anims.length
          ? el("ul", { class: "cards" }, anims.map(function (a) { return card("#/animation/" + encodeURIComponent(a.id), a.titre || TODO, a.classe); }))
          : todoBanner(TODO + " : aucune animation dans data/animations.js.")
      ])
    };
  }

  /* Schéma du corps : zones génériques (positions dans un repère 0–400 × 0–520). */
  var ZONES = {
    bouche:   { label: "Bouche",        x: 200, y: 62 },
    poumons:  { label: "Poumons",       x: 145, y: 165 },
    coeur:    { label: "Cœur",          x: 228, y: 172 },
    sang:     { label: "Sang",          x: 305, y: 185 },
    foie:     { label: "Foie",          x: 150, y: 245 },
    estomac:  { label: "Estomac",       x: 235, y: 255 },
    rein:     { label: "Reins",         x: 105, y: 305 },
    intestin: { label: "Intestin",      x: 200, y: 335 },
    cible:    { label: "Organe cible",  x: 300, y: 400 },
    peau:     { label: "Peau",          x: 92,  y: 420 }
  };

  function viewAnimation(id) {
    var a = findById(G.animations, id);
    if (!a) return viewNotFound();
    var steps = (a.etapes && a.etapes.length) ? a.etapes : [{ zone: "", titre: TODO, texte: TODO }];
    var current = 0;
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    // Zones utilisées par cette animation uniquement (le schéma reste lisible).
    var used = {};
    steps.forEach(function (s) { if (ZONES[s.zone]) used[s.zone] = true; });

    var svgTitle = svg("title", { id: "anim-svg-title" });
    var svgDesc = svg("desc", { id: "anim-svg-desc" });
    var zoneNodes = {};
    var zoneGroup = svg("g", {});
    Object.keys(used).forEach(function (k) {
      var z = ZONES[k];
      var g = svg("g", { class: "zone", "data-zone": k }, [
        svg("circle", { cx: z.x, cy: z.y, r: 22, class: "zone-dot" }),
        svg("text", { x: z.x, y: z.y + 40, class: "zone-label", "text-anchor": "middle" }, [z.label])
      ]);
      zoneNodes[k] = g;
      zoneGroup.appendChild(g);
    });
    var molecule = svg("g", { class: "molecule" + (reduce ? " no-motion" : "") }, [svg("circle", { r: 10, cx: 0, cy: 0 })]);

    var figure = svg("svg", {
      viewBox: "0 0 400 520", class: "body-diagram", role: "img",
      "aria-labelledby": "anim-svg-title anim-svg-desc", focusable: "false"
    }, [
      svgTitle, svgDesc,
      // Silhouette neutre
      svg("g", { class: "silhouette", "aria-hidden": "true" }, [
        svg("circle", { cx: 200, cy: 60, r: 42 }),
        svg("rect", { x: 182, y: 98, width: 36, height: 22, rx: 8 }),
        svg("rect", { x: 110, y: 115, width: 180, height: 270, rx: 60 }),
        svg("rect", { x: 62, y: 130, width: 40, height: 200, rx: 20 }),
        svg("rect", { x: 298, y: 130, width: 40, height: 200, rx: 20 }),
        svg("rect", { x: 128, y: 370, width: 58, height: 140, rx: 24 }),
        svg("rect", { x: 214, y: 370, width: 58, height: 140, rx: 24 })
      ]),
      zoneGroup,
      molecule
    ]);

    var counter = el("p", { class: "step-counter" });
    var stepTitle = el("h2", { class: "step-title" });
    var stepText = el("p", { class: "step-text" });
    var live = el("div", { class: "step-panel", "aria-live": "polite", "aria-atomic": "true" }, [counter, stepTitle, stepText]);
    var dots = el("ol", { class: "step-dots", "aria-hidden": "true" }, steps.map(function () { return el("li"); }));

    var btnPrev = el("button", { type: "button", class: "btn", onclick: function () { go(current - 1); } }, "← Étape précédente");
    var btnNext = el("button", { type: "button", class: "btn btn-primary", onclick: function () { go(current + 1); } }, "Étape suivante →");
    var btnReset = el("button", { type: "button", class: "btn btn-ghost", onclick: function () { go(0); btnNext.focus(); } }, "Recommencer");

    function setText(node, s) { node.textContent = ""; add(node, s || TODO); }

    function go(n) {
      current = Math.max(0, Math.min(steps.length - 1, n));
      var s = steps[current];
      counter.textContent = "Étape " + (current + 1) + " sur " + steps.length;
      setText(stepTitle, s.titre);
      setText(stepText, s.texte);
      svgTitle.textContent = (a.titre || "Animation") + " — étape " + (current + 1) + " sur " + steps.length;
      var z = ZONES[s.zone];
      svgDesc.textContent = (s.titre || "") + ". " + (z ? "Zone mise en évidence : " + z.label + ". " : "") + (s.texte || "");
      Object.keys(zoneNodes).forEach(function (k) { zoneNodes[k].classList.toggle("active", k === s.zone); });
      if (z) { molecule.style.transform = "translate(" + z.x + "px," + z.y + "px)"; molecule.style.opacity = "1"; }
      else molecule.style.opacity = "0";
      Array.prototype.forEach.call(dots.children, function (li, i) {
        li.className = i === current ? "current" : (i < current ? "done" : "");
      });
      btnPrev.disabled = current === 0;
      btnNext.disabled = current === steps.length - 1;
    }

    var region = el("section", {
      class: "animation", "aria-label": "Animation interactive",
      onkeydown: function (e) {
        if (e.key === "ArrowRight") { go(current + 1); e.preventDefault(); }
        else if (e.key === "ArrowLeft") { go(current - 1); e.preventDefault(); }
      }
    }, [
      el("div", { class: "animation-figure" }, figure),
      el("div", { class: "animation-side" }, [
        dots, live,
        el("div", { class: "controls" }, [btnPrev, btnNext, btnReset]),
        el("p", { class: "hint" }, "Astuce : les flèches ← et → du clavier font aussi avancer l'animation.")
      ])
    ]);

    go(0);

    return {
      title: a.titre || "Animation",
      section: "animations",
      node: el("div", null, [
        el("p", { class: "breadcrumb" }, el("a", { href: "#/animations" }, "← Toutes les animations")),
        el("h1", null, a.titre || TODO),
        validationLine(a.validation),
        hasTodo(a) ? todoBanner("Cette animation contient des éléments à compléter, y compris l'enchaînement des zones du schéma.") : null,
        el("p", null, a.introduction || TODO),
        region,
        el("details", { class: "text-version" }, [
          el("summary", null, "Version texte de toute l'animation"),
          el("ol", null, steps.map(function (s) {
            var z = ZONES[s.zone];
            return el("li", null, [el("strong", null, s.titre || TODO), z ? " (" + z.label + ")" : "", " : ", s.texte || TODO]);
          }))
        ]),
        el("p", null, el("a", { href: "#/sources/" + encodeURIComponent(a.id) }, "Voir les sources de cette animation"))
      ])
    };
  }

  function viewQuizList() {
    var quizzes = G.quiz || [];
    var scores = readScores();
    var status = el("p", { class: "visually-hidden", "aria-live": "polite" });
    var tableBody = el("tbody");

    function fillHistory() {
      scores = readScores();
      tableBody.textContent = "";
      quizzes.forEach(function (q) {
        var essais = (scores[q.id] && scores[q.id].essais) || [];
        var last = essais[essais.length - 1];
        var best = essais.reduce(function (b, e) { return !b || e.score / e.total > b.score / b.total ? e : b; }, null);
        tableBody.appendChild(el("tr", null, [
          el("th", { scope: "row" }, q.titre || q.id),
          el("td", null, last ? last.score + " / " + last.total + " (" + formatDate(last.date) + ")" : "Pas encore fait"),
          el("td", null, best ? best.score + " / " + best.total : "—"),
          el("td", null, String(essais.length))
        ]));
      });
    }
    fillHistory();

    return {
      title: "Quiz",
      node: el("div", null, [
        el("h1", null, "Quiz"),
        el("p", null, "Deux quiz de dix questions : le quiz J0 à faire le premier jour, le quiz J30 après un mois. Chaque réponse est corrigée immédiatement."),
        el("ul", { class: "cards" }, quizzes.map(function (q) {
          return card("#/quiz/" + encodeURIComponent(q.id), q.titre || q.id, q.description);
        })),
        el("h2", null, "Mes résultats sur cet appareil"),
        el("div", { class: "table-wrap", role: "region", "aria-label": "Mes résultats", tabindex: "0" }, el("table", null, [
          el("thead", null, el("tr", null, ["Quiz", "Dernier score", "Meilleur score", "Essais"].map(function (h) { return el("th", { scope: "col" }, h); }))),
          tableBody
        ])),
        el("p", { class: "meta" }, "Ces résultats sont enregistrés uniquement dans ce navigateur. Ils ne sont jamais envoyés et personne d'autre ne les voit."),
        el("button", { type: "button", class: "btn btn-ghost", onclick: function () {
          if (window.confirm("Effacer tous vos résultats de quiz sur cet appareil ?")) {
            clearScores(); fillHistory(); status.textContent = "Résultats effacés.";
          }
        } }, "Effacer mes résultats"),
        status
      ])
    };
  }

  function viewQuiz(id) {
    var q = findById(G.quiz, id);
    if (!q) return viewNotFound();
    var questions = q.questions || [];
    var idx = 0, score = 0, answered = false;
    var stage = el("div", { class: "quiz-stage" });
    var feedback = el("div", { class: "quiz-feedback", "aria-live": "polite" });

    function renderQuestion() {
      answered = false;
      var item = questions[idx];
      var name = "q-" + idx;
      var choices = Array.isArray(item.choix) ? item.choix : [];
      var actionBtn = el("button", { type: "submit", class: "btn btn-primary" }, "Valider ma réponse");
      var error = el("p", { class: "form-error", "aria-live": "assertive" });

      var form = el("form", { class: "quiz-form", novalidate: true }, [
        el("fieldset", null, [
          el("legend", null, [el("span", { class: "step-counter" }, "Question " + (idx + 1) + " sur " + questions.length), el("span", { class: "quiz-question" }, item.question || TODO)]),
          // Réponses mélangées à chaque affichage ; "value" garde la position d'origine (celle de bonneReponse).
          el("div", { class: "choices" }, shuffle(choices.map(function (c, i) { return i; })).map(function (i) {
            var c = choices[i];
            var cid = name + "-" + i;
            return el("div", { class: "choice", "data-index": String(i) }, [
              el("input", { type: "radio", name: name, id: cid, value: String(i) }),
              el("label", { for: cid }, c)
            ]);
          }))
        ]),
        error,
        el("div", { class: "controls" }, actionBtn)
      ]);

      form.addEventListener("submit", function (e) {
        e.preventDefault();
        if (answered) { next(); return; }
        var picked = form.querySelector("input:checked");
        if (!picked) { error.textContent = "Choisissez une réponse avant de valider."; return; }
        error.textContent = "";
        answered = true;
        var chosen = Number(picked.value);
        var good = Number(item.bonneReponse);
        var ok = chosen === good;
        if (ok) score++;
        form.querySelectorAll("input").forEach(function (inp) { inp.disabled = true; });
        form.querySelectorAll(".choice").forEach(function (div) {
          var i = Number(div.getAttribute("data-index"));
          if (i === good) { div.classList.add("is-correct"); div.appendChild(el("span", { class: "tag tag-ok" }, "Bonne réponse")); }
          else if (i === chosen) { div.classList.add("is-wrong"); div.appendChild(el("span", { class: "tag tag-ko" }, "Votre réponse")); }
        });
        feedback.textContent = "";
        add(feedback, el("div", { class: "callout " + (ok ? "callout-ok" : "callout-alert") }, [
          el("p", null, el("strong", null, ok ? "Correct." : "Incorrect. La bonne réponse est : " + (choices[good] !== undefined ? choices[good] : TODO))),
          el("p", null, item.explication || TODO)
        ]));
        actionBtn.textContent = idx < questions.length - 1 ? "Question suivante →" : "Voir mon score";
        actionBtn.focus();
      });

      stage.textContent = "";
      feedback.textContent = "";
      stage.appendChild(form);
      var first = form.querySelector("input");
      if (first && idx > 0) first.focus();
    }

    function next() {
      idx++;
      if (idx < questions.length) renderQuestion(); else renderEnd();
    }

    function renderEnd() {
      var saved = saveScore(q.id, score, questions.length);
      feedback.textContent = "";
      stage.textContent = "";
      var heading = el("h2", { tabindex: "-1" }, "Score final : " + score + " / " + questions.length);
      add(stage, el("div", { class: "quiz-end" }, [
        heading,
        el("p", null, saved ? "Score enregistré sur cet appareil uniquement." : "Le score n'a pas pu être enregistré (stockage du navigateur indisponible). Il n'est envoyé nulle part."),
        el("div", { class: "controls" }, [
          el("button", { type: "button", class: "btn btn-primary", onclick: function () { idx = 0; score = 0; renderQuestion(); stage.querySelector("input") && stage.querySelector("input").focus(); } }, "Recommencer ce quiz"),
          el("a", { class: "btn btn-ghost", href: "#/quiz" }, "Retour aux quiz")
        ])
      ]));
      heading.focus();
    }

    var body = el("div", null, [
      el("p", { class: "breadcrumb" }, el("a", { href: "#/quiz" }, "← Tous les quiz")),
      el("h1", null, q.titre || TODO),
      hasTodo(q) ? todoBanner("Ce quiz contient des questions ou réponses à compléter : le score n'est pas significatif.") : null,
      q.description ? el("p", null, q.description) : null,
      stage,
      feedback
    ]);
    if (questions.length) renderQuestion(); else add(stage, todoBanner(TODO + " : aucune question dans ce quiz."));
    return { title: q.titre || "Quiz", section: "quiz", node: body };
  }

  function refList(refs) {
    refs = refs && refs.length ? refs : [{ titre: TODO }];
    return el("ul", { class: "refs" }, refs.map(function (r) {
      var safe = typeof r.lien === "string" && /^https?:\/\//i.test(r.lien);
      return el("li", null, [
        safe ? el("a", { href: r.lien, target: "_blank", rel: "noopener noreferrer" }, r.titre || r.lien) : el("span", null, r.titre || TODO),
        r.type ? el("span", { class: "meta" }, " — " + r.type) : null,
        r.consulteLe ? el("span", { class: "meta" }, " — consulté le " + r.consulteLe) : null
      ]);
    }));
  }

  function labelForSourceKey(key) {
    var f = findById(G.fiches, key);
    if (f) return { label: "Fiche : " + (f.titre || key), href: "#/fiche/" + encodeURIComponent(key) };
    var a = findById(G.animations, key);
    if (a) return { label: "Animation : " + (a.titre || key), href: "#/animation/" + encodeURIComponent(key) };
    if (key === "medicaments") return { label: "Tableau « Types de médicaments »", href: "#/medicaments" };
    var qz = key.indexOf("quiz-") === 0 && findById(G.quiz, key.slice(5));
    if (qz) return { label: qz.titre || key, href: "#/quiz/" + encodeURIComponent(qz.id) };
    return { label: key, href: null };
  }

  function viewSources(focusKey) {
    var s = G.sources || {};
    var par = s.parFiche || {};
    var sections = Object.keys(par).map(function (k) {
      var info = labelForSourceKey(k);
      return el("section", { id: "src-" + k, tabindex: "-1", class: "source-block" }, [
        el("h3", null, info.href ? el("a", { href: info.href }, info.label) : info.label),
        refList(par[k])
      ]);
    });
    var node = el("div", null, [
      el("h1", null, "Sources"),
      el("p", null, "Notices, bases officielles et documents de référence utilisés pour rédiger chaque contenu du guide."),
      hasTodo(s) ? todoBanner("Des sources restent à compléter.") : null,
      el("h2", null, "Sources générales"),
      refList(s.generales),
      el("h2", null, "Sources par contenu"),
      sections
    ]);
    return { title: "Sources", section: "sources", node: node, focusId: focusKey ? "src-" + focusKey : null };
  }

  function viewPage(id) {
    var p = findById(G.pages, id);
    if (!p) return viewNotFound();
    return {
      title: p.titre || "Page",
      section: "page/" + p.id,
      node: el("div", null, [
        el("h1", null, p.titre || TODO),
        (p.sections || []).map(function (sec) {
          return el("section", null, [
            sec.titre ? el("h2", null, sec.titre) : null,
            (sec.paragraphes || []).map(function (t) { return el("p", null, t); }),
            sec.liste && sec.liste.length ? list(sec.liste) : null
          ]);
        })
      ])
    };
  }

  function viewNotFound() {
    return {
      title: "Page introuvable",
      node: el("div", null, [el("h1", null, "Page introuvable"), el("p", null, el("a", { href: "#/" }, "Retour à l'accueil"))])
    };
  }

  /* ---------- Routeur (adresse après le #) ---------- */

  var firstRender = true;

  function route() {
    var parts = location.hash.replace(/^#\/?/, "").split("/").map(function (p) {
      try { return decodeURIComponent(p); } catch (e) { return p; }
    });
    var section = parts[0] || "", id = parts[1];

    // Ancre classique (ex. #main) : si l'élément existe on y va, sinon on affiche l'accueil.
    if (location.hash && location.hash.indexOf("#/") !== 0) {
      var target = document.getElementById(location.hash.slice(1));
      if (target && app.firstChild && !firstRender) { target.focus(); return; }
      section = "";
    }

    var v;
    switch (section) {
      case "": v = viewHome(); break;
      case "fiches": v = viewFiches(); break;
      case "fiche": v = viewFiche(id); break;
      case "medicaments": v = viewMedicaments(); break;
      case "animations": v = viewAnimations(); break;
      case "animation": v = viewAnimation(id); break;
      case "quiz": v = id ? viewQuiz(id) : viewQuizList(); break;
      case "sources": v = viewSources(id); break;
      case "page": v = viewPage(id); break;
      default: v = viewNotFound();
    }

    app.textContent = "";
    app.appendChild(v.node);
    document.title = v.title + " – " + SITE_TITLE;
    setCurrentNav(v.section || SECTION_OF[section] || section);

    var focusTarget = (v.focusId && document.getElementById(v.focusId)) || null;
    if (focusTarget) {
      focusTarget.focus();
      focusTarget.scrollIntoView();
    } else if (!firstRender) {
      var h1 = app.querySelector("h1");
      if (h1) { h1.setAttribute("tabindex", "-1"); h1.focus(); }
      window.scrollTo(0, 0);
    }
    firstRender = false;
  }

  buildNav();
  document.querySelector(".skip-link").addEventListener("click", jumpTo("main"));
  window.addEventListener("hashchange", route);
  route();
})();
