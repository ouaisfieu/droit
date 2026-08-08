# Droit belge, expliqué

Une introduction complète au droit belge, en accès libre, écrite pour le grand public.
22 chapitres, un glossaire de 273 termes, 124 questions de quiz, un outil interactif
pour identifier la juridiction compétente.

Site statique : HTML, CSS et JavaScript, sans framework, sans dépendance externe,
sans base de données, sans script de suivi.

---

## Mise en ligne sur GitHub Pages

Le site généré se trouve **à la racine du dépôt**. Aucune configuration n'est nécessaire.

1. Poussez le contenu de ce dossier sur `https://github.com/ouaisfieu/droit`

   ```bash
   cd droit
   git init
   git add -A
   git commit -m "Site d'introduction au droit belge"
   git branch -M main
   git remote add origin git@github.com:ouaisfieu/droit.git
   git push -u origin main
   ```

2. Dans le dépôt, allez dans **Settings → Pages**
3. Sous *Build and deployment*, choisissez **Deploy from a branch**
4. Branche `main`, dossier `/ (root)`, puis **Save**

Le site sera disponible sous une minute à l'adresse
**https://ouaisfieu.github.io/droit/**

Le fichier `.nojekyll` à la racine est indispensable : il empêche GitHub de faire
passer les fichiers par Jekyll, qui ignorerait certains répertoires.

### Nom de domaine personnalisé

Ajoutez un fichier `CNAME` à la racine contenant votre domaine, puis configurez
l'enregistrement DNS. Pensez à modifier `SITE_URL` dans `src/build.py` pour que le
`sitemap.xml` pointe vers la bonne adresse.

---

## Modifier le contenu

Tout le texte se trouve dans `src/content/`, un fichier HTML par chapitre.
Ces fichiers ne contiennent **que le corps du chapitre** — pas de `<html>`, pas de
`<head>`, pas de navigation. Le générateur ajoute l'ossature, la numérotation des
sections, le sommaire latéral, l'index de recherche et les métadonnées.

```
src/
├── build.py                  générateur (Python 3, bibliothèque standard uniquement)
├── content/
│   ├── _home.html            page d'accueil
│   ├── _ressources.html      page Ressources
│   ├── _a-propos.html        page À propos
│   └── <slug>.html           les 22 chapitres
├── data/
│   ├── glossaire.json        273 termes
│   └── quiz.json             124 questions
└── assets/
    ├── css/style.css
    ├── js/app.js
    └── img/favicon.svg
```

### Régénérer le site

```bash
cd src
python3 build.py
cp -r out/. ..
```

Aucune dépendance à installer. Python 3.8 ou plus récent suffit.

Pour construire ailleurs qu'en `src/out` :

```bash
OUT=/chemin/de/sortie python3 build.py
```

### Ajouter un chapitre

1. Créez `src/content/mon-chapitre.html`
2. Ajoutez une entrée dans la liste `CHAPTERS` de `build.py` :
   `(23, "mon-chapitre", "Titre du chapitre", "V", "Phrase d'accroche.")`
3. Relancez le build

La numérotation des sections (`§ 23.1`, `§ 23.2`…), les ancres, le sommaire, la
recherche et le `sitemap.xml` sont mis à jour automatiquement.

### Conventions de rédaction

| Élément | Balisage |
|---|---|
| Encadré neutre | `<div class="box"><p class="box-t">Titre</p>…</div>` |
| Points clés (fin de chapitre) | `<div class="box key">` |
| Cas pratique | `<div class="box case">` |
| Avertissement, piège | `<div class="box warn">` |
| Tableau | l'envelopper dans `<div class="tbl-wrap">` |
| Terme du glossaire | `<dfn>terme</dfn>` ou `<dfn data-t="Terme canonique">forme fléchie</dfn>` |
| Schéma | `<figure><div class="fig-frame"><svg …></svg></div><figcaption>…</figcaption></figure>` |

Les `<dfn>` déclenchent une infobulle alimentée par `glossaire.json`. Le texte de la
balise doit correspondre exactement à un terme du glossaire, sinon utilisez `data-t`.

### Format des données

`glossaire.json` — un objet par terme :

```json
{"t": "Terme", "d": "Définition, HTML autorisé.", "c": "slug-du-chapitre", "v": ["Renvoi"]}
```

`quiz.json` — un objet par question, `a` étant l'index de la bonne réponse :

```json
{"th": "Thème", "q": "Question ?", "o": ["A","B","C","D"], "a": 2,
 "e": "Explication.", "c": "slug-du-chapitre"}
```

---

## Fonctionnalités

- **Recherche plein texte** dans les 22 chapitres — touche `/` ou `Ctrl/Cmd + K`,
  normalisation des accents, surlignage des résultats, navigation au clavier
- **Numérotation marginale** `§ n.m` sur chaque section, cliquable pour copier un lien profond
- **Glossaire** de 273 termes, filtrable, avec renvois croisés et infobulles dans les chapitres
- **Quiz** de 124 questions, filtrables par thème, avec explication et lien vers le chapitre
- **Outil « Quelle juridiction ? »** — arbre de décision civil, pénal et administratif
- **Schémas SVG** : hiérarchie des normes, parcours d'une loi, pyramide judiciaire
- Sommaire latéral actif au défilement, barre de progression de lecture
- Thème clair et sombre, respect de `prefers-color-scheme`
- Responsive, styles d'impression, accessible au clavier et aux lecteurs d'écran
- Dégradation gracieuse : les pages restent lisibles sans JavaScript

---

## Sources et méthode

Le plan suit la progression classique d'un cours universitaire d'introduction au droit
belge. Les règles, chiffres, seuils, délais et procédures proviennent des textes
normatifs et des sources officielles listées sur la page *Ressources*.

**L'intégralité du texte a été rédigée pour ce site.** Aucun passage n'est repris d'un
manuel, d'un syllabus ou d'un article. Les documents de référence ont servi à la
vérification, jamais de matière première rédactionnelle.

Les textes normatifs cités — Constitution, lois, arrêtés, décisions de justice —
sont des documents officiels relevant du domaine public.

## Avertissement

Ce site fournit une **information générale**. Il ne constitue pas un conseil juridique
et ne tient pas compte d'une situation particulière. Pour une décision qui vous
concerne, consultez un avocat, un notaire, un service de médiation ou une permanence
d'aide juridique — l'aide juridique de première ligne est gratuite et sans condition
de revenus.

Le droit change. Vérifiez toujours la version consolidée d'un texte sur
[Justel](https://www.ejustice.just.fgov.be/) avant de vous y fier.

## Contribuer

Les corrections sont bienvenues, en particulier sur les chiffres, les seuils, les
délais et les intitulés de juridictions, qui évoluent. Ouvrez une *issue* ou une
*pull request*.

Si vous modifiez `src/content/` ou `src/data/`, régénérez le site avant de committer,
ou laissez le workflow GitHub Actions le faire (voir `.github/workflows/build.yml`).

## Licence

Le texte rédigé pour ce site peut être repris, adapté et rediffusé librement, y compris
à des fins pédagogiques, moyennant mention de la source.
