/* Droit belge, expliqué — script unique, sans dépendance. */
(function () {
  "use strict";

  var BASE = window.DB_BASE || "";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* --- stockage tolérant aux navigateurs verrouillés ------------------ */
  var mem = {};
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return mem[k] || null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) { mem[k] = v; } }
  };

  /* --- thème ---------------------------------------------------------- */
  var root = document.documentElement;
  var tBtn = $("#theme-toggle");
  if (tBtn) {
    tBtn.addEventListener("click", function () {
      var cur = root.getAttribute("data-theme");
      if (cur === "auto") {
        cur = matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      }
      var next = cur === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      store.set("db-theme", next);
    });
  }

  /* --- menu mobile ---------------------------------------------------- */
  var side = $("#sidenav"), mBtn = $("#menu-open");
  if (mBtn && side) {
    mBtn.addEventListener("click", function () {
      var open = side.classList.toggle("open");
      mBtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("click", function (e) {
      if (!side.classList.contains("open")) return;
      if (side.contains(e.target) || mBtn.contains(e.target)) return;
      side.classList.remove("open");
      mBtn.setAttribute("aria-expanded", "false");
    });
  }

  /* --- barre de progression + sommaire actif -------------------------- */
  var bar = $("#readbar span");
  var article = $(".chapter article");
  var tocLinks = $$(".onthis a");
  var heads = tocLinks.length ? $$(".chapter h2[id], .chapter h3[id]") : [];

  function onScroll() {
    if (bar && article) {
      var top = article.offsetTop;
      var h = article.offsetHeight - window.innerHeight * 0.6;
      var p = h > 0 ? (window.scrollY - top) / h : 0;
      bar.style.width = Math.max(0, Math.min(1, p)) * 100 + "%";
    }
    if (heads.length) {
      var y = window.scrollY + 120, cur = heads[0];
      for (var i = 0; i < heads.length; i++) { if (heads[i].offsetTop <= y) cur = heads[i]; }
      tocLinks.forEach(function (a) {
        a.classList.toggle("on", a.getAttribute("href") === "#" + cur.id);
      });
    }
  }
  var ticking = false;
  window.addEventListener("scroll", function () {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () { onScroll(); ticking = false; });
  }, { passive: true });
  onScroll();

  /* --- copie du lien de section --------------------------------------- */
  $$(".sec-ref").forEach(function (a) {
    a.addEventListener("click", function (e) {
      var url = location.href.split("#")[0] + a.getAttribute("href");
      if (navigator.clipboard) {
        e.preventDefault();
        navigator.clipboard.writeText(url).then(function () {
          history.replaceState(null, "", a.getAttribute("href"));
          var old = a.innerHTML;
          a.innerHTML = "lien copié";
          setTimeout(function () { a.innerHTML = old; }, 1200);
          document.getElementById(a.getAttribute("href").slice(1)).scrollIntoView();
        });
      }
    });
  });

  /* --- recherche ------------------------------------------------------ */
  var sbox = $("#searchbox"), sInput = $("#search-input"), sRes = $("#search-results");
  var idx = null, loading = false;

  function normalize(s) {
    return s.toLowerCase()
      .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9\s]/g, " ");
  }

  function loadIndex(cb) {
    if (idx) { cb(); return; }
    if (loading) return;
    loading = true;
    fetch(BASE + "assets/js/search-index.json")
      .then(function (r) { return r.json(); })
      .then(function (d) {
        idx = d.map(function (o) { o._n = normalize(o.t + " " + o.c + " " + o.s); return o; });
        loading = false; cb();
      })
      .catch(function () {
        loading = false;
        sRes.innerHTML = '<p class="sb-empty">Index indisponible. Rechargez la page.</p>';
      });
  }

  function openSearch() {
    if (!sbox) return;
    sbox.hidden = false;
    document.body.style.overflow = "hidden";
    sInput.focus();
    sInput.select();
    loadIndex(function () { runSearch(); });
  }
  function closeSearch() {
    if (!sbox) return;
    sbox.hidden = true;
    document.body.style.overflow = "";
  }

  function highlight(text, words) {
    var out = text;
    words.forEach(function (w) {
      if (w.length < 3) return;
      var re = new RegExp("(" + w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig");
      out = out.replace(re, "<mark>$1</mark>");
    });
    return out;
  }

  function runSearch() {
    if (!idx) return;
    var q = normalize(sInput.value).trim();
    if (q.length < 2) {
      sRes.innerHTML = '<p class="sb-empty">Tapez au moins deux lettres. Essayez « cassation », « arrêté royal », « prescription », « Moniteur ».</p>';
      return;
    }
    var words = q.split(/\s+/).filter(Boolean);
    var hits = [];
    for (var i = 0; i < idx.length; i++) {
      var d = idx[i], score = 0;
      for (var j = 0; j < words.length; j++) {
        var w = words[j];
        var pos = d._n.indexOf(w);
        if (pos === -1) { score = 0; break; }
        score += 3;
        if (normalize(d.s).indexOf(w) !== -1) score += 6;
        if (normalize(d.c).indexOf(w) !== -1) score += 4;
        if (pos < 160) score += 1;
      }
      if (score > 0) hits.push({ d: d, s: score });
    }
    hits.sort(function (a, b) { return b.s - a.s; });
    if (!hits.length) {
      sRes.innerHTML = '<p class="sb-empty">Aucun résultat pour « ' + sInput.value.replace(/</g, "&lt;") + ' ».</p>';
      return;
    }
    var html = hits.slice(0, 24).map(function (h) {
      var d = h.d;
      var pos = d._n.indexOf(words[0]);
      var start = Math.max(0, pos - 70);
      var snip = (start > 0 ? "…" : "") + d.t.slice(start, start + 210) + "…";
      var src = d.c + (d.s ? " · " + d.s : "");
      return '<a class="sb-item" href="' + BASE + d.u + '"><span class="sb-src">' +
        src.replace(/</g, "&lt;") + '</span><p class="sb-txt">' +
        highlight(snip.replace(/</g, "&lt;"), words) + "</p></a>";
    }).join("");
    sRes.innerHTML = html;
  }

  if (sInput) {
    var deb;
    sInput.addEventListener("input", function () {
      clearTimeout(deb);
      deb = setTimeout(runSearch, 90);
    });
    sInput.addEventListener("keydown", function (e) {
      var items = $$(".sb-item", sRes);
      var cur = items.findIndex(function (n) { return n.classList.contains("on"); });
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        if (!items.length) return;
        if (cur >= 0) items[cur].classList.remove("on");
        var nx = e.key === "ArrowDown" ? (cur + 1) % items.length : (cur <= 0 ? items.length - 1 : cur - 1);
        items[nx].classList.add("on");
        items[nx].scrollIntoView({ block: "nearest" });
      } else if (e.key === "Enter") {
        if (cur >= 0) { e.preventDefault(); items[cur].click(); }
        else if (items.length) { e.preventDefault(); items[0].click(); }
      }
    });
  }
  if ($("#search-open")) $("#search-open").addEventListener("click", openSearch);
  if ($("#search-close")) $("#search-close").addEventListener("click", closeSearch);
  if (sbox) sbox.addEventListener("click", function (e) { if (e.target === sbox) closeSearch(); });

  document.addEventListener("keydown", function (e) {
    var tag = (e.target.tagName || "").toLowerCase();
    var typing = tag === "input" || tag === "textarea" || tag === "select";
    if (e.key === "Escape") { closeSearch(); hidePop(); return; }
    if ((e.key === "/" && !typing) || ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k")) {
      e.preventDefault(); openSearch();
    }
  });

  /* --- définitions au survol ------------------------------------------ */
  var pop = $("#dfn-pop"), gloss = null;
  function hidePop() { if (pop) pop.hidden = true; }
  function showPop(el) {
    if (!pop || !gloss) return;
    var key = (el.getAttribute("data-t") || el.textContent).toLowerCase().trim();
    var g = gloss[key];
    if (!g) return;
    pop.innerHTML = "<b>" + g.t + "</b>" + g.d;
    pop.hidden = false;
    var r = el.getBoundingClientRect();
    var top = r.bottom + window.scrollY + 8;
    var left = Math.min(r.left + window.scrollX, window.innerWidth - pop.offsetWidth - 16);
    pop.style.top = top + "px";
    pop.style.left = Math.max(8, left) + "px";
  }
  var dfns = $$("dfn");
  if (dfns.length) {
    fetch(BASE + "assets/js/glossaire.json").then(function (r) { return r.json(); }).then(function (d) {
      gloss = {};
      d.forEach(function (g) { gloss[g.t.toLowerCase()] = { t: g.t, d: g.d }; });
      dfns.forEach(function (el) {
        el.setAttribute("tabindex", "0");
        el.addEventListener("mouseenter", function () { showPop(el); });
        el.addEventListener("focus", function () { showPop(el); });
        el.addEventListener("mouseleave", hidePop);
        el.addEventListener("blur", hidePop);
      });
    }).catch(function () {});
  }
  window.addEventListener("scroll", hidePop, { passive: true });

  /* --- pile « hiérarchie des normes » (accueil) ------------------------ */
  var stack = $("#stack");
  if (stack) {
    var note = $("#stack-note");
    var lvls = $$(".lvl", stack);
    function pick(b) {
      lvls.forEach(function (x) { x.setAttribute("aria-expanded", x === b ? "true" : "false"); });
      note.innerHTML = "<b>" + b.getAttribute("data-t") + "</b> " + b.getAttribute("data-d");
    }
    lvls.forEach(function (b) {
      b.addEventListener("click", function () { pick(b); });
      b.addEventListener("mouseenter", function () { pick(b); });
    });
    pick(lvls[0]);
  }

  /* --- glossaire : filtre --------------------------------------------- */
  var gf = $("#gl-filter");
  if (gf) {
    var items = $$(".gl-item");
    var letters = $$(".gl-letter");
    var count = $("#gl-count");
    function upd() {
      var q = normalize(gf.value).trim();
      var n = 0;
      items.forEach(function (it) {
        var ok = !q || normalize(it.textContent).indexOf(q) !== -1;
        it.hidden = !ok;
        if (ok) n++;
      });
      letters.forEach(function (h) {
        var sib = h.nextElementSibling, any = false;
        if (sib) $$(".gl-item", sib).forEach(function (it) { if (!it.hidden) any = true; });
        h.hidden = !any;
        if (sib) sib.hidden = !any;
      });
      count.textContent = n + (n > 1 ? " termes" : " terme");
    }
    gf.addEventListener("input", upd);
    upd();
    if (location.hash) {
      var t = document.getElementById(location.hash.slice(1));
      if (t) setTimeout(function () { t.scrollIntoView(); }, 60);
    }
  }

  /* --- quiz ------------------------------------------------------------ */
  var qStart = $("#q-start");
  if (qStart) {
    var pool = [], run = [], at = 0, good = 0;
    var elQ = $("#quiz"), elR = $("#quiz-result"), elS = $("#quiz-setup");

    fetch(BASE + "assets/js/quiz.json").then(function (r) { return r.json(); })
      .then(function (d) { pool = d; })
      .catch(function () { qStart.disabled = true; qStart.textContent = "Quiz indisponible"; });

    function shuffle(a) {
      a = a.slice();
      for (var i = a.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var t = a[i]; a[i] = a[j]; a[j] = t;
      }
      return a;
    }

    qStart.addEventListener("click", function () {
      var th = $("#q-theme").value;
      var n = parseInt($("#q-count").value, 10);
      var set = pool.filter(function (q) { return !th || q.th === th; });
      run = shuffle(set);
      if (n > 0) run = run.slice(0, n);
      if (!run.length) return;
      at = 0; good = 0;
      elS.hidden = true; elR.hidden = true; elQ.hidden = false;
      render();
    });

    function render() {
      var q = run[at];
      var opts = q.o.map(function (o, i) {
        return '<button class="q-opt" data-i="' + i + '">' + o + "</button>";
      }).join("");
      elQ.innerHTML =
        '<div class="q-card"><p class="q-prog"><span>Question ' + (at + 1) + " / " + run.length +
        '</span><span>' + q.th + '</span></p>' +
        '<p class="q-txt">' + q.q + "</p>" +
        '<div class="q-opts">' + opts + "</div><div id=\"q-after\"></div></div>";
      $$(".q-opt", elQ).forEach(function (b) {
        b.addEventListener("click", function () { answer(parseInt(b.getAttribute("data-i"), 10)); });
      });
      elQ.scrollIntoView({ block: "nearest" });
    }

    function answer(i) {
      var q = run[at];
      $$(".q-opt", elQ).forEach(function (b, k) {
        b.disabled = true;
        if (k === q.a) b.classList.add("good");
        else if (k === i) b.classList.add("bad");
      });
      if (i === q.a) good++;
      var link = q.c ? ' <a href="' + BASE + "chapitres/" + q.c + '.html">Lire le chapitre</a>' : "";
      $("#q-after").innerHTML =
        '<div class="q-exp"><p>' + q.e + "</p>" + link + "</div>" +
        '<button class="btn q-next" id="q-next">' +
        (at + 1 < run.length ? "Question suivante" : "Voir le résultat") + "</button>";
      $("#q-next").addEventListener("click", function () {
        at++;
        if (at < run.length) render(); else finish();
      });
      $("#q-next").focus();
    }

    function finish() {
      elQ.hidden = true; elR.hidden = false;
      var pct = Math.round((good / run.length) * 100);
      var msg = pct >= 85 ? "Excellent — vous maîtrisez la matière."
        : pct >= 65 ? "Bon niveau. Quelques zones à revoir."
        : pct >= 40 ? "Les bases sont là, la précision manque encore."
        : "Reprenez les chapitres tranquillement : ça viendra.";
      elR.innerHTML = '<p class="qr-score">' + good + " / " + run.length + "</p>" +
        '<div class="qr-bar"><span style="width:' + pct + '%"></span></div>' +
        "<p>" + msg + '</p><button class="btn ghost" id="q-again">Recommencer</button>';
      $("#q-again").addEventListener("click", function () {
        elR.hidden = true; elS.hidden = false;
        elS.scrollIntoView({ block: "nearest" });
      });
      elR.scrollIntoView({ block: "nearest" });
    }
  }

  /* --- outil « quelle juridiction ? » ---------------------------------- */
  var tool = $("#tool-juri");
  if (tool) {
    var TREE = {
      start: {
        q: "De quoi s'agit-il ?",
        o: [["Un litige entre personnes (argent, bail, famille, travail…)", "civil"],
            ["Une infraction : quelqu'un est poursuivi", "penal"],
            ["Un acte d'une administration que je conteste", "admin"]]
      },
      civil: {
        q: "Quel est l'objet du litige ?",
        o: [["Un bail, un voisinage, une petite somme (≤ 5 000 €)", "r_paix"],
            ["Divorce, filiation, pension alimentaire, autorité parentale", "r_famille"],
            ["Contrat de travail, licenciement, chômage, pension", "r_travail"],
            ["Un différend entre entreprises", "r_entreprise"],
            ["Autre litige civil de plus de 5 000 €", "r_civil"]]
      },
      penal: {
        q: "Quelle est la nature des faits ?",
        o: [["Circulation routière (n'importe quelle gravité)", "r_police"],
            ["Infraction la moins grave, hors roulage", "r_police"],
            ["Vol, coups, fraude — gravité moyenne", "r_correctionnel"],
            ["Faits les plus graves (assassinat…), délit politique ou de presse", "r_assises"],
            ["L'auteur avait moins de 18 ans", "r_jeunesse"]]
      },
      admin: {
        q: "Quel type d'acte ?",
        o: [["Un permis, une sanction, une nomination, un règlement communal", "r_ce"],
            ["Une loi, un décret ou une ordonnance", "r_cc"]]
      },
      r_paix: { r: "Justice de paix", d: "Le juge de proximité : litiges civils jusqu'à 5 000 €, plus les baux, le voisinage et les mesures de protection des personnes, quel que soit le montant. Il y en a un par canton judiciaire." },
      r_famille: { r: "Tribunal de la famille et de la jeunesse", d: "Il concentre tout le contentieux familial. Une même famille garde en principe le même dossier et le même juge." },
      r_travail: { r: "Tribunal du travail", d: "Un magistrat professionnel y siège avec deux juges non professionnels, l'un côté travailleurs, l'autre côté employeurs. La procédure y est gratuite pour l'assuré social dans la plupart des litiges de sécurité sociale." },
      r_entreprise: { r: "Tribunal de l'entreprise", d: "Compétent pour les litiges entre entreprises. Un particulier qui attaque une entreprise peut choisir cette voie, mais n'y est jamais contraint." },
      r_civil: { r: "Tribunal de première instance — section civile", d: "Le juge de droit commun : il connaît de tout ce qui n'est pas expressément attribué à une autre juridiction." },
      r_police: { r: "Tribunal de police", d: "Toutes les affaires de roulage y passent, du stationnement à l'accident mortel, ainsi que les infractions les moins graves." },
      r_correctionnel: { r: "Tribunal correctionnel", d: "Section pénale du tribunal de première instance. C'est là que se juge l'essentiel de la délinquance." },
      r_assises: { r: "Cour d'assises", d: "Juridiction non permanente, avec un jury de douze citoyens tirés au sort. Ses arrêts ne sont pas susceptibles d'appel : seul un pourvoi en cassation est possible." },
      r_jeunesse: { r: "Tribunal de la jeunesse", d: "On ne parle pas d'infraction mais de « fait qualifié infraction », et pas de peine mais de mesure. Entre 16 et 18 ans, le juge peut exceptionnellement se dessaisir au profit d'une juridiction pénale." },
      r_ce: { r: "Conseil d'État — section du contentieux administratif", d: "Recours en annulation dans les 60 jours de la publication ou de la notification, avec possibilité de demander la suspension en urgence." },
      r_cc: { r: "Cour constitutionnelle", d: "Recours en annulation dans les six mois de la publication, ou question préjudicielle posée par un juge en cours de procès." }
    };
    var stateKey = "start";
    function drawTool() {
      var n = TREE[stateKey];
      if (n.r) {
        tool.innerHTML = '<h4>Quelle juridiction ?</h4><div class="tool-res"><b>' + n.r + "</b><p>" + n.d +
          '</p></div><button class="tool-restart">Recommencer</button>';
      } else {
        tool.innerHTML = '<h4>Quelle juridiction ?</h4><p class="tool-q">' + n.q + '</p><div class="tool-opts">' +
          n.o.map(function (o, i) { return '<button class="tool-opt" data-k="' + o[1] + '">' + o[0] + "</button>"; }).join("") +
          "</div>" + (stateKey !== "start" ? '<button class="tool-restart">Recommencer</button>' : "");
      }
      $$(".tool-opt", tool).forEach(function (b) {
        b.addEventListener("click", function () { stateKey = b.getAttribute("data-k"); drawTool(); });
      });
      var rs = $(".tool-restart", tool);
      if (rs) rs.addEventListener("click", function () { stateKey = "start"; drawTool(); });
    }
    drawTool();
  }
})();
