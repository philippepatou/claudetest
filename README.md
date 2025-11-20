# Site Web Infirmière Libérale - Dunkerque

Site web professionnel pour infirmière libérale basée à Dunkerque (59140).

**Caractéristiques principales :**
- ✅ Conforme à la déontologie des infirmiers (pas de publicité)
- ✅ Optimisé SEO local pour "infirmière Dunkerque"
- ✅ Mobile-first et responsive
- ✅ Performant (< 3s chargement)
- ✅ Accessible (WCAG 2.1 AA)
- ✅ Conforme RGPD

---

## 📁 Structure du Projet

```
/
├── index.html                      # Page d'accueil
├── qui-suis-je.html               # Parcours professionnel
├── soins-proposes.html            # Liste des actes infirmiers
├── infos-pratiques.html           # Contact, horaires, formulaire
├── blog.html                      # Liste des articles
├── mentions-legales.html          # Mentions légales
├── confidentialite.html           # Politique RGPD
├── liens-utiles.html              # Liens organismes santé
├── css/
│   └── styles.css                 # Styles principaux
├── js/
│   └── main.js                    # JavaScript
├── images/                        # Images du site
│   ├── blog/                      # Images des articles
│   └── icons/                     # Icônes
└── blog/                          # Articles de blog
    ├── prevenir-infections-urinaires.html
    ├── vivre-avec-diabete.html
    └── maintien-domicile-personnes-agees.html
```

---

## 🚀 Installation et Déploiement

### 1. Téléchargement

Téléchargez ou clonez ce projet sur votre ordinateur.

### 2. Personnalisation (OBLIGATOIRE)

Avant de mettre en ligne, vous **DEVEZ** remplacer toutes les informations de placeholder par vos vraies données.

#### ✏️ Informations à personnaliser :

Recherchez et remplacez dans **TOUS les fichiers HTML** :

| Placeholder | À remplacer par |
|-------------|----------------|
| `Sophie Martin` | Votre prénom et nom |
| `03 28 59 12 34` | Votre numéro de téléphone |
| `+33328591234` | Votre numéro (format international) |
| `contact@infirmiere-dunkerque.fr` | Votre adresse email |
| `15 Rue Jean Jaurès` | Votre adresse de cabinet |
| `10003123456` | Votre numéro RPPS |
| `[à compléter]` | Vos informations (ADELI, SIRET, etc.) |

**Astuce :** Utilisez la fonction "Rechercher et remplacer" de votre éditeur de code (Ctrl+H ou Cmd+H).

#### 📝 Contenu à adapter :

1. **qui-suis-je.html** :
   - Modifier le parcours professionnel
   - Adapter les formations et diplômes
   - Personnaliser les expériences

2. **soins-proposes.html** :
   - Ajouter/retirer des soins selon vos compétences
   - Adapter les descriptions

