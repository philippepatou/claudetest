"""
Module de gestion du portefeuille de trading
"""
from datetime import datetime
from typing import Dict, List, Tuple


class Portfolio:
    """Gère le portefeuille virtuel de l'agent de trading"""

    def __init__(self, initial_balance: float = 1000.0, transaction_fee: float = 0.0025,
                 use_realistic_execution: bool = True):
        """
        Initialise le portefeuille

        Args:
            initial_balance: Capital de départ en EUR
            transaction_fee: Frais de transaction (0.0025 = 0.25%)
            use_realistic_execution: Utiliser slippage et spread réalistes
        """
        self.initial_balance = initial_balance
        self.cash = initial_balance
        self.transaction_fee = transaction_fee
        self.use_realistic_execution = use_realistic_execution
        self.holdings = {}  # {symbol: quantity}
        self.transaction_history = []
        self.portfolio_history = []

        # Paramètres de réalisme d'exécution
        self.spread_pct = 0.002  # 0.2% de spread bid/ask
        self.market_depth_eur = 50000  # Liquidité moyenne du market
        self.max_slippage_pct = 0.005  # 0.5% slippage maximum

    def calculate_slippage(self, order_size_eur: float) -> float:
        """
        Calcule le slippage basé sur la taille de l'ordre

        Args:
            order_size_eur: Taille de l'ordre en EUR

        Returns:
            Slippage en pourcentage (ex: 0.002 = 0.2%)
        """
        if not self.use_realistic_execution:
            return 0.0

        # Impact ratio: taille de l'ordre / liquidité du marché
        impact_ratio = order_size_eur / self.market_depth_eur

        # Slippage proportionnel à l'impact
        # Formule: 0.1% de slippage par 10% de market depth consommé
        slippage = impact_ratio * 0.001

        # Limiter au maximum
        return min(self.max_slippage_pct, slippage)

    def get_total_value(self, current_prices: Dict[str, float]) -> float:
        """
        Calcule la valeur totale du portefeuille

        Args:
            current_prices: Dict {symbol: price} des prix actuels

        Returns:
            Valeur totale en EUR
        """
        total = self.cash

        for symbol, quantity in self.holdings.items():
            if symbol in current_prices and quantity > 0:
                total += quantity * current_prices[symbol]

        return total

    def buy(self, symbol: str, amount_eur: float, price: float, date: datetime, order_type: str = 'market') -> bool:
        """
        Achète une crypto avec slippage et spread réalistes

        Args:
            symbol: Symbole de la crypto
            amount_eur: Montant en EUR à investir
            price: Prix actuel de la crypto (mid price)
            date: Date de la transaction
            order_type: Type d'ordre (market, limit, stop)

        Returns:
            True si l'achat a réussi, False sinon
        """
        if amount_eur <= 0:
            return False

        # Calculer le slippage
        slippage = self.calculate_slippage(amount_eur)

        # Prix d'exécution réel pour un achat (ask price + slippage)
        # Pour acheter, on paie le spread (moitié) + slippage
        spread_cost = self.spread_pct / 2 if self.use_realistic_execution else 0
        execution_price = price * (1 + spread_cost + slippage)

        # Coût total avec fees
        total_cost = amount_eur * (1 + self.transaction_fee + spread_cost + slippage)

        # Vérifier si assez de cash
        if total_cost > self.cash:
            return False

        # Calculer la quantité obtenue (avec le prix d'exécution réel)
        quantity = amount_eur / execution_price

        # Exécuter l'achat
        self.cash -= total_cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity

        # Enregistrer la transaction
        self.transaction_history.append({
            'date': date,
            'type': 'buy',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'execution_price': execution_price,
            'amount_eur': amount_eur,
            'fee': amount_eur * self.transaction_fee,
            'slippage': slippage,
            'spread_cost': spread_cost,
            'total_cost': total_cost,
            'order_type': order_type
        })

        return True

    def sell(self, symbol: str, quantity: float, price: float, date: datetime, order_type: str = 'market') -> bool:
        """
        Vend une crypto avec slippage et spread réalistes

        Args:
            symbol: Symbole de la crypto
            quantity: Quantité à vendre
            price: Prix actuel de la crypto (mid price)
            date: Date de la transaction
            order_type: Type d'ordre (market, limit, stop)

        Returns:
            True si la vente a réussi, False sinon
        """
        if quantity <= 0:
            return False

        # Vérifier si assez de crypto
        if symbol not in self.holdings or self.holdings[symbol] < quantity:
            return False

        # Montant théorique au mid price
        amount_eur_mid = quantity * price

        # Calculer le slippage
        slippage = self.calculate_slippage(amount_eur_mid)

        # Prix d'exécution réel pour une vente (bid price - slippage)
        # Pour vendre, on reçoit le prix minus le spread (moitié) et minus le slippage
        spread_cost = self.spread_pct / 2 if self.use_realistic_execution else 0
        execution_price = price * (1 - spread_cost - slippage)

        # Montant réel obtenu
        amount_eur = quantity * execution_price
        fee = amount_eur * self.transaction_fee
        net_amount = amount_eur - fee

        # Exécuter la vente
        self.holdings[symbol] -= quantity
        self.cash += net_amount

        # Nettoyer si quantité devient 0
        if self.holdings[symbol] < 1e-8:
            del self.holdings[symbol]

        # Enregistrer la transaction
        self.transaction_history.append({
            'date': date,
            'type': 'sell',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'execution_price': execution_price,
            'amount_eur': amount_eur,
            'fee': fee,
            'slippage': slippage,
            'spread_cost': spread_cost,
            'net_amount': net_amount,
            'order_type': order_type
        })

        return True

    def sell_all(self, symbol: str, price: float, date: datetime) -> bool:
        """
        Vend toute la quantité d'une crypto

        Args:
            symbol: Symbole de la crypto
            price: Prix actuel
            date: Date de la transaction

        Returns:
            True si la vente a réussi
        """
        if symbol not in self.holdings or self.holdings[symbol] <= 0:
            return False

        return self.sell(symbol, self.holdings[symbol], price, date)

    def get_holding_value(self, symbol: str, current_price: float) -> float:
        """
        Calcule la valeur d'une position

        Args:
            symbol: Symbole de la crypto
            current_price: Prix actuel

        Returns:
            Valeur en EUR
        """
        if symbol not in self.holdings:
            return 0.0

        return self.holdings[symbol] * current_price

    def get_allocation(self, current_prices: Dict[str, float]) -> Dict[str, float]:
        """
        Calcule l'allocation du portefeuille en pourcentage

        Args:
            current_prices: Prix actuels de toutes les cryptos

        Returns:
            Dict {symbol: percentage}
        """
        total_value = self.get_total_value(current_prices)
        if total_value == 0:
            return {}

        allocation = {'CASH': (self.cash / total_value) * 100}

        for symbol, quantity in self.holdings.items():
            if symbol in current_prices and quantity > 0:
                value = quantity * current_prices[symbol]
                allocation[symbol] = (value / total_value) * 100

        return allocation

    def record_portfolio_state(self, date: datetime, current_prices: Dict[str, float]):
        """
        Enregistre l'état du portefeuille à une date donnée

        Args:
            date: Date de l'enregistrement
            current_prices: Prix actuels
        """
        total_value = self.get_total_value(current_prices)
        allocation = self.get_allocation(current_prices)

        self.portfolio_history.append({
            'date': date,
            'total_value': total_value,
            'cash': self.cash,
            'holdings': dict(self.holdings),
            'allocation': allocation,
            'roi': ((total_value - self.initial_balance) / self.initial_balance) * 100
        })

    def get_roi(self, current_prices: Dict[str, float]) -> float:
        """
        Calcule le ROI actuel

        Args:
            current_prices: Prix actuels

        Returns:
            ROI en pourcentage
        """
        total_value = self.get_total_value(current_prices)
        return ((total_value - self.initial_balance) / self.initial_balance) * 100

    def get_performance_metrics(self, current_prices: Dict[str, float]) -> Dict:
        """
        Calcule les métriques de performance

        Args:
            current_prices: Prix actuels

        Returns:
            Dict avec les métriques
        """
        total_value = self.get_total_value(current_prices)
        roi = self.get_roi(current_prices)

        # Calculer le nombre de trades
        num_trades = len(self.transaction_history)
        num_buys = sum(1 for t in self.transaction_history if t['type'] == 'buy')
        num_sells = sum(1 for t in self.transaction_history if t['type'] == 'sell')

        # Calculer les frais totaux
        total_fees = sum(t['fee'] for t in self.transaction_history)

        return {
            'initial_balance': self.initial_balance,
            'final_value': total_value,
            'roi': roi,
            'profit_loss': total_value - self.initial_balance,
            'num_trades': num_trades,
            'num_buys': num_buys,
            'num_sells': num_sells,
            'total_fees': total_fees,
            'cash': self.cash,
            'holdings': dict(self.holdings)
        }

    def __repr__(self):
        return f"Portfolio(cash={self.cash:.2f}€, holdings={len(self.holdings)})"
