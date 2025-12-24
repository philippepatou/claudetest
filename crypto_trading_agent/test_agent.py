#!/usr/bin/env python3
"""
Script de test rapide pour vérifier que tous les modules fonctionnent
"""
from datetime import datetime, timedelta
from data_fetcher import CryptoDataFetcher
from portfolio import Portfolio
from trading_strategy import TradingStrategy
from agent import TradingAgent
import pandas as pd


def test_data_fetcher():
    """Test du module de récupération de données"""
    print("Testing Data Fetcher...")
    fetcher = CryptoDataFetcher()

    # Tester sur une courte période
    start = datetime(2024, 12, 24)
    end = datetime(2024, 12, 31)

    print(f"  Fetching data for {start.date()} to {end.date()}...")
    data = fetcher.get_all_top10_data(start, end)

    if data:
        print(f"  ✓ Successfully fetched data for {len(data)} cryptos")
        for symbol in list(data.keys())[:3]:
            print(f"    - {symbol}: {len(data[symbol])} days")
        return True
    else:
        print("  ✗ Failed to fetch data")
        return False


def test_portfolio():
    """Test du module de portefeuille"""
    print("\nTesting Portfolio...")
    portfolio = Portfolio(initial_balance=1000.0)

    # Test d'achat
    success = portfolio.buy('BTC', 100, 50000, datetime.now())
    if success:
        print(f"  ✓ Buy test passed (cash: {portfolio.cash:.2f}€)")
    else:
        print("  ✗ Buy test failed")
        return False

    # Test de vente
    success = portfolio.sell_all('BTC', 51000, datetime.now())
    if success:
        print(f"  ✓ Sell test passed (cash: {portfolio.cash:.2f}€)")
        roi = portfolio.get_roi({})
        print(f"  ✓ ROI calculation: {roi:.2f}%")
        return True
    else:
        print("  ✗ Sell test failed")
        return False


def test_strategy():
    """Test du module de stratégie"""
    print("\nTesting Trading Strategy...")
    strategy = TradingStrategy()

    # Créer des données de test
    dates = pd.date_range(start='2024-12-01', end='2024-12-31', freq='D')
    prices = pd.Series(range(100, 100 + len(dates)), index=dates)

    df = pd.DataFrame({
        'timestamp': dates,
        'price': prices
    })

    # Tester l'analyse
    analysis = strategy.analyze_crypto(df)

    if analysis and 'signal' in analysis:
        print(f"  ✓ Strategy analysis passed")
        print(f"    Signal: {analysis['signal']}, Score: {analysis['score']:.1f}")
        return True
    else:
        print("  ✗ Strategy analysis failed")
        return False


def test_agent():
    """Test de l'agent de trading"""
    print("\nTesting Trading Agent...")

    portfolio = Portfolio(initial_balance=1000.0)
    strategy = TradingStrategy()
    agent = TradingAgent(portfolio, strategy)

    # Créer des données de test simplifiées
    test_data = {}
    dates = pd.date_range(start='2024-12-01', end='2024-12-31', freq='D')

    for symbol in ['BTC', 'ETH', 'SOL']:
        prices = pd.Series(range(100, 100 + len(dates)), index=dates) * (1 if symbol == 'BTC' else 0.5)
        test_data[symbol] = pd.DataFrame({
            'timestamp': dates,
            'price': prices
        })

    # Test d'une décision
    current_prices = {'BTC': 130, 'ETH': 65, 'SOL': 65}
    decision = agent.make_daily_decisions(
        datetime(2024, 12, 31),
        test_data,
        current_prices
    )

    if decision and 'actions' in decision:
        print(f"  ✓ Agent decision test passed")
        print(f"    Actions taken: {len(decision['actions'])}")
        print(f"    Portfolio value: {decision['portfolio_value']:.2f}€")
        return True
    else:
        print("  ✗ Agent decision test failed")
        return False


def main():
    print("="*60)
    print("CRYPTO TRADING AGENT - QUICK TEST")
    print("="*60)

    results = []

    # Test 1: Data Fetcher
    results.append(("Data Fetcher", test_data_fetcher()))

    # Test 2: Portfolio
    results.append(("Portfolio", test_portfolio()))

    # Test 3: Strategy
    results.append(("Strategy", test_strategy()))

    # Test 4: Agent
    results.append(("Agent", test_agent()))

    # Résumé
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:20s}: {status}")
        if not passed:
            all_passed = False

    print("="*60)
    if all_passed:
        print("\n✓ All tests passed! Agent is ready to trade.")
        print("\nYou can now run the full simulation with:")
        print("  python main.py --fast --save-reports")
    else:
        print("\n✗ Some tests failed. Please check the errors above.")

    return all_passed


if __name__ == "__main__":
    main()