3. **blog/** :
   - Modifier ou supprimer les articles
   - En créer de nouveaux si souhaité

4. **index.html** :
   - Modifier le texte de présentation
   - Adapter la zone d'intervention

### 3. Images

Remplacez les placeholders d'images par vos propres photos :

#### Images recommandées :

| Emplacement | Type | Dimensions | Poids max |
|-------------|------|------------|-----------|
| Portrait professionnel | Photo de vous en tenue professionnelle | 800x800px | 150 Ko |
| Cabinet extérieur | Photo de votre cabinet | 1200x800px | 150 Ko |
| Cabinet intérieur | Photo de la salle de soins | 1200x800px | 150 Ko |
| Articles blog | Images libres de droits | 800x600px | 100 Ko |

**Format recommandé :** WebP (avec fallback JPG)

**Outils de compression :**
- [TinyPNG](https://tinypng.com/)
- [Squoosh](https://squoosh.app/)

**Sources d'images gratuites :**
- [Unsplash](https://unsplash.com/)
- [Pexels](https://www.pexels.com/)
- [Pixabay](https://pixabay.com/)

### 4. Hébergement

#### Options d'hébergement recommandées :

**Option 1 : OVH (recommandé pour débutants)**
- Offre "Perso" à partir de 2,99€/mois
- Nom de domaine inclus la 1ère année
- Certificat SSL gratuit
- [https://www.ovhcloud.com/fr/web-hosting/](https://www.ovhcloud.com/fr/web-hosting/)

**Option 2 : O2Switch**
- Offre unique à 6€/mois HT
- Trafic et stockage illimités
- [https://www.o2switch.fr/](https://www.o2switch.fr/)

**Option 3 : Netlify (gratuit pour sites statiques)**
- Gratuit pour sites statiques
- Déploiement automatique depuis Git
- Certificat SSL automatique
- [https://www.netlify.com/](https://www.netlify.com/)

#### Étapes de mise en ligne (OVH) :

1. **Acheter un hébergement** avec nom de domaine
2. **Accéder à votre espace client** OVH
3. **FTP** : Récupérer les identifiants FTP
4. **Uploader les fichiers** via FileZilla ou autre client FTP
5. **Vérifier** que le site est accessible

---

## 🔍 Checklist SEO Post-Déploiement

### Google Search Console

1. Créer un compte sur [Google Search Console](https://search.google.com/search-console/)
2. Ajouter votre propriété (site web)
3. Vérifier la propriété
4. Soumettre le sitemap : `https://votresite.fr/sitemap.xml` (à créer)

### Google Business Profile (INDISPENSABLE)

Le référencement local passe principalement par Google Business Profile.

**Étapes :**

1. **Créer votre profil** : [https://www.google.com/intl/fr_fr/business/](https://www.google.com/intl/fr_fr/business/)

2. **Remplir TOUTES les informations** :
   - Nom : "Sophie Martin - Infirmière Libérale"
   - Catégorie : "Infirmière"
   - Adresse complète
   - Téléphone
   - Site web
   - Horaires de permanence téléphonique
   - Description (200-300 mots avec mots-clés)

3. **Ajouter des photos** :
   - Photo de profil (portrait)
   - Photo de couverture (cabinet)
   - 5-10 photos du cabinet et équipements

4. **Vérification de l'adresse** :
   - Google enverra un courrier avec code de validation
   - Entrer le code pour valider

5. **Publier régulièrement** :
   - Actualités
   - Offres
   - Articles du blog

### Google Analytics (Optionnel)

1. Créer un compte [Google Analytics](https://analytics.google.com/)
2. Créer une propriété GA4
3. Récupérer l'ID de mesure (G-XXXXXXXXXX)
4. Ajouter le code de suivi dans `<head>` de toutes les pages :

```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### Créer un Sitemap XML

Créer un fichier `sitemap.xml` à la racine :

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://votresite.fr/</loc>
    <lastmod>2025-11-20</lastmod>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://votresite.fr/qui-suis-je.html</loc>
    <lastmod>2025-11-20</lastmod>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://votresite.fr/soins-proposes.html</loc>
    <lastmod>2025-11-20</lastmod>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://votresite.fr/infos-pratiques.html</loc>
    <lastmod>2025-11-20</lastmod>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://votresite.fr/blog.html</loc>
    <lastmod>2025-11-20</lastmod>
    <priority>0.7</priority>
  </url>
  <!-- Ajouter les autres pages -->
</urlset>
```

---

## 📊 Suivi et Maintenance

### Que surveiller ?

- **Google Search Console** : Erreurs d'indexation, positions moyennes
- **Google Business Profile** : Nombre de vues, clics vers le site
- **Google Analytics** : Visites, pages vues, taux de rebond

### Mises à jour régulières

- **Blog** : Publier 1 article par mois minimum
- **Google Business Profile** : Publier 1-2 actualités par mois
- **Photos** : Ajouter de nouvelles photos tous les 3 mois

---

## 🔧 Support Technique

### Modifier le CSS

Le fichier `css/styles.css` contient toutes les variables CSS au début :

```css
:root {
  --primary: #1e5a8e;        /* Couleur principale */
  --secondary: #4a9d7e;      /* Couleur secondaire */
  /* ... */
}
```

Vous pouvez modifier ces valeurs pour changer les couleurs du site.

### Modifier le JavaScript

Le fichier `js/main.js` est commenté pour faciliter les modifications.

**Fonctionnalités incluses :**
- Menu mobile responsive
- Smooth scroll vers ancres
- Validation formulaire
- Lazy loading images (fallback)
- Header sticky au scroll
- Gestion accessibilité clavier

### Ajouter un Article de Blog

1. **Dupliquer** un article existant dans le dossier `blog/`
2. **Renommer** le fichier (ex: `mon-nouvel-article.html`)
3. **Modifier** le contenu (titre, date, texte)
4. **Ajouter** une vignette dans `blog.html`
5. **Mettre à jour** les balises meta et Schema.org

---

## ⚠️ Conformité Déontologie ONI

### Ce qui est AUTORISÉ :

✅ Informations factuelles (nom, diplômes, coordonnées)
✅ Description compétences et parcours
✅ Contenu éducatif scientifique
✅ Ton professionnel et bienveillant

### Ce qui est INTERDIT :

❌ Publicité, réclame, langage promotionnel
❌ "Meilleure", "excellence", "leader"
❌ Témoignages clients
❌ Logos fantaisistes
❌ Référencement payant Google Ads
❌ Promesses de résultats
❌ Comparaison avec confrères

### En cas de doute :

Consultez le **Code de déontologie des infirmiers** (décret n°2016-1605) :
[https://www.ordre-infirmiers.fr/deontologie](https://www.ordre-infirmiers.fr/deontologie)

---

## 📞 Mentions Obligatoires

Votre site DOIT afficher :

- ✅ Nom et prénom
- ✅ N° RPPS
- ✅ Adresse professionnelle
- ✅ Téléphone
- ✅ Email
- ✅ Mention "Inscrit(e) à l'Ordre des Infirmiers"
- ✅ Lien vers ordre-infirmiers.fr
- ✅ Conventionnement (secteur 1 ou 2)

---

## 🔐 RGPD et Confidentialité

### Obligations RGPD :

- ✅ Politique de confidentialité accessible
- ✅ Mention RGPD sur le formulaire
- ✅ Conservation limitée des données (1 an contacts, 20 ans dossiers soins)
- ✅ Droit d'accès, rectification, suppression
- ✅ Consentement pour cookies non essentiels

### Gestion des Données de Contact :

Les données du formulaire de contact sont actuellement traitées en **frontend uniquement** (pas d'envoi réel).

**Pour activer l'envoi réel**, vous avez 2 options :

**Option 1 : Formspree (simple, gratuit)**
1. Créer un compte sur [https://formspree.io/](https://formspree.io/)
2. Obtenir votre endpoint unique
3. Modifier l'attribut `action` du formulaire :
```html
<form action="https://formspree.io/f/VOTRE_ID" method="POST">
```

**Option 2 : Backend PHP**
Créer un fichier `contact.php` sur votre serveur (non inclus, nécessite compétences PHP).

---

## 📈 Optimisations Avancées (Optionnel)

### Compression GZIP

Ajouter dans `.htaccess` (hébergement Apache) :

```apache
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript
</IfModule>
```

### Cache Navigateur

```apache
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType image/jpg "access plus 1 year"
  ExpiresByType image/jpeg "access plus 1 year"
  ExpiresByType image/png "access plus 1 year"
  ExpiresByType image/webp "access plus 1 year"
  ExpiresByType text/css "access plus 1 month"
  ExpiresByType application/javascript "access plus 1 month"
