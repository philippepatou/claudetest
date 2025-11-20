# 🚀 Activer GitHub Pages

Ce guide vous explique comment héberger votre site sur GitHub Pages pour le visualiser en ligne.

## 📋 Prérequis

- ✅ Le code est déjà pushé sur la branche `claude/nurse-website-dunkerque-01UVNQdUogpKigjjHFFEvN7g`
- ✅ Vous avez accès au repository GitHub

## 🔧 Étapes d'Activation

### Option 1 : Activer depuis la branche actuelle

1. **Aller sur GitHub**
   - Ouvrez votre navigateur
   - Allez sur : https://github.com/philippepatou/claudetest

2. **Accéder aux Settings**
   - Cliquez sur l'onglet **Settings** (Paramètres)
   - Dans le menu latéral gauche, cliquez sur **Pages**

3. **Configurer la source**
   - Dans la section "Build and deployment"
   - **Source** : Sélectionnez "Deploy from a branch"
   - **Branch** : Sélectionnez `claude/nurse-website-dunkerque-01UVNQdUogpKigjjHFFEvN7g`
   - **Folder** : Sélectionnez `/ (root)`
   - Cliquez sur **Save**

4. **Attendre le déploiement**
   - GitHub va construire le site (1-2 minutes)
   - Une fois prêt, une URL apparaîtra en haut de la page Pages
   - Format : `https://philippepatou.github.io/claudetest/`

### Option 2 : Merger dans main puis activer (recommandé pour production)

1. **Créer une Pull Request**
   - Sur GitHub, allez dans l'onglet **Pull Requests**
   - Cliquez sur **New Pull Request**
   - Base : `main`
   - Compare : `claude/nurse-website-dunkerque-01UVNQdUogpKigjjHFFEvN7g`
   - Cliquez sur **Create Pull Request**
   - Ajoutez un titre et description
   - Cliquez sur **Merge Pull Request**

2. **Activer GitHub Pages sur main**
   - Settings > Pages
   - Source : Deploy from a branch
   - Branch : `main`
   - Folder : `/ (root)`
   - Save

3. **Accéder au site**
   - URL : `https://philippepatou.github.io/claudetest/`

## 🌐 URL de Votre Site

Une fois activé, votre site sera accessible à :

```
https://philippepatou.github.io/claudetest/
```

**Note :** Si vous avez un domaine personnalisé, vous pouvez le configurer dans Settings > Pages > Custom domain

## 🔍 Vérification du Déploiement

1. **Vérifier l'état**
   - Allez dans l'onglet **Actions** sur GitHub
   - Vous verrez un workflow "pages build and deployment"
   - ✅ Coche verte = déploiement réussi
   - ❌ Croix rouge = erreur (cliquez pour voir les logs)

2. **Tester le site**
   - Ouvrez l'URL dans votre navigateur
   - Testez la navigation entre les pages
   - Vérifiez le responsive (mobile/tablette/desktop)
   - Testez le menu hamburger sur mobile

## ⚠️ Points Importants

### Chemins relatifs

Les fichiers utilisent des chemins relatifs, ce qui fonctionne sur GitHub Pages :
- ✅ `css/styles.css` → OK
- ✅ `js/main.js` → OK
- ✅ `blog/article.html` → OK
- ✅ `/` redirige vers index.html → OK

### Images manquantes

Actuellement, les dossiers `images/`, `images/blog/` et `images/icons/` sont vides.

**Pour ajouter des images :**

1. Créez des images (ou utilisez des placeholders)
2. Ajoutez-les dans les dossiers appropriés
3. Commitez et pushez :
   ```bash
   git add images/
   git commit -m "Add images"
   git push
   ```
4. GitHub Pages se mettra à jour automatiquement

### Délai de mise à jour

- Premier déploiement : 1-5 minutes
- Mises à jour ultérieures : 30 secondes - 2 minutes
- Si vous ne voyez pas les changements, videz le cache (Ctrl+Shift+R)

## 🎨 Personnalisation Avant Production

Avant de partager le lien publiquement, pensez à :

1. **Remplacer les données placeholder**
   - [ ] Nom et prénom
   - [ ] Numéro de téléphone
   - [ ] Email
   - [ ] Adresse
   - [ ] N° RPPS

2. **Ajouter de vraies images**
   - [ ] Portrait professionnel
   - [ ] Photos du cabinet
   - [ ] Images des articles blog

3. **Adapter le contenu**
   - [ ] Parcours professionnel
   - [ ] Soins proposés (selon compétences)
   - [ ] Zone d'intervention

## 🔒 Visibilité du Site

### Par défaut (repository public)
- ✅ Le site est accessible à tous via l'URL GitHub Pages
- ✅ Le code source est visible sur GitHub

### Repository privé
- Si le repository est privé, vous devrez avoir GitHub Pro/Team/Enterprise pour GitHub Pages
- Ou rendre le repository public

## 📱 Tester sur Mobile

Pour tester le site sur votre téléphone :

1. Ouvrez l'URL GitHub Pages sur votre mobile
2. Testez le menu hamburger
3. Vérifiez que tout est lisible
4. Testez le formulaire de contact
5. Vérifiez les liens

## 🐛 Résolution de Problèmes

### Le site n'apparaît pas
- Attendez 2-3 minutes après activation
- Vérifiez que la branche et le dossier sont corrects
- Allez dans Actions pour voir si le déploiement a réussi

### Erreur 404 sur les pages
- Vérifiez que tous les fichiers .html sont bien présents
- Vérifiez les liens dans le code (case-sensitive)

### Les styles ne s'appliquent pas
- Videz le cache du navigateur (Ctrl+Shift+R)
- Vérifiez que `css/styles.css` existe
- Regardez la console du navigateur (F12) pour les erreurs

### Les images ne s'affichent pas
- Normal, les dossiers images sont vides
- Ajoutez des images ou utilisez des placeholders
- URLs d'images placeholder gratuits :
  - https://via.placeholder.com/800x600
  - https://picsum.photos/800/600

## 📊 Monitoring et Analytics

Une fois le site en ligne, vous pouvez :

1. **Google Search Console**
   - Ajouter la propriété avec l'URL GitHub Pages
   - Soumettre le sitemap

2. **Google Analytics**
   - Créer une propriété GA4
   - Ajouter le code de suivi dans toutes les pages

3. **Statistiques GitHub**
   - Dans Insights > Traffic
   - Voir le nombre de visiteurs

## 🚀 Prochaines Étapes

Une fois satisfait du rendu sur GitHub Pages :

1. **Acheter un nom de domaine**
   - Ex: infirmiere-dunkerque.fr
   - Chez OVH, Gandi, etc.

2. **Configurer le domaine personnalisé**
   - Settings > Pages > Custom domain
   - Ajouter votre domaine
   - Configurer les DNS

3. **Ou migrer vers un hébergement classique**
   - OVH, O2Switch, etc.
   - Transférer tous les fichiers via FTP

## 📞 Support

Pour toute question sur GitHub Pages :
- Documentation : https://docs.github.com/en/pages
- GitHub Community : https://github.community/

---

**Bon test ! 🎉**
