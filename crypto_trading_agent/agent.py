"""
Agent de trading autonome qui prend des décisions basées sur la stratégie
"""
from datetime import datetime
from typing import Dict, List
import pandas as pd
from portfolio import Portfolio
from trading_strategy import TradingStrategy


class TradingAgent:
    """Agent autonome de trading de cryptomonnaies"""

    def __init__(self, portfolio: Portfolio, strategy: TradingStrategy):
        """
        Initialise l'agent

        Args:
            portfolio: Instance du portefeuille
            strategy: Instance de la stratégie de trading
        """
        self.portfolio = portfolio
        self.strategy = strategy
        self.entry_prices = {}  # {symbol: entry_price} pour tracking des positions
        self.decisions_log = []

    def make_daily_decisions(self, current_date: datetime, all_data: Dict[str, pd.DataFrame],
                            current_prices: Dict[str, float]):
        """
        Prend des décisions de trading pour la journée

        Args:
            current_date: Date actuelle
            all_data: Toutes les données historiques jusqu'à aujourd'hui
            current_prices: Prix actuels de toutes les cryptos
        """
        decision = {
            'date': current_date,
            'actions': [],
            'portfolio_value': self.portfolio.get_total_value(current_prices),
            'cash': self.portfolio.cash
        }

        # 1. Analyser toutes les cryptos
        analyses = {}
        for symbol, df in all_data.items():
            # Ne garder que les données jusqu'à la date actuelle
            historical_df = df[df['timestamp'] <= current_date].copy()

            if len(historical_df) >= self.strategy.params['min_history']:
                analyses[symbol] = self.strategy.analyze_crypto(historical_df)
            else:
                analyses[symbol] = {
                    'signal': 'HOLD',
                    'score': 0,
                    'reasons': ['Insufficient data'],
                    'indicators': {}
                }

        # 2. Vérifier les positions existantes et gérer les stops/profits
        for symbol in list(self.portfolio.holdings.keys()):
            if symbol not in current_prices:
                continue

            current_price = current_prices[symbol]
            entry_price = self.entry_prices.get(symbol, current_price)

            # Vérifier s'il faut vendre
            should_sell, reason = self.strategy.should_sell(
                symbol, entry_price, current_price, analyses[symbol]
            )

            if should_sell:
                success = self.portfolio.sell_all(symbol, current_price, current_date)
                if success:
                    pnl = ((current_price - entry_price) / entry_price) * 100
                    decision['actions'].append({
                        'action': 'SELL',
                        'symbol': symbol,
                        'reason': reason,
                        'price': current_price,
                        'pnl_pct': pnl
                    })
                    if symbol in self.entry_prices:
                        del self.entry_prices[symbol]

        # 3. Identifier les opportunités d'achat
        ranked_opportunities = self.strategy.rank_opportunities(analyses)

        # Filtrer uniquement les signaux d'achat
        buy_opportunities = [
            (symbol, analysis) for symbol, analysis in ranked_opportunities
            if analysis['signal'] == 'BUY' and analysis['score'] > 30
        ]

        # 4. Exécuter les achats pour les meilleures opportunités
        total_value = self.portfolio.get_total_value(current_prices)
        allocation = self.portfolio.get_allocation(current_prices)

        for symbol, analysis in buy_opportunities[:3]:  # Top 3 opportunités max par jour
            current_price = current_prices[symbol]

            # Vérifier si on a déjà cette position
            if symbol in self.portfolio.holdings:
                current_allocation = allocation.get(symbol, 0)
                # Ne pas acheter plus si déjà > max_allocation
                if current_allocation >= self.strategy.params['max_allocation_per_coin'] * 100:
                    continue

            # Calculer la taille de position
            available_capital = self.portfolio.cash * 0.95  # Garder 5% de cash
            position_size = self.strategy.get_position_size(
                available_capital, current_price, analysis
            )

            # Vérifier qu'on ne dépasse pas l'allocation max
            max_position = total_value * self.strategy.params['max_allocation_per_coin']
            current_holding_value = self.portfolio.get_holding_value(symbol, current_price)
            if current_holding_value + position_size > max_position:
                position_size = max(0, max_position - current_holding_value)

            # Exécuter l'achat
            if position_size > 10:  # Minimum 10€ par trade
                success = self.portfolio.buy(symbol, position_size, current_price, current_date)
                if success:
                    self.entry_prices[symbol] = current_price
                    decision['actions'].append({
                        'action': 'BUY',
                        'symbol': symbol,
                        'amount_eur': position_size,
                        'price': current_price,
                        'score': analysis['score'],
                        'reasons': analysis['reasons']
                    })

        # 5. Enregistrer l'état du portefeuille
        self.portfolio.record_portfolio_state(current_date, current_prices)

        # Enregistrer la décision
        self.decisions_log.append(decision)

        return decision

    def get_performance_summary(self, current_prices: Dict[str, float]) -> Dict:
        """
        Obtient un résumé de la performance

        Args:
            current_prices: Prix actuels

        Returns:
            Dict avec les métriques de performance
        """
        metrics = self.portfolio.get_performance_metrics(current_prices)

        # Ajouter des statistiques sur les décisions
        total_decisions = len(self.decisions_log)
        total_actions = sum(len(d['actions']) for d in self.decisions_log)

        if self.portfolio.transaction_history:
            buy_trades = [t for t in self.portfolio.transaction_history if t['type'] == 'buy']
            sell_trades = [t for t in self.portfolio.transaction_history if t['type'] == 'sell']

            # Calculer les trades gagnants/perdants
            winning_trades = 0
            losing_trades = 0

            for sell in sell_trades:
                symbol = sell['symbol']
                # Trouver l'achat correspondant (simplification: dernier achat avant la vente)
                matching_buys = [b for b in buy_trades
                                if b['symbol'] == symbol and b['date'] < sell['date']]
                if matching_buys:
                    buy = matching_buys[-1]
                    if sell['price'] > buy['price']:
                        winning_trades += 1
                    else:
                        losing_trades += 1

            win_rate = (winning_trades / len(sell_trades) * 100) if sell_trades else 0

            metrics['win_rate'] = win_rate
            metrics['winning_trades'] = winning_trades
            metrics['losing_trades'] = losing_trades

        metrics['total_decisions'] = total_decisions
        metrics['total_actions'] = total_actions

        return metrics

    def analyze_mistakes(self, all_data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """
        Analyse les erreurs de trading pour l'autocritique

        Args:
            all_data: Données historiques complètes

        Returns:
            Liste des erreurs identifiées
        """
        mistakes = []

        # Analyser les ventes perdantes
        sell_trades = [t for t in self.portfolio.transaction_history if t['type'] == 'sell']
        buy_trades = [t for t in self.portfolio.transaction_history if t['type'] == 'buy']

        for sell in sell_trades:
            symbol = sell['symbol']
            # Trouver l'achat correspondant
            matching_buys = [b for b in buy_trades
                            if b['symbol'] == symbol and b['date'] < sell['date']]

            if matching_buys:
                buy = matching_buys[-1]
                pnl_pct = ((sell['price'] - buy['price']) / buy['price']) * 100

                if pnl_pct < -5:  # Perte > 5%
                    # Analyser ce qui s'est passé
                    if symbol in all_data:
                        df = all_data[symbol]
                        period_data = df[
                            (df['timestamp'] >= buy['date']) &
                            (df['timestamp'] <= sell['date'])
                        ]

                        if len(period_data) > 0:
                            max_price = period_data['price'].max()
                            max_potential_gain = ((max_price - buy['price']) / buy['price']) * 100

                            mistakes.append({
                                'type': 'losing_trade',
                                'symbol': symbol,
                                'buy_date': buy['date'],
                                'sell_date': sell['date'],
                                'buy_price': buy['price'],
                                'sell_price': sell['price'],
                                'pnl_pct': pnl_pct,
                                'max_potential_gain': max_potential_gain,
                                'reason': 'Sold at loss when could have waited'
                                         if max_potential_gain > 0 else 'Bad entry timing'
                            })

        # Analyser les opportunités manquées
        # (simplifié: cryptos qu'on n'a jamais achetées mais qui ont bien performé)
        for symbol, df in all_data.items():
            traded_symbols = set(t['symbol'] for t in self.portfolio.transaction_history)

            if symbol not in traded_symbols and len(df) > 30:
                start_price = df.iloc[0]['price']
                end_price = df.iloc[-1]['price']
                potential_gain = ((end_price - start_price) / start_price) * 100

                if potential_gain > 50:  # Opportunité manquée > 50% gain
                    mistakes.append({
                        'type': 'missed_opportunity',
                        'symbol': symbol,
                        'potential_gain': potential_gain,
                        'reason': f'Never traded {symbol} which gained {potential_gain:.1f}%'
                    })

        return mistakes

    def get_strategy_parameters(self) -> Dict:
        """Retourne les paramètres actuels de la stratégie"""
        return self.strategy.params.copy()

    def update_strategy(self, new_params: Dict):
        """
        Met à jour les paramètres de la stratégie

        Args:
            new_params: Nouveaux paramètres
        """
        self.strategy.update_parameters(new_params)
