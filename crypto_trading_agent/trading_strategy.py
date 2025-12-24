"""
Module de stratégie de trading hybride
Combine indicateurs techniques et analyse de momentum
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class TradingStrategy:
    """Stratégie de trading hybride avec indicateurs techniques"""

    def __init__(self, parameters: Dict = None):
        """
        Initialise la stratégie avec des paramètres configurables

        Args:
            parameters: Dict de paramètres de la stratégie
        """
        # Paramètres par défaut
        self.params = {
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'ema_short': 12,
            'ema_long': 26,
            'macd_signal': 9,
            'bb_period': 20,
            'bb_std': 2,
            'momentum_period': 10,
            'min_history': 30,  # Minimum de jours d'historique nécessaires
            'risk_per_trade': 0.15,  # Maximum 15% du capital par trade
            'max_allocation_per_coin': 0.25,  # Maximum 25% dans une seule crypto
            'stop_loss': 0.10,  # Stop loss à -10%
            'take_profit': 0.20,  # Take profit à +20%
        }

        # Mettre à jour avec les paramètres fournis
        if parameters:
            self.params.update(parameters)

    def calculate_rsi(self, prices: pd.Series, period: int = None) -> pd.Series:
        """
        Calcule le RSI (Relative Strength Index)

        Args:
            prices: Série de prix
            period: Période pour le calcul

        Returns:
            Série RSI
        """
        if period is None:
            period = self.params['rsi_period']

        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def calculate_macd(self, prices: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calcule le MACD (Moving Average Convergence Divergence)

        Args:
            prices: Série de prix

        Returns:
            Tuple (MACD, signal, histogram)
        """
        ema_short = prices.ewm(span=self.params['ema_short'], adjust=False).mean()
        ema_long = prices.ewm(span=self.params['ema_long'], adjust=False).mean()

        macd = ema_short - ema_long
        signal = macd.ewm(span=self.params['macd_signal'], adjust=False).mean()
        histogram = macd - signal

        return macd, signal, histogram

    def calculate_bollinger_bands(self, prices: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calcule les Bollinger Bands

        Args:
            prices: Série de prix

        Returns:
            Tuple (upper, middle, lower)
        """
        period = self.params['bb_period']
        std_dev = self.params['bb_std']

        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()

        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)

        return upper, middle, lower

    def calculate_momentum(self, prices: pd.Series, period: int = None) -> pd.Series:
        """
        Calcule le momentum

        Args:
            prices: Série de prix
            period: Période pour le calcul

        Returns:
            Série de momentum
        """
        if period is None:
            period = self.params['momentum_period']

        momentum = prices.pct_change(periods=period) * 100
        return momentum

    def calculate_ema(self, prices: pd.Series, period: int) -> pd.Series:
        """
        Calcule l'EMA (Exponential Moving Average)

        Args:
            prices: Série de prix
            period: Période

        Returns:
            Série EMA
        """
        return prices.ewm(span=period, adjust=False).mean()

    def analyze_crypto(self, df: pd.DataFrame) -> Dict:
        """
        Analyse une crypto avec tous les indicateurs

        Args:
            df: DataFrame avec colonnes 'timestamp' et 'price'

        Returns:
            Dict avec les signaux et scores
        """
        if len(df) < self.params['min_history']:
            return {'signal': 'HOLD', 'score': 0, 'reason': 'Insufficient history'}

        prices = df['price'].copy()

        # Calculer tous les indicateurs
        rsi = self.calculate_rsi(prices)
        macd, macd_signal, macd_hist = self.calculate_macd(prices)
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(prices)
        momentum = self.calculate_momentum(prices)
        ema_short = self.calculate_ema(prices, self.params['ema_short'])
        ema_long = self.calculate_ema(prices, self.params['ema_long'])

        # Valeurs actuelles (dernière ligne)
        current_price = prices.iloc[-1]
        current_rsi = rsi.iloc[-1]
        current_macd = macd.iloc[-1]
        current_macd_signal = macd_signal.iloc[-1]
        current_macd_hist = macd_hist.iloc[-1]
        current_bb_upper = bb_upper.iloc[-1]
        current_bb_lower = bb_lower.iloc[-1]
        current_momentum = momentum.iloc[-1]
        current_ema_short = ema_short.iloc[-1]
        current_ema_long = ema_long.iloc[-1]

        # Calcul du score (de -100 à +100)
        score = 0
        reasons = []

        # 1. RSI (poids: 25 points)
        if current_rsi < self.params['rsi_oversold']:
            score += 25
            reasons.append(f"RSI oversold ({current_rsi:.1f})")
        elif current_rsi > self.params['rsi_overbought']:
            score -= 25
            reasons.append(f"RSI overbought ({current_rsi:.1f})")
        else:
            # RSI neutre
            if current_rsi < 50:
                score += (50 - current_rsi) / 2
            else:
                score -= (current_rsi - 50) / 2

        # 2. MACD (poids: 25 points)
        if current_macd > current_macd_signal and current_macd_hist > 0:
            score += 25
            reasons.append("MACD bullish crossover")
        elif current_macd < current_macd_signal and current_macd_hist < 0:
            score -= 25
            reasons.append("MACD bearish crossover")

        # 3. Bollinger Bands (poids: 20 points)
        if current_price < current_bb_lower:
            score += 20
            reasons.append("Price below lower BB")
        elif current_price > current_bb_upper:
            score -= 20
            reasons.append("Price above upper BB")

        # 4. EMA Trend (poids: 15 points)
        if current_ema_short > current_ema_long:
            score += 15
            reasons.append("Bullish EMA trend")
        else:
            score -= 15
            reasons.append("Bearish EMA trend")

        # 5. Momentum (poids: 15 points)
        if current_momentum > 5:
            score += 15
            reasons.append(f"Strong positive momentum ({current_momentum:.1f}%)")
        elif current_momentum < -5:
            score -= 15
            reasons.append(f"Strong negative momentum ({current_momentum:.1f}%)")

        # Déterminer le signal
        if score > 40:
            signal = 'BUY'
        elif score < -40:
            signal = 'SELL'
        else:
            signal = 'HOLD'

        return {
            'signal': signal,
            'score': score,
            'reasons': reasons,
            'indicators': {
                'rsi': current_rsi,
                'macd': current_macd,
                'macd_signal': current_macd_signal,
                'macd_histogram': current_macd_hist,
                'bb_upper': current_bb_upper,
                'bb_lower': current_bb_lower,
                'momentum': current_momentum,
                'ema_short': current_ema_short,
                'ema_long': current_ema_long
            }
        }

    def rank_opportunities(self, analyses: Dict[str, Dict]) -> List[Tuple[str, Dict]]:
        """
        Classe les opportunités par score

        Args:
            analyses: Dict {symbol: analysis_result}

        Returns:
            Liste triée de (symbol, analysis) par score décroissant
        """
        opportunities = [(symbol, analysis) for symbol, analysis in analyses.items()]
        opportunities.sort(key=lambda x: x[1]['score'], reverse=True)

        return opportunities

    def should_sell(self, symbol: str, entry_price: float, current_price: float,
                    analysis: Dict) -> Tuple[bool, str]:
        """
        Détermine s'il faut vendre une position

        Args:
            symbol: Symbole de la crypto
            entry_price: Prix d'entrée
            current_price: Prix actuel
            analysis: Résultat de l'analyse

        Returns:
            Tuple (should_sell, reason)
        """
        # Calculer le profit/perte
        pnl_pct = ((current_price - entry_price) / entry_price) * 100

        # Stop loss
        if pnl_pct <= -self.params['stop_loss'] * 100:
            return True, f"Stop loss triggered ({pnl_pct:.1f}%)"

        # Take profit
        if pnl_pct >= self.params['take_profit'] * 100:
            return True, f"Take profit reached ({pnl_pct:.1f}%)"

        # Signal de vente fort
        if analysis['signal'] == 'SELL' and analysis['score'] < -50:
            return True, f"Strong sell signal (score: {analysis['score']})"

        return False, ""

    def get_position_size(self, capital: float, current_price: float,
                         analysis: Dict) -> float:
        """
        Calcule la taille de position recommandée

        Args:
            capital: Capital disponible
            current_price: Prix actuel
            analysis: Résultat de l'analyse

        Returns:
            Montant en EUR à investir
        """
        # Base sur le risque par trade
        max_position = capital * self.params['risk_per_trade']

        # Ajuster selon la force du signal (score de 0 à 100)
        score_strength = min(abs(analysis['score']) / 100, 1.0)
        adjusted_position = max_position * score_strength

        return adjusted_position

    def update_parameters(self, new_params: Dict):
        """
        Met à jour les paramètres de la stratégie

        Args:
            new_params: Nouveaux paramètres
        """
        self.params.update(new_params)
