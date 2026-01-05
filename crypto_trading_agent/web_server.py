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

        simulation_state['total_iterations'] = iterations
        simulation_state['logs'].append(f"Starting simulation with {iterations} iterations")

        for iteration in range(1, iterations + 1):
            if not simulation_state['running']:
                break

            simulation_state['current_iteration'] = iteration
            simulation_state['logs'].append(f"Starting iteration {iteration}/{iterations}")

            # Créer le backtester
            backtester = Backtester(
                start_date=start_date,
                end_date=end_date,
                initial_balance=initial_balance,
                strategy_params=strategy_params,
                delay_per_day=0.0,  # Pas de délai pour l'UI
                use_synthetic_data=True,
                use_twitter_signals=use_twitter
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

            simulation_state['results'] = iteration_results
            simulation_state['logs'].append(
                f"Iteration {iteration} completed: ROI {iteration_results['roi']:+.2f}%"
            )

            # Obtenir les paramètres suggérés pour la prochaine itération
            if iteration < iterations:
                suggested_params = critique.suggest_improvements()
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

    except Exception as e:
        simulation_state['running'] = False
        simulation_state['logs'].append(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
