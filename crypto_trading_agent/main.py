#!/usr/bin/env python3
"""
Main script pour exécuter l'agent de trading de cryptomonnaies
"""
import argparse
from datetime import datetime
import json
import os
from backtester import Backtester
from autocritique import AutoCritique
from data_fetcher import CryptoDataFetcher
from iteration_history import IterationHistory


def run_iteration(iteration_num: int, strategy_params: dict, args, history: IterationHistory):
    """
    Exécute une itération complète de trading avec autocritique

    Args:
        iteration_num: Numéro de l'itération
        strategy_params: Paramètres de la stratégie
        args: Arguments de la ligne de commande

    Returns:
        Nouveaux paramètres suggérés
    """
    print(f"\n{'#'*60}")
    print(f"{'#'*60}")
    print(f"ITERATION {iteration_num}")
    print(f"{'#'*60}")
    print(f"{'#'*60}\n")

    # Créer le backtester
    backtester = Backtester(
        start_date=args.start_date,
        end_date=args.end_date,
        initial_balance=args.initial_balance,
        strategy_params=strategy_params,
        delay_per_day=args.delay,
        use_synthetic_data=args.synthetic
    )

    # Charger les données
    if not backtester.load_data():
        print("Error: Failed to load data")
        return None

    # Exécuter la simulation
    backtester.run_simulation(verbose=args.verbose)

    # Récupérer les prix finaux
    final_prices = backtester.data_fetcher.get_daily_prices(
        backtester.all_data,
        args.end_date
    )

    # Autocritique avec historique
    critique = AutoCritique(backtester.agent, backtester.all_data, history=history)
    critique.analyze_performance(final_prices)

    # Sauvegarder le rapport
    if args.save_reports:
        report_dir = 'reports'
        os.makedirs(report_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(report_dir, f'iteration_{iteration_num}_{timestamp}.txt')
        critique.generate_report(report_path)

        # Sauvegarder le graphique
        chart_path = os.path.join(report_dir, f'iteration_{iteration_num}_{timestamp}.png')
        backtester.plot_performance(chart_path)

        # Sauvegarder les paramètres
        params_path = os.path.join(report_dir, f'params_{iteration_num}_{timestamp}.json')
        with open(params_path, 'w') as f:
            json.dump(strategy_params, f, indent=2)

    # Obtenir les suggestions pour la prochaine itération
    suggested_params = critique.suggest_improvements()

    # Sauvegarder les résultats de l'itération
    iteration_results = {
        'iteration': iteration_num,
        'roi': critique.analysis_report['roi_analysis']['roi'],
        'score': critique.analysis_report['overall_score'],
        'win_rate': critique.analysis_report['trade_analysis']['win_rate'],
        'num_trades': critique.analysis_report['trade_analysis']['num_trades'],
        'parameters': strategy_params,
        'suggested_parameters': suggested_params
    }

    # Ajouter l'itération à l'historique
    history.add_iteration(iteration_results)

    return iteration_results


def main():
    parser = argparse.ArgumentParser(
        description='Agent de trading de cryptomonnaies avec autocritique'
    )

    parser.add_argument(
        '--start-date',
        type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
        default=datetime(2024, 12, 24),
        help='Date de début (format: YYYY-MM-DD)'
    )

    parser.add_argument(
        '--end-date',
        type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
        default=datetime(2025, 12, 24),
        help='Date de fin (format: YYYY-MM-DD)'
    )

    parser.add_argument(
        '--initial-balance',
        type=float,
        default=1000.0,
        help='Capital initial en EUR (défaut: 1000)'
    )

    parser.add_argument(
        '--delay',
        type=float,
        default=5.0,
        help='Délai en secondes par jour simulé (défaut: 5)'
    )

    parser.add_argument(
        '--iterations',
        type=int,
        default=1,
        help='Nombre d\'itérations avec autocritique (défaut: 1)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Afficher les logs détaillés'
    )

    parser.add_argument(
        '--save-reports',
        action='store_true',
        help='Sauvegarder les rapports et graphiques'
    )

    parser.add_argument(
        '--fast',
        action='store_true',
        help='Mode rapide: 0.1s par jour au lieu de 5s'
    )

    parser.add_argument(
        '--synthetic',
        action='store_true',
        help='Utiliser des données synthétiques au lieu de l\'API CoinGecko'
    )

    parser.add_argument(
        '--reset-history',
        action='store_true',
        help='Réinitialiser l\'historique et repartir de zéro'
    )

    args = parser.parse_args()

    if args.fast:
        args.delay = 0.1

    print("=" * 60)
    print("CRYPTO TRADING AGENT - SANDBOX MODE")
    print("=" * 60)
    print(f"Period: {args.start_date.strftime('%Y-%m-%d')} to {args.end_date.strftime('%Y-%m-%d')}")
    print(f"Initial Balance: {args.initial_balance}€")
    print(f"Iterations: {args.iterations}")
    print(f"Delay per day: {args.delay}s")
    print("=" * 60)

    # Charger ou créer l'historique
    history = IterationHistory(history_file='iteration_history.json')

    # Réinitialiser l'historique si demandé
    if args.reset_history:
        print("\nResetting iteration history...\n")
        history.clear_history()

    # Afficher le résumé de l'historique si disponible
    if len(history.iterations) > 0:
        history.print_summary()

    # Paramètres initiaux de la stratégie
    strategy_params = {
        'rsi_period': 14,
        'rsi_oversold': 30,
        'rsi_overbought': 70,
        'ema_short': 12,
        'ema_long': 26,
        'macd_signal': 9,
        'bb_period': 20,
        'bb_std': 2,
        'momentum_period': 10,
        'min_history': 30,
        'risk_per_trade': 0.15,
        'max_allocation_per_coin': 0.25,
        'stop_loss': 0.10,
        'take_profit': 0.20,
    }

    # Si on a un historique, utiliser les meilleurs paramètres connus
    if len(history.iterations) > 0 and not args.reset_history:
        print("Using optimized parameters based on historical data...")
        optimization = history.suggest_optimal_parameters(strategy_params)
        strategy_params = optimization['parameters']
        print(f"Starting from parameters optimized over {len(history.iterations)} iterations\n")

    all_iterations_results = []

    # Exécuter les itérations
    for iteration in range(1, args.iterations + 1):
        result = run_iteration(iteration, strategy_params, args, history)

        if result:
            all_iterations_results.append(result)

            # Utiliser les paramètres suggérés pour la prochaine itération
            if iteration < args.iterations:
                print(f"\n{'='*60}")
                print(f"Preparing iteration {iteration + 1} with improved parameters...")
                print(f"{'='*60}\n")
                strategy_params = result['suggested_parameters']

                # Demander confirmation si pas en mode automatique
                if args.iterations > 1 and not args.fast:
                    input("Press Enter to continue to next iteration...")

    # Résumé final de toutes les itérations
    if len(all_iterations_results) > 1:
        print(f"\n{'#'*60}")
        print("SUMMARY OF ALL ITERATIONS")
        print(f"{'#'*60}\n")

        for result in all_iterations_results:
            print(f"Iteration {result['iteration']}: "
                  f"ROI={result['roi']:+.2f}% | "
                  f"Score={result['score']:.1f}/100 | "
                  f"Win Rate={result.get('win_rate', 0):.1f}%")

        # Amélioration au fil du temps
        first_roi = all_iterations_results[0]['roi']
        last_roi = all_iterations_results[-1]['roi']
        improvement = last_roi - first_roi
        print(f"\nImprovement: {improvement:+.2f}% (from {first_roi:+.2f}% to {last_roi:+.2f}%)")

        # Meilleure itération
        best_iteration = max(all_iterations_results, key=lambda x: x['roi'])
        print(f"Best Performance: Iteration {best_iteration['iteration']} "
              f"with ROI of {best_iteration['roi']:+.2f}%")

        # Moyenne
        avg_roi = sum(r['roi'] for r in all_iterations_results) / len(all_iterations_results)
        print(f"Average ROI: {avg_roi:+.2f}%")

        # Sauvegarder le résumé
        if args.save_reports:
            summary_path = 'reports/iterations_summary.json'
            with open(summary_path, 'w') as f:
                json.dump(all_iterations_results, f, indent=2, default=str)
            print(f"\nFull summary saved to {summary_path}")

    # Afficher le résumé complet de l'historique
    print(f"\n{'#'*60}")
    print("COMPLETE HISTORY (All Time)")
    print(f"{'#'*60}")
    history.print_summary()

    print(f"\n{'='*60}")
    print("TRADING AGENT COMPLETED")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