</IfModule>
```

### Minification CSS/JS

Utiliser des outils en ligne pour minifier :
- CSS : [https://cssminifier.com/](https://cssminifier.com/)
- JS : [https://javascript-minifier.com/](https://javascript-minifier.com/)

---

## 📝 Checklist Finale Avant Mise en Ligne

- [ ] Toutes les informations personnelles sont remplacées
- [ ] Le numéro RPPS est correct
- [ ] L'adresse email fonctionne
- [ ] Le numéro de téléphone est correct
- [ ] Les images sont optimisées (< 150 Ko)
- [ ] Toutes les pages s'affichent correctement
- [ ] Le site est responsive (tester sur mobile)
- [ ] Le formulaire de contact fonctionne
- [ ] Les liens du menu fonctionnent
- [ ] Les liens externes s'ouvrent dans un nouvel onglet
- [ ] La page mentions légales est complétée
- [ ] Le nom de l'hébergeur est ajouté
- [ ] Google Analytics est configuré (si souhaité)
- [ ] Le sitemap.xml est créé et soumis
- [ ] Google Business Profile est créé et vérifié

---

## 🎯 Objectifs SEO

**Mots-clés cibles :**
- infirmière libérale Dunkerque
- soins infirmiers à domicile Dunkerque
- cabinet infirmier Dunkerque
- infirmière à domicile 59140
- prélèvements sanguins Dunkerque
- soins palliatifs à domicile Dunkerque

**Résultats attendus (3-6 mois) :**
- Apparition sur Google Maps (locale)
- Position top 3 sur "infirmière Dunkerque"
- Visibilité sur recherches longue traîne

---

## 📚 Ressources Utiles

- **Ordre National des Infirmiers** : [https://www.ordre-infirmiers.fr/](https://www.ordre-infirmiers.fr/)
- **Code de déontologie** : [https://www.ordre-infirmiers.fr/deontologie](https://www.ordre-infirmiers.fr/deontologie)
- **CNIL (RGPD)** : [https://www.cnil.fr/](https://www.cnil.fr/)
- **Google Business Profile** : [https://www.google.com/intl/fr_fr/business/](https://www.google.com/intl/fr_fr/business/)
- **Google Search Console** : [https://search.google.com/search-console/](https://search.google.com/search-console/)

---

## 📧 Support

Pour toute question technique sur ce site, consultez la documentation en ligne ou contactez un développeur web local.

---

## 📄 Licence

Ce site est fourni tel quel. Vous êtes libre de le modifier selon vos besoins tout en respectant :
- La déontologie de l'Ordre des Infirmiers
- Le RGPD
- Les lois françaises en vigueur

---

**Bonne chance avec votre site web ! 🚀**
