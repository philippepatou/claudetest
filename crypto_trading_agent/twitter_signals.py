"""
Module de signaux Twitter pour le trading de cryptomonnaies
Simule des conseils d'achat/vente de comptes Twitter influents

NOTE: Version synthétique pour démo. Pour utiliser de vrais tweets :
1. Obtenir des clés API Twitter/X (https://developer.twitter.com)
2. Installer tweepy: pip install tweepy
3. Remplacer TwitterSignalGenerator par TwitterAPIFetcher
"""
import random
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd
import numpy as np


class TwitterSignal:
    """Représente un signal Twitter d'un influenceur crypto"""

    def __init__(self, account: str, symbol: str, signal: str,
                 confidence: float, timestamp: datetime, reason: str = ""):
        """
        Args:
            account: Compte Twitter (@username)
            symbol: Symbole de la crypto (BTC, ETH, etc.)
            signal: Type de signal ('BUY', 'SELL', 'HOLD', 'NEUTRAL')
            confidence: Niveau de confiance du signal (0-1)
            timestamp: Date/heure du signal
            reason: Raison du signal (texte du tweet simplifié)
        """
        self.account = account
        self.symbol = symbol
        self.signal = signal
        self.confidence = confidence
        self.timestamp = timestamp
        self.reason = reason

    def __repr__(self):
        return (f"TwitterSignal({self.account}: {self.signal} {self.symbol} "
                f"[{self.confidence:.0%}] on {self.timestamp.date()})")


class TwitterInfluencers:
    """Base de données des influenceurs crypto à suivre"""

    # Comptes avec leur poids d'influence (0-1)
    INFLUENCERS = {
        # Comptes internationaux majeurs
        '@cz_binance': {'weight': 1.0, 'specialty': 'general', 'language': 'en'},
        '@MessariCrypto': {'weight': 0.95, 'specialty': 'analytics', 'language': 'en'},
        '@CoinDesk': {'weight': 0.85, 'specialty': 'news', 'language': 'en'},
        '@WatcherGuru': {'weight': 0.80, 'specialty': 'whales', 'language': 'en'},

        # Analystes techniques
        '@IncomeSharks': {'weight': 0.90, 'specialty': 'technical', 'language': 'en'},
        '@CryptoCred': {'weight': 0.88, 'specialty': 'technical', 'language': 'en'},
        '@CryptoDonAlt': {'weight': 0.85, 'specialty': 'technical', 'language': 'en'},
        '@Clementte': {'weight': 0.87, 'specialty': 'onchain', 'language': 'en'},

        # Comptes francophones
        '@cryptomatrix2': {'weight': 0.82, 'specialty': 'technical', 'language': 'fr'},
        '@cryptonaute_btc': {'weight': 0.75, 'specialty': 'education', 'language': 'fr'},
        '@aucoinDubloc': {'weight': 0.70, 'specialty': 'news', 'language': 'fr'},
        '@crypto__Goku': {'weight': 0.72, 'specialty': 'trends', 'language': 'fr'},
        '@cryptopicsou': {'weight': 0.78, 'specialty': 'trading', 'language': 'fr'},
        '@CFarmeur': {'weight': 0.75, 'specialty': 'defi', 'language': 'fr'},
    }

    @classmethod
    def get_weight(cls, account: str) -> float:
        """Retourne le poids d'influence d'un compte"""
        return cls.INFLUENCERS.get(account, {}).get('weight', 0.5)

    @classmethod
    def get_all_accounts(cls) -> List[str]:
        """Retourne la liste de tous les comptes"""
        return list(cls.INFLUENCERS.keys())


