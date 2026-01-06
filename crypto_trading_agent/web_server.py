"""
Serveur web Flask pour l'interface graphique de l'agent de trading
"""
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import threading
import json
import os
from datetime import datetime
from backtester import Backtester
from autocritique import AutoCritique
from iteration_history import IterationHistory
import matplotlib
matplotlib.use('Agg')  # Backend non-GUI
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
CORS(app)

# État global de la simulation
simulation_state = {
    'running': False,
    'progress': 0,
    'current_iteration': 0,
    'total_iterations': 0,
    'current_day': 0,
    'total_days': 0,
    'results': None,
    'logs': []
}

history = IterationHistory(history_file='iteration_history.json')


@app.route('/')
def index():
    """Page principale"""
    return render_template('index.html')


@app.route('/api/config', methods=['GET'])
def get_config():
    """Récupère la configuration actuelle"""
    return jsonify({
        'strategy_params': {
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'ema_short': 12,
            'ema_long': 26,
            'risk_per_trade': 0.15,
            'max_allocation_per_coin': 0.25,
            'stop_loss': 0.10,
            'take_profit': 0.20,
            'twitter_weight': 0.30
        },
        'simulation_params': {
            'initial_balance': 1000,
            'start_date': '2024-12-24',
            'end_date': '2025-12-24',
            'iterations': 1,
            'use_twitter': True,
            'fast_mode': True
        }
    })


@app.route('/api/history', methods=['GET'])
def get_history():
    """Récupère l'historique des itérations"""
    return jsonify({
        'iterations': history.iterations,
        'summary': {
            'total': len(history.iterations),
            'avg_roi': sum(it.get('roi', 0) for it in history.iterations) / len(history.iterations) if history.iterations else 0,
            'best_roi': max((it.get('roi', 0) for it in history.iterations), default=0),
            'worst_roi': min((it.get('roi', 0) for it in history.iterations), default=0)
        }
    })


@app.route('/api/simulation/start', methods=['POST'])
def start_simulation():
    """Démarre une nouvelle simulation"""
    if simulation_state['running']:
        return jsonify({'error': 'Simulation already running'}), 400

    data = request.json

    # Réinitialiser l'état
    simulation_state['running'] = True
    simulation_state['progress'] = 0
    simulation_state['current_iteration'] = 0
    simulation_state['total_iterations'] = data.get('iterations', 1)
    simulation_state['logs'] = []

    # Lancer la simulation dans un thread séparé
    thread = threading.Thread(target=run_simulation, args=(data,))
    thread.daemon = True
    thread.start()

    return jsonify({'status': 'started'})


@app.route('/api/simulation/status', methods=['GET'])
def get_simulation_status():
    """Récupère l'état actuel de la simulation"""
    return jsonify(simulation_state)


@app.route('/api/simulation/stop', methods=['POST'])
def stop_simulation():
    """Arrête la simulation en cours"""
    simulation_state['running'] = False
    return jsonify({'status': 'stopped'})


@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    """Efface l'historique"""
    history.clear_history()
    return jsonify({'status': 'cleared'})


@app.route('/api/best-parameters', methods=['GET'])
def get_best_parameters():
    """Récupère les meilleurs paramètres de tout l'historique"""
    if not history.iterations or len(history.iterations) == 0:
        return jsonify({'parameters': None})

    # Trouver l'itération avec le meilleur ROI
    best_iteration = max(history.iterations, key=lambda x: x.get('roi', float('-inf')))

    return jsonify({
        'parameters': best_iteration.get('parameters', {}),
        'roi': best_iteration.get('roi', 0),
        'score': best_iteration.get('score', 0),
        'iteration': best_iteration.get('iteration', 0)
    })


@app.route('/api/autocritique/latest', methods=['GET'])
def get_latest_autocritique():
    """Récupère le dernier rapport d'autocritique détaillé"""
    if 'last_autocritique' not in simulation_state:
        print("⚠ No autocritique available in simulation_state")
        return jsonify({'error': 'No autocritique available'}), 404

    print(f"✓ Returning autocritique data (iteration {simulation_state['last_autocritique'].get('iteration', '?')})")
    return jsonify(simulation_state['last_autocritique'])


