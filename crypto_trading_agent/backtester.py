"""
Module de backtesting/simulation pour tester l'agent de trading
"""
import time
from datetime import datetime, timedelta
from typing import Dict
import pandas as pd
from portfolio import Portfolio
from trading_strategy import TradingStrategy
from agent import TradingAgent
from data_fetcher import CryptoDataFetcher
from synthetic_data import SyntheticDataGenerator


class Backtester:
    """Simule le trading de l'agent sur des données historiques"""

    def __init__(self, start_date: datetime, end_date: datetime,
                 initial_balance: float = 1000.0,
                 strategy_params: Dict = None,
                 delay_per_day: float = 5.0,
                 use_synthetic_data: bool = False,
                 use_twitter_signals: bool = True):
        """
        Initialise le backtester

        Args:
            start_date: Date de début de la simulation
            end_date: Date de fin de la simulation
            initial_balance: Capital initial en EUR
            strategy_params: Paramètres de la stratégie
            delay_per_day: Délai en secondes par jour simulé
            use_synthetic_data: Utiliser des données synthétiques au lieu de l'API
            use_twitter_signals: Utiliser les signaux Twitter (True par défaut)
        """
        self.start_date = start_date
        self.end_date = end_date
        self.initial_balance = initial_balance
        self.strategy_params = strategy_params or {}
        self.delay_per_day = delay_per_day
        self.use_synthetic_data = use_synthetic_data
        self.use_twitter_signals = use_twitter_signals

        # Initialiser les composants
        if use_synthetic_data:
            self.data_fetcher = SyntheticDataGenerator()
        else:
            self.data_fetcher = CryptoDataFetcher()

        self.portfolio = Portfolio(initial_balance=initial_balance)
        self.strategy = TradingStrategy(
            parameters=strategy_params,
            use_twitter_signals=use_twitter_signals
        )
        self.agent = TradingAgent(self.portfolio, self.strategy)

        # Données
        self.all_data = {}
        self.simulation_log = []

    def load_data(self):
        """Charge toutes les données historiques nécessaires"""
        print(f"\n{'='*60}")
        print("LOADING HISTORICAL DATA")
        print(f"{'='*60}")
        print(f"Period: {self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}")

        if self.use_synthetic_data:
            print("Using synthetic data (demo mode)")
            self.all_data = self.data_fetcher.generate_all_data(
                self.start_date,
                self.end_date
            )
        else:
            print("Fetching real data from CoinGecko API")
            self.all_data = self.data_fetcher.get_all_top10_data(
                self.start_date,
                self.end_date
            )

        print(f"\nLoaded data for {len(self.all_data)} cryptocurrencies:")
        for symbol, df in self.all_data.items():
            print(f"  {symbol}: {len(df)} days")

        return len(self.all_data) > 0

    def run_simulation(self, verbose: bool = True):
        """
        Exécute la simulation jour par jour

        Args:
            verbose: Afficher les logs détaillés
        """
        if not self.all_data:
            print("Error: No data loaded. Call load_data() first.")
            return

        print(f"\n{'='*60}")
        print("STARTING TRADING SIMULATION")
        print(f"{'='*60}")
        print(f"Initial Balance: {self.initial_balance:.2f}€")
        print(f"Delay per day: {self.delay_per_day}s")
        print(f"Strategy parameters: {self.strategy_params}")

        # Générer la liste de toutes les dates
        current_date = self.start_date
        dates = []
        while current_date <= self.end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)

        total_days = len(dates)
        print(f"\nSimulating {total_days} days of trading...")
        print(f"{'='*60}\n")

        start_time = time.time()

        for day_num, current_date in enumerate(dates, 1):
            # Obtenir les prix du jour
            current_prices = self.data_fetcher.get_daily_prices(self.all_data, current_date)

            if not current_prices:
                continue

            # Créer des sous-ensembles de données jusqu'à la date actuelle
            # (l'agent ne doit pas voir le futur!)
            historical_data = {}
            for symbol, df in self.all_data.items():
                historical_data[symbol] = df[df['timestamp'] <= current_date].copy()

            # L'agent prend ses décisions
            decision = self.agent.make_daily_decisions(
                current_date, historical_data, current_prices
            )

            # Logger
            if verbose and day_num % 30 == 0:  # Afficher tous les 30 jours
                portfolio_value = self.portfolio.get_total_value(current_prices)
                roi = self.portfolio.get_roi(current_prices)
                print(f"Day {day_num}/{total_days} | {current_date.strftime('%Y-%m-%d')} | "
                      f"Value: {portfolio_value:.2f}€ | ROI: {roi:+.2f}% | "
                      f"Actions: {len(decision['actions'])}")

                if decision['actions']:
                    for action in decision['actions']:
                        if action['action'] == 'BUY':
                            print(f"  → BUY {action['symbol']} "
                                  f"({action['amount_eur']:.2f}€ @ {action['price']:.4f}€)")
                        elif action['action'] == 'SELL':
                            print(f"  → SELL {action['symbol']} "
                                  f"@ {action['price']:.4f}€ (PnL: {action['pnl_pct']:+.2f}%)")

            # Attendre le délai configuré (simulation temps réel)
            time.sleep(self.delay_per_day)

        elapsed_time = time.time() - start_time

        print(f"\n{'='*60}")
        print("SIMULATION COMPLETED")
        print(f"{'='*60}")
        print(f"Total time: {elapsed_time:.1f}s ({elapsed_time/60:.1f} minutes)")

        # Afficher les résultats finaux
        self.print_final_results(current_prices)

    def print_final_results(self, final_prices: Dict[str, float]):
        """
        Affiche les résultats finaux de la simulation

        Args:
            final_prices: Prix finaux de toutes les cryptos
        """
        metrics = self.agent.get_performance_summary(final_prices)

        print(f"\n{'='*60}")
        print("FINAL RESULTS")
        print(f"{'='*60}")
        print(f"Initial Balance:  {metrics['initial_balance']:.2f}€")
        print(f"Final Value:      {metrics['final_value']:.2f}€")
        print(f"Profit/Loss:      {metrics['profit_loss']:+.2f}€")
        print(f"ROI:              {metrics['roi']:+.2f}%")
        print(f"\nTrading Activity:")
        print(f"  Total Trades:   {metrics['num_trades']}")
        print(f"  Buys:           {metrics['num_buys']}")
        print(f"  Sells:          {metrics['num_sells']}")
        print(f"  Total Fees:     {metrics['total_fees']:.2f}€")

        if 'win_rate' in metrics:
            print(f"\nTrade Performance:")
            print(f"  Winning Trades: {metrics['winning_trades']}")
            print(f"  Losing Trades:  {metrics['losing_trades']}")
            print(f"  Win Rate:       {metrics['win_rate']:.1f}%")

        print(f"\nFinal Portfolio:")
        print(f"  Cash:           {metrics['cash']:.2f}€")
        if metrics['holdings']:
            print(f"  Holdings:")
            allocation = self.portfolio.get_allocation(final_prices)
            for symbol, quantity in metrics['holdings'].items():
                if symbol in final_prices:
                    value = quantity * final_prices[symbol]
                    alloc_pct = allocation.get(symbol, 0)
                    print(f"    {symbol}: {quantity:.6f} ({value:.2f}€, {alloc_pct:.1f}%)")

    def get_results_dataframe(self) -> pd.DataFrame:
        """
        Retourne l'historique du portefeuille sous forme de DataFrame

        Returns:
            DataFrame avec l'évolution du portefeuille
        """
        if not self.portfolio.portfolio_history:
            return pd.DataFrame()

        df = pd.DataFrame(self.portfolio.portfolio_history)
        return df

    def plot_performance(self, save_path: str = None):
        """
        Génère un graphique de la performance

        Args:
            save_path: Chemin pour sauvegarder le graphique
        """
        try:
            import matplotlib.pyplot as plt

            df = self.get_results_dataframe()
            if df.empty:
                print("No data to plot")
                return

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

            # Graphique 1: Valeur du portefeuille
            ax1.plot(df['date'], df['total_value'], linewidth=2)
            ax1.axhline(y=self.initial_balance, color='r', linestyle='--',
                       label=f'Initial: {self.initial_balance}€')
            ax1.set_title('Portfolio Value Over Time', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Value (EUR)')
            ax1.grid(True, alpha=0.3)
            ax1.legend()

            # Graphique 2: ROI
            ax2.plot(df['date'], df['roi'], color='green', linewidth=2)
            ax2.axhline(y=0, color='r', linestyle='--')
            ax2.set_title('Return on Investment (ROI)', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Date')
            ax2.set_ylabel('ROI (%)')
            ax2.grid(True, alpha=0.3)

            plt.tight_layout()

            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                print(f"Chart saved to {save_path}")
            else:
                plt.show()

        except ImportError:
            print("matplotlib not available for plotting")
