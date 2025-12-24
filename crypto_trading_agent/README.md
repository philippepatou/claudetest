# Agent de Trading de Cryptomonnaies 🤖💰

Agent autonome de trading de cryptomonnaies avec stratégie hybride et système d'autocritique.

## 🎯 Objectif

L'agent commence avec 1000€ virtuels et tente de maximiser son ROI en tradant sur le top 10 des cryptomonnaies. Il analyse les données historiques, prend des décisions basées sur des indicateurs techniques, et s'améliore via un système d'autocritique.

## 📋 Caractéristiques

- **Mode Sandbox** : Trading virtuel avec 1000€ de départ
- **Top 10 Cryptos** : BTC, ETH, USDT, BNB, SOL, USDC, XRP, ADA, DOGE, TRX
- **Période** : 24/12/2024 → 24/12/2025 (1 an)
- **Stratégie Hybride** :
  - Indicateurs techniques (RSI, MACD, Bollinger Bands, EMA)
  - Analyse de momentum
  - Gestion du risque (stop-loss, take-profit)
- **Simulation Réaliste** :
  - Frais de transaction : 0.25%
  - Types d'ordres : market, limit, stop
  - Décisions quotidiennes
- **Autocritique** : Analyse des performances et optimisation automatique

## 🚀 Installation

```bash
cd crypto_trading_agent
pip install -r requirements.txt
```

## 💻 Utilisation

### Lancement basique

```bash
python main.py
```

### Lancement avec options

```bash
# Mode rapide (0.1s par jour au lieu de 5s)
python main.py --fast

# Avec sauvegarde des rapports
python main.py --save-reports

# Plusieurs itérations avec autocritique
python main.py --iterations 3 --save-reports

# Mode verbose
python main.py --verbose --save-reports

# Personnaliser les dates et le capital
python main.py --start-date 2024-12-24 --end-date 2025-12-24 --initial-balance 1000
```

### Options disponibles

- `--start-date YYYY-MM-DD` : Date de début (défaut: 2024-12-24)
- `--end-date YYYY-MM-DD` : Date de fin (défaut: 2025-12-24)
- `--initial-balance EUR` : Capital initial (défaut: 1000)
- `--delay SECONDS` : Délai par jour simulé (défaut: 5)
- `--iterations N` : Nombre d'itérations (défaut: 1)
- `--fast` : Mode rapide (0.1s par jour)
- `--verbose` : Logs détaillés
- `--save-reports` : Sauvegarder rapports et graphiques

## 📊 Résultats

L'agent affiche :
- **ROI** : Retour sur investissement
- **Nombre de trades** : Achats et ventes
- **Taux de réussite** : Pourcentage de trades gagnants
- **Allocation** : Répartition du portefeuille
- **Autocritique** : Analyse des faiblesses

Les rapports sont sauvegardés dans le dossier `reports/` :
- Rapport textuel (.txt)
- Graphiques de performance (.png)
- Paramètres de stratégie (.json)

## 🏗️ Architecture

```
crypto_trading_agent/
├── data_fetcher.py      # Récupération données CoinGecko
├── portfolio.py         # Gestion du portefeuille
├── trading_strategy.py  # Stratégie hybride
├── agent.py            # Agent de trading
├── backtester.py       # Simulateur
├── autocritique.py     # Système d'autocritique
├── main.py             # Script principal
├── requirements.txt    # Dépendances
└── data/               # Cache des données
```

## 🧠 Stratégie de Trading

### Indicateurs Techniques

1. **RSI** (Relative Strength Index)
   - Survendu < 30 → Signal d'achat
   - Suracheté > 70 → Signal de vente

2. **MACD** (Moving Average Convergence Divergence)
   - Croisement haussier → Signal d'achat
   - Croisement baissier → Signal de vente

3. **Bollinger Bands**
   - Prix sous la bande inférieure → Opportunité d'achat
   - Prix au-dessus de la bande supérieure → Signal de vente

4. **EMA** (Exponential Moving Averages)
   - Tendance haussière/baissière

5. **Momentum**
   - Analyse de la vélocité des prix

### Gestion du Risque

- **Stop Loss** : -10% par défaut
- **Take Profit** : +20% par défaut
- **Risque par trade** : Maximum 15% du capital
- **Allocation max** : Maximum 25% par crypto
- **Diversification** : 3-7 positions recommandées

## 🔄 Système d'Autocritique

Après chaque itération, l'agent :
1. Analyse son ROI vs objectif (20% minimum)
2. Évalue son taux de réussite
3. Identifie les trades perdants
4. Détecte les opportunités manquées
5. Suggère des ajustements de paramètres

### Améliorations Automatiques

- ROI faible → Position sizes plus agressives
- Trop de cash → Seuils RSI ajustés
- Mauvais win rate → Stop-loss et take-profit optimisés
- Peu de trades → Périodes d'indicateurs raccourcies

## 📈 Exemple de Résultat

```
FINAL RESULTS
============================================================
Initial Balance:  1000.00€
Final Value:      1250.00€
Profit/Loss:      +250.00€
ROI:              +25.00%

Trading Activity:
  Total Trades:   45
  Buys:           23
  Sells:          22
  Total Fees:     12.50€

Trade Performance:
  Winning Trades: 15
  Losing Trades:  7
  Win Rate:       68.2%
```

## 🎓 Apprentissage Continu

En mode itérations multiples, l'agent :
- Teste la stratégie
- Analyse ses erreurs
- Ajuste ses paramètres
- Re-teste avec la stratégie améliorée
- Compare les performances

## ⚠️ Avertissement

Ceci est un projet éducatif en mode sandbox. Ne tradez JAMAIS avec de l'argent réel basé uniquement sur des algorithmes sans comprendre les risques. Les performances passées ne garantissent pas les résultats futurs.

## 📝 Licence

Projet éducatif - Utilisation libre

## 🤝 Contribution

N'hésitez pas à améliorer la stratégie, ajouter de nouveaux indicateurs, ou optimiser l'algorithme d'autocritique !