def run_simulation(config):
    """Exécute la simulation avec la configuration donnée"""
    try:
        # Extraire les paramètres
        sim_params = config.get('simulation_params', {})
        strategy_params = config.get('strategy_params', {})

        start_date = datetime.strptime(sim_params.get('start_date', '2024-12-24'), '%Y-%m-%d')
        end_date = datetime.strptime(sim_params.get('end_date', '2025-12-24'), '%Y-%m-%d')
        initial_balance = sim_params.get('initial_balance', 1000)
        iterations = sim_params.get('iterations', 1)
        use_twitter = sim_params.get('use_twitter', True)

        # Générer un identifiant unique pour ce batch de simulations
        import uuid
        batch_id = str(uuid.uuid4())[:8]  # Identifiant court pour ce batch
        simulation_state['current_batch_id'] = batch_id

        simulation_state['total_iterations'] = iterations
        simulation_state['logs'].append(f"Starting simulation batch {batch_id} with {iterations} iterations")

        # Suivre la meilleure itération
        best_iteration = None
        best_roi = float('-inf')
        all_iterations = []

        for iteration in range(1, iterations + 1):
            if not simulation_state['running']:
                break

            simulation_state['current_iteration'] = iteration
            simulation_state['logs'].append(f"Starting iteration {iteration}/{iterations}")

            # Réinitialiser l'historique du portfolio pour cette itération
            simulation_state['portfolio_history'] = []
            simulation_state['current_portfolio_value'] = initial_balance
            simulation_state['current_roi'] = 0

            # Créer le backtester avec variation_seed = numéro d'itération
            # Cela génère des données différentes pour chaque itération
            backtester = Backtester(
                start_date=start_date,
                end_date=end_date,
                initial_balance=initial_balance,
                strategy_params=strategy_params,
                delay_per_day=0.0,  # Pas de délai pour l'UI
                use_synthetic_data=True,
                use_twitter_signals=use_twitter,
                variation_seed=iteration  # Chaque itération a des données de marché différentes
            )

            # Charger les données
            backtester.load_data()

            # Calculer le nombre total de jours
            total_days = (end_date - start_date).days + 1
            simulation_state['total_days'] = total_days

            # Simuler jour par jour
            current_date = start_date
            day_num = 0

            from datetime import timedelta
            while current_date <= end_date:
                if not simulation_state['running']:
                    break

                day_num += 1
                simulation_state['current_day'] = day_num
                simulation_state['progress'] = int((day_num / total_days) * 100)

                # Obtenir les prix du jour
                current_prices = backtester.data_fetcher.get_daily_prices(
                    backtester.all_data, current_date
                )

                if current_prices:
                    # Créer des sous-ensembles de données jusqu'à la date actuelle
                    historical_data = {}
                    for symbol, df in backtester.all_data.items():
                        historical_data[symbol] = df[df['timestamp'] <= current_date].copy()

                    # L'agent prend ses décisions
                    backtester.agent.make_daily_decisions(
                        current_date, historical_data, current_prices
                    )

                    # Calculer la valeur actuelle du portfolio
                    current_portfolio_value = backtester.agent.portfolio.get_total_value(current_prices)

                    # Calculer le ROI actuel
                    current_roi = ((current_portfolio_value - initial_balance) / initial_balance) * 100

                    # Mettre à jour l'état en temps réel
                    simulation_state['current_portfolio_value'] = current_portfolio_value
                    simulation_state['current_roi'] = current_roi
                    simulation_state['portfolio_history'].append({
                        'day': day_num,
                        'value': current_portfolio_value,
                        'roi': current_roi
                    })

                current_date += timedelta(days=1)

            # Récupérer les prix finaux
            final_prices = backtester.data_fetcher.get_daily_prices(
                backtester.all_data, end_date
            )

            # Autocritique
            critique = AutoCritique(backtester.agent, backtester.all_data, history=history)
            critique.analyze_performance(final_prices)

            # Obtenir les métriques
            metrics = backtester.agent.get_performance_summary(final_prices)

            # Obtenir les paramètres suggérés par l'autocritique
            suggested_params = critique.suggest_improvements()

            # Sauvegarder le rapport d'autocritique complet pour l'API
            try:
                simulation_state['last_autocritique'] = {
                    'iteration': iteration,
                    'roi_analysis': critique.analysis_report.get('roi_analysis', {}),
                    'trade_analysis': critique.analysis_report.get('trade_analysis', {}),
                    'error_analysis': critique.analysis_report.get('error_analysis', {}),
                    'allocation_analysis': critique.analysis_report.get('allocation_analysis', {}),
                    'indicator_analysis': critique.analysis_report.get('indicator_analysis', {}),
                    'transaction_analysis': critique.analysis_report.get('transaction_analysis', {}),
                    'market_anticipation_analysis': critique.analysis_report.get('market_anticipation_analysis', {}),
                    'influencer_impact_analysis': critique.analysis_report.get('influencer_impact_analysis', {}),
                    'historical_comparison': critique.analysis_report.get('historical_comparison', {}),
                    'overall_score': critique.analysis_report.get('overall_score', 0),
                    'suggested_parameters': suggested_params  # NOUVEAU
                }
                print(f"✓ Autocritique saved successfully for iteration {iteration}")
            except Exception as e:
                print(f"✗ Error saving autocritique: {e}")
                import traceback
                traceback.print_exc()

            # Sauvegarder dans l'historique
            iteration_results = {
                'iteration': iteration,
                'roi': critique.analysis_report['roi_analysis']['roi'],
                'score': critique.analysis_report['overall_score'],
                'win_rate': critique.analysis_report['trade_analysis']['win_rate'],
                'num_trades': critique.analysis_report['trade_analysis']['num_trades'],
                'parameters': strategy_params,
                'final_value': metrics['final_value'],
                'profit_loss': metrics['profit_loss']
            }

            history.add_iteration(iteration_results)

            # Suivre les itérations et la meilleure
            all_iterations.append(iteration_results)
            if iteration_results['roi'] > best_roi:
                best_roi = iteration_results['roi']
                best_iteration = iteration_results.copy()

            simulation_state['results'] = iteration_results
            simulation_state['logs'].append(
                f"Iteration {iteration} completed: ROI {iteration_results['roi']:+.2f}%"
            )

            # Utiliser les paramètres suggérés pour la prochaine itération
            if iteration < iterations:
                strategy_params = suggested_params

                # Convertir les paramètres qui doivent être des entiers
                int_params = ['rsi_period', 'ema_short', 'ema_long', 'macd_signal',
                              'bb_period', 'momentum_period', 'min_history']
                for param in int_params:
                    if param in strategy_params:
                        strategy_params[param] = int(round(strategy_params[param]))

        simulation_state['running'] = False
        simulation_state['progress'] = 100
        simulation_state['logs'].append("Simulation completed!")

        # Obtenir le classement des influenceurs Twitter (utiliser le dernier backtester)
        twitter_rankings = []
        suggested_weights = {}
        if use_twitter and 'backtester' in locals():
            twitter_rankings = backtester.agent.get_influencer_rankings()
            suggested_weights = backtester.agent.get_suggested_twitter_weights()

        # Afficher le résumé de la meilleure itération
        if best_iteration:
            simulation_state['logs'].append("")
            simulation_state['logs'].append("=" * 60)
            simulation_state['logs'].append("🏆 MEILLEURE ITÉRATION")
            simulation_state['logs'].append("=" * 60)
            simulation_state['logs'].append(f"Itération: {best_iteration['iteration']}/{iterations}")
            simulation_state['logs'].append(f"ROI: {best_iteration['roi']:+.2f}%")
            simulation_state['logs'].append(f"Score: {best_iteration['score']:.2f}/100")
            simulation_state['logs'].append(f"Taux de réussite: {best_iteration['win_rate']:.1f}%")
            simulation_state['logs'].append(f"Nombre de trades: {best_iteration['num_trades']}")
            simulation_state['logs'].append(f"Valeur finale: {best_iteration['final_value']:.2f}€")
            simulation_state['logs'].append(f"Profit/Perte: {best_iteration['profit_loss']:+.2f}€")
            simulation_state['logs'].append("")
            simulation_state['logs'].append("📊 PARAMÈTRES OPTIMAUX:")
            params = best_iteration['parameters']
            simulation_state['logs'].append(f"  • RSI Period: {params.get('rsi_period', 'N/A')}")
            simulation_state['logs'].append(f"  • RSI Oversold: {params.get('rsi_oversold', 'N/A')}")
            simulation_state['logs'].append(f"  • RSI Overbought: {params.get('rsi_overbought', 'N/A')}")
            simulation_state['logs'].append(f"  • EMA Short: {params.get('ema_short', 'N/A')}")
            simulation_state['logs'].append(f"  • EMA Long: {params.get('ema_long', 'N/A')}")
            simulation_state['logs'].append(f"  • Risk per Trade: {params.get('risk_per_trade', 'N/A'):.2%}")
            simulation_state['logs'].append(f"  • Max Allocation: {params.get('max_allocation_per_coin', 'N/A'):.2%}")
            simulation_state['logs'].append(f"  • Stop Loss: {params.get('stop_loss', 'N/A'):.2%}")
            simulation_state['logs'].append(f"  • Take Profit: {params.get('take_profit', 'N/A'):.2%}")
            simulation_state['logs'].append(f"  • Twitter Weight: {params.get('twitter_weight', 'N/A'):.2%}")
            simulation_state['logs'].append("=" * 60)

        # Afficher le classement des influenceurs Twitter
        if twitter_rankings:
            simulation_state['logs'].append("")
            simulation_state['logs'].append("=" * 60)
            simulation_state['logs'].append("🐦 CLASSEMENT DES INFLUENCEURS TWITTER")
            simulation_state['logs'].append("=" * 60)

            for i, rank in enumerate(twitter_rankings[:10], 1):  # Top 10
                simulation_state['logs'].append(
                    f"{i}. {rank['influencer']} - "
                    f"Win Rate: {rank['win_rate']:.1f}% | "
                    f"Trades: {rank['total_trades']} | "
                    f"PNL Moyen: {rank['avg_pnl']:+.2f}% | "
                    f"Score: {rank['reliability_score']:.1f}"
                )

            simulation_state['logs'].append("")
            simulation_state['logs'].append("💡 POIDS SUGGÉRÉS (basés sur la performance):")
            for influencer, weight in sorted(suggested_weights.items(), key=lambda x: x[1], reverse=True)[:10]:
                simulation_state['logs'].append(f"  • {influencer}: {weight}")
            simulation_state['logs'].append("=" * 60)

        # Ajouter le résumé aux résultats (sans référence circulaire)
        if best_iteration:
            simulation_state['best_iteration'] = {
                'iteration': best_iteration['iteration'],
                'roi': best_iteration['roi'],
                'score': best_iteration['score'],
                'win_rate': best_iteration['win_rate'],
                'num_trades': best_iteration['num_trades'],
                'final_value': best_iteration['final_value'],
                'profit_loss': best_iteration['profit_loss'],
                'parameters': best_iteration['parameters'].copy()
            }

        simulation_state['all_iterations_summary'] = [
            {
                'iteration': it['iteration'],
                'roi': it['roi'],
                'score': it['score']
            }
            for it in all_iterations
        ]

        # Ajouter les classements Twitter
        if twitter_rankings:
            simulation_state['twitter_rankings'] = twitter_rankings[:10]  # Top 10
            simulation_state['suggested_twitter_weights'] = suggested_weights

    except Exception as e:
        simulation_state['running'] = False
        simulation_state['logs'].append(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
