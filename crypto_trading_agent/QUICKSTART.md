# Guide de Démarrage Rapide 🚀

## Installation

```bash
cd crypto_trading_agent
pip install -r requirements.txt
```

## Lancement Rapide (Mode Démo)

Le mode démo utilise des données synthétiques et ne nécessite pas d'accès Internet :

```bash
# Test rapide (50 secondes environ)
python main.py --synthetic --fast --verbose --save-reports

# Test complet (30 minutes environ - 5s par jour)
python main.py --synthetic --verbose --save-reports

# Avec plusieurs itérations pour voir l'autocritique en action
python main.py --synthetic --fast --iterations 3 --save-reports
```

## Lancement avec Données Réelles

Si vous avez accès à Internet et voulez utiliser les vraies données CoinGecko :

```bash
# Mode normal
python main.py --verbose --save-reports

# Mode rapide
python main.py --fast --verbose --save-reports
```

## Comprendre les Résultats

Après l'exécution, vous verrez :

1. **ROI** : Le retour sur investissement (objectif : >20%)
2. **Win Rate** : Pourcentage de trades gagnants
3. **Autocritique** : Analyse des erreurs et suggestions d'amélioration

Les rapports sont sauvegardés dans `reports/` :
- `iteration_X_TIMESTAMP.txt` : Rapport d'autocritique
- `iteration_X_TIMESTAMP.png` : Graphique de performance
- `params_X_TIMESTAMP.json` : Paramètres utilisés

## Exemple de Résultat

```
Initial Balance:  1000.00€
Final Value:      1430.80€
ROI:              +43.08%
Win Rate:         38.7%
```

L'agent a transformé 1000€ en 1430€ en un an, soit +43% de profit !

## Itérations Multiples

Le système d'autocritique améliore la stratégie à chaque itération :

```bash
python main.py --synthetic --fast --iterations 5 --save-reports
```

Vous verrez l'agent apprendre de ses erreurs et optimiser ses paramètres automatiquement.

## Personnalisation

Modifiez les paramètres dans `main.py` (ligne ~150) :

```python
strategy_params = {
    'risk_per_trade': 0.15,        # 15% du capital par trade
    'max_allocation_per_coin': 0.25,  # Max 25% dans une crypto
    'stop_loss': 0.10,             # Stop loss à -10%
    'take_profit': 0.20,           # Take profit à +20%
    # ... autres paramètres
}
```

## Problèmes Courants

### Erreur de connexion à l'API
→ Utilisez `--synthetic` pour le mode démo sans Internet

### Installation échoue
→ Vérifiez que vous avez Python 3.8+
→ Utilisez un environnement virtuel

### Trop lent
→ Utilisez `--fast` pour accélérer (0.1s par jour au lieu de 5s)

## Amusez-vous bien ! 🎉
