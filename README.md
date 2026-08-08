# Droit belge, expliqué

Introduction complète au droit belge, en accès libre, écrite pour le grand public.

**HTML, CSS et JavaScript purs. Aucun build, aucune dépendance, aucun framework.**
Vous poussez les fichiers tels quels, GitHub Pages les sert tels quels.

- 22 chapitres, ~32 600 mots
- Glossaire de 273 termes avec renvois croisés et infobulles
- 124 questions de quiz
- Recherche plein texte, schémas SVG, thème clair/sombre

---

## Mise en ligne

```bash
cd droit
git init
git add -A
git commit -m "Site d'introduction au droit belge"
git branch -M main
git remote add origin git@github.com:ouaisfieu/droit.git
git push -u origin main
```

Puis dans le dépôt : **Settings → Pages → Deploy from a branch**,
branche `main`, dossier `/ (root)`, **Save**.

Le site est en ligne sous une minute : **https://ouaisfieu.github.io/droit/**

### Si la page reste blanche ou sans style, vérifiez ces trois points

1. **Les 38 fichiers sont-ils tous poussés ?** Le cas le plus fréquent : `assets/`
   manquant, ce qui donne une page sans aucun style.
   ```bash
   git ls-files | wc -l    # doit afficher 38
   ```

2. **`.nojekyll` est-il présent à la racine ?** C'est un fichier caché, facile à
   oublier. Sans lui, GitHub fait passer le site par Jekyll, qui ignore certains
   dossiers.
   ```bash
   git ls-files | grep nojekyll
   ```

3. **La source Pages est-elle bien « Deploy from a branch » ?**
   Si elle est réglée sur « GitHub Actions », rien ne sera publié.

---

## Aperçu en local

Ne double-cliquez pas `index.html`. En `file://`, les navigateurs bloquent le
chargement des fichiers JSON : la recherche, le glossaire et le quiz resteront vides.
Ce n'est pas un défaut du site, c'est une sécurité du navigateur.

Lancez plutôt un serveur local, depuis le dossier du site :

```bash
python3 -m http.server 8000
```

Puis ouvrez `http://localhost:8000`. Tout fonctionne alors comme en ligne.

---

## Structure

```
.
├── .nojekyll              indispensable pour GitHub Pages
├── index.html             accueil
├── glossaire.html         273 termes
├── quiz.html              124 questions
├── ressources.html        où trouver textes officiels et aide juridique
├── a-propos.html          méthode, limites, avertissement
├── 404.html
├── robots.txt
├── sitemap.xml
├── chapitres/             22 fichiers, un par chapitre
└── assets/
    ├── css/style.css
    ├── img/favicon.svg
    └── js/
        ├── app.js             recherche, glossaire, quiz, thème, outils
        ├── glossaire.json     273 termes
        ├── quiz.json          124 questions
        └── search-index.json  index de recherche
```

Chaque fichier HTML est **autonome et complet** : en-tête, navigation, contenu, pied
de page. Vous pouvez en ouvrir un dans n'importe quel éditeur et modifier le texte
directement.

---

## Modifier le site

### Corriger ou enrichir un chapitre

Ouvrez le fichier concerné dans `chapitres/` et modifiez le HTML. Les conventions
de balisage utilisées :

| Élément | Balisage |
|---|---|
| Encadré neutre | `<div class="box"><p class="box-t">Titre</p>…</div>` |
| Points clés | `<div class="box key">` |
| Cas pratique | `<div class="box case">` |
| Avertissement | `<div class="box warn">` |
| Tableau | l'envelopper dans `<div class="tbl-wrap">` |
| Terme du glossaire | `<dfn>terme</dfn>` ou `<dfn data-t="Terme canonique">forme fléchie</dfn>` |

Si vous ajoutez une section `<h2>`, reprenez le modèle des sections voisines : ancre
`id`, lien `§ n.m`, et entrée correspondante dans le sommaire latéral du même fichier.

### Ajouter un terme au glossaire

Dans `assets/js/glossaire.json` — la liste est triée alphabétiquement :

```json
{"t": "Terme", "d": "Définition, HTML autorisé.", "c": "slug-du-chapitre", "v": ["Renvoi"]}
```

Ajoutez aussi l'entrée dans `glossaire.html` pour qu'elle apparaisse sur la page : le
JSON alimente les infobulles des chapitres, le HTML alimente la page du glossaire.

### Ajouter une question de quiz

Dans `assets/js/quiz.json`, `a` étant l'index de la bonne réponse (0 = première) :

```json
{"th": "Thème", "q": "Question ?", "o": ["A","B","C","D"], "a": 2,
 "e": "Explication.", "c": "slug-du-chapitre"}
```

### Ajouter un chapitre

Dupliquez un fichier existant de `chapitres/`, remplacez le contenu, puis ajoutez le
lien dans la barre latérale de **chaque** page et dans `sitemap.xml`. C'est la
contrepartie de l'absence de build : un ajout de chapitre se répercute à la main.

### Nom de domaine personnalisé

Créez un fichier `CNAME` à la racine contenant votre domaine, configurez le DNS,
et remplacez l'adresse dans `sitemap.xml`.

---

## Sources et méthode

Le plan suit la progression classique d'un cours d'introduction au droit belge. Les
règles, chiffres, seuils, délais et procédures proviennent des textes normatifs et des
sources officielles listées sur la page *Ressources*.

**L'intégralité du texte a été rédigée pour ce site.** Aucun passage n'est repris d'un
manuel, d'un syllabus ou d'un article. Les documents de référence ont servi à la
vérification, jamais de matière première rédactionnelle. Les textes normatifs cités —
Constitution, lois, arrêtés, décisions de justice — relèvent du domaine public.

## Avertissement

Ce site fournit une **information générale**. Il ne constitue pas un conseil juridique
et ne tient pas compte d'une situation particulière. Pour une décision qui vous
concerne, consultez un avocat, un notaire, un service de médiation ou une permanence
d'aide juridique — l'aide juridique de première ligne est gratuite et sans condition
de revenus.

Le droit change. Vérifiez la version consolidée d'un texte sur
[Justel](https://www.ejustice.just.fgov.be/) avant de vous y fier. Les seuils chiffrés
(5 000 €, 2 000 €, 2 500 €, délais de recours) sont ceux qui évoluent le plus souvent.

## Licence

Le texte peut être repris, adapté et rediffusé librement, y compris à des fins
pédagogiques, moyennant mention de la source.
