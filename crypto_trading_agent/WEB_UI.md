# 🌐 Interface Web - Guide d'Utilisation

## 🎨 Interface Graphique Moderne

L'agent de trading dispose maintenant d'une **interface web moderne et intuitive** pour contrôler et visualiser les simulations en temps réel !

## 🚀 Démarrage Rapide

### 1. Installation des Dépendances

```bash
pip install flask flask-cors
```

Ou avec le fichier requirements:
```bash
pip install -r requirements.txt
```

### 2. Lancer le Serveur Web

```bash
cd crypto_trading_agent
python web_server.py
```

Le serveur démarre sur **http://localhost:5000**

### 3. Ouvrir l'Interface

Ouvre ton navigateur et va sur :
```
http://localhost:5000
```

## 📊 Fonctionnalités de l'Interface

### ⚙️ Configuration de la Simulation

L'interface permet de configurer tous les paramètres :

**Paramètres de Simulation :**
- Capital Initial (€)
- Nombre d'Itérations
- Date de Début / Fin
- Activer/Désactiver les Signaux Twitter

**Paramètres de Stratégie :**
- Risque par Trade (%)
- Allocation Max par Coin (%)
- Stop Loss (%)
- Take Profit (%)
- Poids Twitter (%)

### 📈 Progression en Temps Réel

Pendant la simulation, tu vois :
- **Barre de progression** animée
- **Itération** et **Jour** en cours
- **Valeur du portefeuille** en temps réel
- **ROI actuel**
- **Logs de simulation** qui défilent

### 🏆 Résultats Détaillés

À la fin, l'interface affiche :
- **ROI Final** (en vert si positif)
- **Valeur Finale** du portefeuille
- **Profit/Perte** en euros
- **Nombre de Trades** effectués
- **Win Rate** (taux de réussite)
- **Score Global** sur 100

### 📊 Historique des Itérations

Section dédiée montrant :
- **Statistiques globales** (ROI moyen, meilleur, pire)
- **Tableau complet** de toutes les itérations
- **Tri automatique** par date (plus récent en haut)
- **Codes couleur** pour le ROI (vert/rouge)

## 🎮 Utilisation

### Lancer une Simulation

1. **Configure les paramètres** dans les deux sections
2. **Clique sur "🚀 Démarrer la Simulation"**
3. **Observe la progression** en temps réel
4. **Consulte les résultats** une fois terminé

### Arrêter une Simulation

Clique sur **"⏹️ Arrêter"** à tout moment pour interrompre.

### Effacer l'Historique

Clique sur **"🗑️ Effacer l'Historique"** pour repartir de zéro.

## 🖥️ Capture d'Écran Textuelle

```
┌────────────────────────────────────────────┐
│  🤖 Agent de Trading Crypto                │
│  Interface de Contrôle et de Visualisation │
└────────────────────────────────────────────┘

┌─ ⚙️ Configuration ──────────────────────────┐
│                                              │
│  Simulation        │  Stratégie             │
│  ├─ Capital: 1000€ │  ├─ Risque: 15%        │
│  ├─ Itérations: 3  │  ├─ Alloc: 25%         │
│  ├─ Date: 24/12-24 │  ├─ Stop: 10%          │
│  └─ Twitter: ✓     │  └─ Profit: 20%        │
│                                              │
│  [🚀 Démarrer]  [⏹️ Arrêter]  [🗑️ Effacer]  │
└──────────────────────────────────────────────┘

┌─ 📊 Progression ────────────────────────────┐
│  Itération 2 / 3 - Jour 245 / 366           │
│  ████████████░░░░░░░░ 67%                   │
│                                              │
│  Itération │ Jour   │ Valeur │ ROI          │
│  2 / 3     │245/366 │1342.50€│ +34.25%      │
│                                              │
│  📝 Logs:                                    │
│  ▸ Starting iteration 2/3                    │
│  ▸ Day 245: BUY BTC (Twitter signal)         │
│  ▸ Portfolio value: 1342.50€                 │
└──────────────────────────────────────────────┘

┌─ 🏆 Résultats ──────────────────────────────┐
│  ROI: +42.5%  │  Win Rate: 65%               │
│  Valeur: 1425€│  Trades: 127                 │
│  P/L: +425€   │  Score: 85/100               │
└──────────────────────────────────────────────┘

┌─ 📈 Historique ─────────────────────────────┐
│  Total: 5  │  Moy: +38%  │  Best: +48%      │
│                                              │
│  # │ Date       │ ROI      │ Score │ Win %   │
│  5 │ 05/01 14:32│ +42.5%   │ 85/100│ 65%     │
│  4 │ 05/01 14:20│ +38.2%   │ 78/100│ 58%     │
│  3 │ 05/01 14:05│ +35.7%   │ 74/100│ 52%     │
└──────────────────────────────────────────────┘
```

