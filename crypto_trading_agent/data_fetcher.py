"""
Module pour récupérer les données historiques des cryptomonnaies via CoinGecko API
"""
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import json
import os


class CryptoDataFetcher:
    """Récupère et gère les données historiques des cryptomonnaies"""

    def __init__(self, cache_dir='data'):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

        # Top 10 cryptos au 24/12/2024 (basé sur market cap)
        self.top_10_cryptos = {
            'bitcoin': 'BTC',
            'ethereum': 'ETH',
            'tether': 'USDT',
            'binancecoin': 'BNB',
            'solana': 'SOL',
            'usd-coin': 'USDC',
            'ripple': 'XRP',
            'cardano': 'ADA',
            'dogecoin': 'DOGE',
            'tron': 'TRX'
        }

    def get_historical_data(self, coin_id, start_date, end_date):
        """
        Récupère les données historiques pour une crypto donnée

        Args:
            coin_id: ID CoinGecko de la crypto
            start_date: Date de début (datetime)
            end_date: Date de fin (datetime)

        Returns:
            DataFrame avec les données historiques
        """
        cache_file = os.path.join(
            self.cache_dir,
            f"{coin_id}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json"
        )

        # Vérifier le cache
        if os.path.exists(cache_file):
            print(f"Loading cached data for {coin_id}")
            with open(cache_file, 'r') as f:
                data = json.load(f)
            return pd.DataFrame(data)

        # Calculer les timestamps
        from_timestamp = int(start_date.timestamp())
        to_timestamp = int(end_date.timestamp())

        url = f"{self.base_url}/coins/{coin_id}/market_chart/range"
        params = {
            'vs_currency': 'eur',
            'from': from_timestamp,
            'to': to_timestamp
        }

        print(f"Fetching data for {coin_id}...")
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Convertir en DataFrame
            df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['coin_id'] = coin_id
            df['symbol'] = self.top_10_cryptos.get(coin_id, coin_id.upper())

            # Ajouter volume et market cap si disponibles
            if 'total_volumes' in data:
                volumes = pd.DataFrame(data['total_volumes'], columns=['timestamp', 'volume'])
                volumes['timestamp'] = pd.to_datetime(volumes['timestamp'], unit='ms')
                df = df.merge(volumes, on='timestamp', how='left')

            # Sauvegarder dans le cache
            df.to_json(cache_file, orient='records', date_format='iso')

            # Respecter les limites de l'API
            time.sleep(1.5)

            return df

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {coin_id}: {e}")
            return pd.DataFrame()

    def get_all_top10_data(self, start_date, end_date):
        """
        Récupère les données pour toutes les cryptos du top 10

        Args:
            start_date: Date de début
            end_date: Date de fin

        Returns:
            Dict avec les DataFrames pour chaque crypto
        """
        all_data = {}

        for coin_id, symbol in self.top_10_cryptos.items():
            print(f"\nFetching {symbol} ({coin_id})...")
            df = self.get_historical_data(coin_id, start_date, end_date)
            if not df.empty:
                # Resample pour avoir des données journalières
                df = df.set_index('timestamp').resample('D').agg({
                    'price': 'mean',
                    'volume': 'sum' if 'volume' in df.columns else lambda x: 0
                }).reset_index()
                df['coin_id'] = coin_id
                df['symbol'] = symbol
                all_data[symbol] = df

        return all_data

    def get_daily_prices(self, all_data, date):
        """
        Récupère les prix de toutes les cryptos pour une date donnée

        Args:
            all_data: Dict avec les données de toutes les cryptos
            date: Date pour laquelle récupérer les prix

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
                # Si pas de correspondance exacte, prendre le prix le plus proche
                closest_idx = (df_copy['timestamp'] - target_date).abs().idxmin()
                prices[symbol] = df_copy.loc[closest_idx, 'price']

        return prices


if __name__ == "__main__":
    # Test du module
    fetcher = CryptoDataFetcher()

    start = datetime(2024, 12, 24)
    end = datetime(2025, 12, 24)

    print("Testing data fetcher...")
    all_data = fetcher.get_all_top10_data(start, end)

    print(f"\nFetched data for {len(all_data)} cryptocurrencies")
    for symbol, df in all_data.items():
        print(f"{symbol}: {len(df)} days of data")