class TwitterSignalGenerator:
    """Génère des signaux Twitter synthétiques basés sur les mouvements de marché"""

    def __init__(self, seed: int = 42):
        """
        Initialise le générateur de signaux

        Args:
            seed: Seed pour reproductibilité
        """
        np.random.seed(seed)
        random.seed(seed)
        self.influencers = TwitterInfluencers()

    def generate_signals_for_date(self, date: datetime,
                                  price_data: Dict[str, pd.DataFrame]) -> List[TwitterSignal]:
        """
        Génère des signaux Twitter pour une date donnée

        Args:
            date: Date pour laquelle générer les signaux
            price_data: Données de prix historiques {symbol: DataFrame}

        Returns:
            Liste de TwitterSignal
        """
        signals = []

        # Nombre de signaux par jour (aléatoire, 0-5)
        num_signals = random.randint(0, 5)

        for _ in range(num_signals):
            # Choisir un compte aléatoire
            account = random.choice(self.influencers.get_all_accounts())

            # Choisir une crypto aléatoire
            available_symbols = list(price_data.keys())
            if not available_symbols:
                continue

            symbol = random.choice(available_symbols)

            # Analyser la tendance récente pour générer un signal cohérent
            df = price_data[symbol]
            recent_data = df[df['timestamp'] <= date].tail(7)  # 7 derniers jours

            if len(recent_data) < 3:
                continue

            # Calculer la variation récente
            price_change = ((recent_data['price'].iloc[-1] - recent_data['price'].iloc[0])
                           / recent_data['price'].iloc[0])

            # Générer un signal basé sur la tendance + aléatoire
            signal, confidence, reason = self._generate_signal(
                symbol, price_change, account
            )

            # Créer le signal
            twitter_signal = TwitterSignal(
                account=account,
                symbol=symbol,
                signal=signal,
                confidence=confidence,
                timestamp=date,
                reason=reason
            )

            signals.append(twitter_signal)

        return signals

    def _generate_signal(self, symbol: str, price_change: float,
                        account: str) -> tuple:
        """
        Génère un signal basé sur le mouvement de prix

        Args:
            symbol: Symbole de la crypto
            price_change: Variation de prix (en décimal)
            account: Compte Twitter

        Returns:
            (signal, confidence, reason)
        """
        # Influence de la tendance sur le signal
        trend_strength = abs(price_change)

        # Aléatoire avec biais vers la tendance
        rand = random.random()

        # Si forte hausse
        if price_change > 0.10:  # +10%
            if rand < 0.6:  # 60% de chance de BUY
                signal = 'BUY'
                confidence = min(0.9, 0.6 + trend_strength)
                reason = f"Strong upward momentum on ${symbol}. Bullish pattern emerging."
            elif rand < 0.9:
                signal = 'HOLD'
                confidence = 0.7
                reason = f"${symbol} showing strength. Wait for pullback to enter."
            else:
                signal = 'SELL'
                confidence = 0.6
                reason = f"${symbol} overbought. Consider taking profits."

        # Si forte baisse
        elif price_change < -0.10:  # -10%
            if rand < 0.5:  # 50% de chance de BUY (buy the dip)
                signal = 'BUY'
                confidence = min(0.85, 0.5 + trend_strength)
                reason = f"${symbol} dip presents buying opportunity. Accumulation zone."
            elif rand < 0.8:
                signal = 'HOLD'
                confidence = 0.65
                reason = f"${symbol} correction ongoing. Watch for support levels."
            else:
                signal = 'SELL'
                confidence = 0.75
                reason = f"${symbol} breaking down. Bearish trend confirmed."

        # Tendance modérée
        else:
            if rand < 0.4:
                signal = 'BUY'
                confidence = 0.6 + random.random() * 0.2
                reason = f"${symbol} consolidating. Good entry point."
            elif rand < 0.7:
                signal = 'HOLD'
                confidence = 0.7
                reason = f"${symbol} range-bound. Waiting for breakout."
            else:
                signal = 'SELL'
                confidence = 0.55 + random.random() * 0.15
                reason = f"${symbol} losing momentum. Consider reducing exposure."

        return signal, confidence, reason

    def aggregate_signals(self, signals: List[TwitterSignal], symbol: str) -> Dict:
        """
        Agrège les signaux Twitter pour une crypto donnée

        Args:
            signals: Liste de signaux
            symbol: Symbole de la crypto

        Returns:
            Dict avec le signal agrégé et les détails
        """
        # Filtrer les signaux pour ce symbole
        relevant_signals = [s for s in signals if s.symbol == symbol]

        if not relevant_signals:
            return {
                'signal': 'NEUTRAL',
                'confidence': 0.0,
                'num_signals': 0,
                'details': []
            }

        # Calculer le score pondéré
        buy_score = 0.0
        sell_score = 0.0
        hold_score = 0.0

        for sig in relevant_signals:
            weight = self.influencers.get_weight(sig.account)
            weighted_confidence = sig.confidence * weight

            if sig.signal == 'BUY':
                buy_score += weighted_confidence
            elif sig.signal == 'SELL':
                sell_score += weighted_confidence
            elif sig.signal == 'HOLD':
                hold_score += weighted_confidence

        # Normaliser
        total_score = buy_score + sell_score + hold_score
        if total_score == 0:
            return {
                'signal': 'NEUTRAL',
                'confidence': 0.0,
                'num_signals': len(relevant_signals),
                'details': relevant_signals
            }

        buy_pct = buy_score / total_score
        sell_pct = sell_score / total_score
        hold_pct = hold_score / total_score

        # Déterminer le signal dominant
        if buy_pct > max(sell_pct, hold_pct):
            signal = 'BUY'
            confidence = buy_pct
        elif sell_pct > max(buy_pct, hold_pct):
            signal = 'SELL'
            confidence = sell_pct
        else:
            signal = 'HOLD'
            confidence = hold_pct

        return {
            'signal': signal,
            'confidence': confidence,
            'num_signals': len(relevant_signals),
            'buy_score': buy_pct,
            'sell_score': sell_pct,
            'hold_score': hold_pct,
            'details': relevant_signals
        }