## 🎨 Design Moderne

L'interface utilise :
- **Thème sombre** élégant (bleu foncé)
- **Animations fluides** sur les cartes et boutons
- **Gradients colorés** pour les boutons et le header
- **Typographie Inter** moderne et lisible
- **Design responsive** (fonctionne sur mobile)
- **Codes couleur** intuitifs (vert = profit, rouge = perte)

## 🔧 Architecture Technique

### Backend (Flask)
- **Routes API REST** pour contrôler la simulation
- **Threading** pour exécution asynchrone
- **Stockage JSON** des résultats
- **CORS** activé pour développement

### Frontend
- **HTML5** moderne et sémantique
- **CSS3** avec variables et animations
- **JavaScript vanilla** (pas de framework)
- **Polling** pour mise à jour temps réel

## 📡 API Endpoints

```
GET  /                      - Page principale
GET  /api/config            - Configuration actuelle
GET  /api/history           - Historique des itérations
GET  /api/simulation/status - État de la simulation
POST /api/simulation/start  - Démarrer une simulation
POST /api/simulation/stop   - Arrêter la simulation
POST /api/history/clear     - Effacer l'historique
```

## 🐛 Dépannage

### Le serveur ne démarre pas
```bash
# Vérifier que Flask est installé
pip install flask flask-cors

# Vérifier que le port 5000 est libre
# Sur Windows
netstat -ano | findstr :5000

# Sur Linux/Mac
lsof -i :5000
```

### L'interface ne se charge pas
- Vérifie que le serveur est bien lancé
- Va sur http://localhost:5000 (pas 127.0.0.1)
- Ouvre la console du navigateur (F12) pour voir les erreurs

### La simulation ne démarre pas
- Vérifie que tous les modules Python sont installés
- Regarde les logs dans le terminal du serveur
- Efface l'historique si corrompu

## 🚀 Prochaines Améliorations

Fonctionnalités prévues :
- 📊 **Graphiques interactifs** (Chart.js)
- 📥 **Export des résultats** (PDF, CSV)
- 🔔 **Notifications** de fin de simulation
- 📱 **Version mobile** optimisée
- 🎯 **Comparaison d'itérations**
- 🔐 **Authentification** (optionnelle)

## 💡 Conseils d'Utilisation

1. **Commence avec 1 itération** pour tester
2. **Active les signaux Twitter** pour de meilleures performances
3. **Ajuste les paramètres** en fonction des résultats
4. **Lance plusieurs itérations** pour voir l'apprentissage
5. **Surveille le Win Rate** et le Score global

## 🎓 Exemple de Session

```bash
# Terminal 1: Lancer le serveur
cd crypto_trading_agent
python web_server.py

# Navigateur: http://localhost:5000
# 1. Configure: 1000€, 3 itérations, Twitter activé
# 2. Clique "Démarrer"
# 3. Observe la progression
# 4. Consulte les résultats
# 5. Lance 3 itérations supplémentaires
# 6. Compare les performances dans l'historique
```

## 📞 Support

En cas de problème :
1. Vérifie les logs du serveur (terminal)
2. Ouvre la console du navigateur (F12)
3. Consulte `iteration_history.json` pour l'historique

## 🎉 Profite de l'Interface !

L'interface web rend l'utilisation de l'agent **10x plus agréable** !
Plus besoin de ligne de commande, tout est visuel et interactif 🚀
