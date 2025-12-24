"""
Module de gestion du portefeuille de trading
"""
from datetime import datetime
from typing import Dict, List, Tuple


class Portfolio:
    """Gère le portefeuille virtuel de l'agent de trading"""

    def __init__(self, initial_balance: float = 1000.0, transaction_fee: float = 0.0025):
        """
        Initialise le portefeuille

        Args:
            initial_balance: Capital de départ en EUR
            transaction_fee: Frais de transaction (0.0025 = 0.25%)
        """
        self.initial_balance = initial_balance
        self.cash = initial_balance
        self.transaction_fee = transaction_fee
        self.holdings = {}  # {symbol: quantity}
        self.transaction_history = []
        self.portfolio_history = []

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
        Achète une crypto

        Args:
            symbol: Symbole de la crypto
            amount_eur: Montant en EUR à investir
            price: Prix actuel de la crypto
            date: Date de la transaction
            order_type: Type d'ordre (market, limit, stop)

        Returns:
            True si l'achat a réussi, False sinon
        """
        if amount_eur <= 0:
            return False

        # Vérifier si assez de cash
        total_cost = amount_eur * (1 + self.transaction_fee)
        if total_cost > self.cash:
            return False

        # Calculer la quantité
        quantity = amount_eur / price

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
            'amount_eur': amount_eur,
            'fee': amount_eur * self.transaction_fee,
            'order_type': order_type
        })

        return True

    def sell(self, symbol: str, quantity: float, price: float, date: datetime, order_type: str = 'market') -> bool:
        """
        Vend une crypto

        Args:
            symbol: Symbole de la crypto
            quantity: Quantité à vendre
            price: Prix actuel de la crypto
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

        # Calculer le montant
        amount_eur = quantity * price
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
            'amount_eur': amount_eur,
            'fee': fee,
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
