"""
Générateur de données synthétiques pour tester l'agent sans accès à l'API
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class SyntheticDataGenerator:
    """Génère des données synthétiques réalistes de cryptomonnaies"""

    def __init__(self, seed=42):
        """
        Initialise le générateur

        Args:
            seed: Seed pour la reproductibilité
        """
        np.random.seed(seed)
        self.cryptos = {
            'BTC': {'initial_price': 80000, 'volatility': 0.03, 'trend': 0.0002},
            'ETH': {'initial_price': 3500, 'volatility': 0.04, 'trend': 0.0003},
            'USDT': {'initial_price': 0.95, 'volatility': 0.001, 'trend': 0.0},
            'BNB': {'initial_price': 600, 'volatility': 0.035, 'trend': 0.0001},
            'SOL': {'initial_price': 180, 'volatility': 0.05, 'trend': 0.0004},
            'USDC': {'initial_price': 0.95, 'volatility': 0.001, 'trend': 0.0},
            'XRP': {'initial_price': 2.2, 'volatility': 0.045, 'trend': 0.0002},
            'ADA': {'initial_price': 0.85, 'volatility': 0.04, 'trend': 0.0001},
            'DOGE': {'initial_price': 0.30, 'volatility': 0.06, 'trend': 0.0001},
            'TRX': {'initial_price': 0.22, 'volatility': 0.04, 'trend': 0.00015}
        }

    def generate_price_series(self, symbol: str, start_date: datetime,
                             end_date: datetime) -> pd.DataFrame:
        """
        Génère une série de prix réaliste avec tendance et volatilité

        Args:
            symbol: Symbole de la crypto
            start_date: Date de début
            end_date: Date de fin

        Returns:
            DataFrame avec timestamp et price
        """
        config = self.cryptos.get(symbol)
        if not config:
            return pd.DataFrame()

        # Générer les dates
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        num_days = len(dates)

        # Prix initial
        prices = [config['initial_price']]

        # Générer les prix avec un random walk avec tendance
        for i in range(1, num_days):
            # Composante aléatoire (volatilité)
            random_change = np.random.normal(0, config['volatility'])

            # Composante de tendance
            trend = config['trend']

            # Ajouter quelques événements aléatoires (bull/bear runs)
            if np.random.random() < 0.05:  # 5% de chance d'événement
                event = np.random.choice([-0.10, 0.15])  # Crash ou pump
                random_change += event

            # Calculer le nouveau prix
            price_change = 1 + trend + random_change
            new_price = prices[-1] * price_change

            # S'assurer que le prix reste positif
            new_price = max(new_price, config['initial_price'] * 0.1)

            prices.append(new_price)

        # Créer le DataFrame
        df = pd.DataFrame({
            'timestamp': dates,
            'price': prices,
            'volume': np.random.uniform(1e6, 1e9, num_days)
        })

        return df

    def generate_all_data(self, start_date: datetime,
                         end_date: datetime) -> dict:
        """
        Génère les données pour toutes les cryptos

        Args:
            start_date: Date de début
            end_date: Date de fin

        Returns:
            Dict {symbol: DataFrame}
        """
        all_data = {}

        for symbol in self.cryptos.keys():
            df = self.generate_price_series(symbol, start_date, end_date)
            if not df.empty:
                all_data[symbol] = df

        return all_data

    def get_daily_prices(self, all_data: dict, date: datetime) -> dict:
        """
        Récupère les prix pour une date donnée

        Args:
            all_data: Dict avec toutes les données
            date: Date cible

        Returns:
            Dict {symbol: price}
        """
        prices = {}
        target_date = pd.Timestamp(date).normalize()

        for symbol, df in all_data.items():
            df_copy = df.copy()
            df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp']).dt.normalize()
            matching_rows = df_copy[df_copy['timestamp'] == target_date]

            if not matching_rows.empty:
                prices[symbol] = matching_rows.iloc[0]['price']
            elif len(df_copy) > 0:
                closest_idx = (df_copy['timestamp'] - target_date).abs().idxmin()
                prices[symbol] = df_copy.loc[closest_idx, 'price']

        return prices


if __name__ == "__main__":
    # Test du générateur
    generator = SyntheticDataGenerator()

    start = datetime(2024, 12, 24)
    end = datetime(2025, 12, 24)

    print("Generating synthetic data...")
    all_data = generator.generate_all_data(start, end)

    print(f"\nGenerated data for {len(all_data)} cryptocurrencies:")
    for symbol, df in all_data.items():
        initial = df.iloc[0]['price']
        final = df.iloc[-1]['price']
        roi = ((final - initial) / initial) * 100
        print(f"  {symbol}: {len(df)} days, "
              f"Price {initial:.4f}€ → {final:.4f}€ (ROI: {roi:+.1f}%)")