# Pour intégration future avec la vraie API Twitter
class TwitterAPIFetcher:
    """
    Classe pour intégrer la vraie API Twitter (à implémenter)

    Installation requise:
    pip install tweepy

    Configuration:
    1. Créer un compte développeur sur https://developer.twitter.com
    2. Créer une application et obtenir les clés API
    3. Configurer les clés dans un fichier .env
    """

    def __init__(self, api_key: str, api_secret: str,
                 access_token: str, access_token_secret: str):
        """
        Initialise la connexion à l'API Twitter

        Args:
            api_key: Clé API Twitter
            api_secret: Secret API Twitter
            access_token: Token d'accès
            access_token_secret: Secret du token
        """
        raise NotImplementedError(
            "Twitter API integration requires:\n"
            "1. Twitter Developer account\n"
            "2. API keys (paid plan)\n"
            "3. pip install tweepy\n"
            "Use TwitterSignalGenerator for synthetic data instead."
        )


if __name__ == "__main__":
    # Test du générateur de signaux
    generator = TwitterSignalGenerator()

    # Créer des données de prix fictives
    dates = pd.date_range(start='2024-12-01', end='2024-12-10', freq='D')
    price_data = {
        'BTC': pd.DataFrame({
            'timestamp': dates,
            'price': [50000 + i*1000 for i in range(len(dates))]
        }),
        'ETH': pd.DataFrame({
            'timestamp': dates,
            'price': [3000 - i*50 for i in range(len(dates))]
        })
    }

    # Générer des signaux
    test_date = datetime(2024, 12, 10)
    signals = generator.generate_signals_for_date(test_date, price_data)

    print(f"Generated {len(signals)} Twitter signals for {test_date.date()}:\n")
    for sig in signals:
        print(f"  {sig}")
        print(f"    → {sig.reason}\n")

    # Agréger les signaux par crypto
    for symbol in ['BTC', 'ETH']:
        aggregated = generator.aggregate_signals(signals, symbol)
        print(f"\nAggregated signal for {symbol}:")
        print(f"  Signal: {aggregated['signal']}")
        print(f"  Confidence: {aggregated['confidence']:.1%}")
        print(f"  Based on {aggregated['num_signals']} tweets")
