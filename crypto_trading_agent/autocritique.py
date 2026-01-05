"""
Module d'autocritique et d'optimisation pour l'agent de trading
Analyse les performances et suggère des améliorations
"""
from typing import Dict, List
import pandas as pd
import numpy as np
from agent import TradingAgent
from iteration_history import IterationHistory


class AutoCritique:
    """Système d'autocritique pour analyser et améliorer la stratégie"""

    def __init__(self, agent: TradingAgent, all_data: Dict[str, pd.DataFrame],
                 history: IterationHistory = None):
        """
        Initialise le système d'autocritique

        Args:
            agent: Instance de l'agent de trading
            all_data: Données historiques complètes
            history: Historique des itérations précédentes
        """
        self.agent = agent
        self.all_data = all_data
        self.history = history
        self.analysis_report = {}

    def analyze_performance(self, final_prices: Dict[str, float]) -> Dict:
        """
        Analyse complète des performances

        Args:
            final_prices: Prix finaux

        Returns:
            Dict avec l'analyse complète
        """
        print(f"\n{'='*60}")
        print("AUTOCRITIQUE - PERFORMANCE ANALYSIS")
        print(f"{'='*60}\n")

        metrics = self.agent.get_performance_summary(final_prices)
        mistakes = self.agent.analyze_mistakes(self.all_data)

        # 1. Analyse du ROI
        roi_analysis = self._analyze_roi(metrics)

        # 2. Analyse des trades
        trade_analysis = self._analyze_trades(metrics)

        # 3. Analyse des erreurs
        error_analysis = self._analyze_errors(mistakes)

        # 4. Analyse de l'allocation
        allocation_analysis = self._analyze_allocation(final_prices)

        # 5. Analyse des indicateurs
        indicator_analysis = self._analyze_indicator_effectiveness()

        self.analysis_report = {
            'roi_analysis': roi_analysis,
            'trade_analysis': trade_analysis,
            'error_analysis': error_analysis,
            'allocation_analysis': allocation_analysis,
            'indicator_analysis': indicator_analysis,
            'overall_score': self._calculate_overall_score(metrics)
        }

        self._print_analysis()

        return self.analysis_report

    def _analyze_roi(self, metrics: Dict) -> Dict:
        """Analyse le ROI"""
        roi = metrics['roi']

        analysis = {
            'roi': roi,
            'target_roi': 20.0,  # Objectif: 20% ROI minimum
            'performance': 'excellent' if roi > 50 else
                          'good' if roi > 20 else
                          'acceptable' if roi > 0 else
                          'poor',
            'weakness': []
        }

        if roi < 20:
            analysis['weakness'].append(
                f"ROI ({roi:.1f}%) below target (20%). Need more aggressive strategy."
            )
        if roi < 0:
            analysis['weakness'].append(
                "Negative ROI - strategy is losing money. Major revision needed."
            )

        return analysis

    def _analyze_trades(self, metrics: Dict) -> Dict:
        """Analyse l'activité de trading"""
        analysis = {
            'num_trades': metrics.get('num_trades', 0),
            'win_rate': metrics.get('win_rate', 0),
            'winning_trades': metrics.get('winning_trades', 0),
            'losing_trades': metrics.get('losing_trades', 0),
            'weakness': []
        }

        # Vérifier le taux de réussite
        if analysis['win_rate'] < 50:
            analysis['weakness'].append(
                f"Win rate ({analysis['win_rate']:.1f}%) is below 50%. "
                "Need better entry/exit timing."
            )

        # Vérifier le nombre de trades
        if analysis['num_trades'] < 10:
            analysis['weakness'].append(
                f"Only {analysis['num_trades']} trades executed. "
                "Strategy may be too conservative."
            )
        elif analysis['num_trades'] > 200:
            analysis['weakness'].append(
                f"{analysis['num_trades']} trades executed. "
                "Strategy may be overtrading (high fees)."
            )

        return analysis

    def _analyze_errors(self, mistakes: List[Dict]) -> Dict:
        """Analyse les erreurs de trading"""
        losing_trades = [m for m in mistakes if m['type'] == 'losing_trade']
        missed_opportunities = [m for m in mistakes if m['type'] == 'missed_opportunity']

        analysis = {
            'total_mistakes': len(mistakes),
            'losing_trades': len(losing_trades),
            'missed_opportunities': len(missed_opportunities),
            'weakness': [],
            'top_mistakes': []
        }

        # Analyser les pertes les plus importantes
        if losing_trades:
            losing_trades.sort(key=lambda x: x['pnl_pct'])
            worst_trades = losing_trades[:3]

            for trade in worst_trades:
                analysis['top_mistakes'].append({
                    'type': 'bad_trade',
                    'symbol': trade['symbol'],
                    'loss': trade['pnl_pct'],
                    'recommendation': 'Improve stop-loss timing or entry criteria'
                })

            avg_loss = np.mean([t['pnl_pct'] for t in losing_trades])
            analysis['weakness'].append(
                f"{len(losing_trades)} losing trades with average loss of {avg_loss:.1f}%"
            )

        # Analyser les opportunités manquées
        if missed_opportunities:
            missed_opportunities.sort(key=lambda x: x['potential_gain'], reverse=True)
            top_missed = missed_opportunities[:3]

            for opp in top_missed:
                analysis['top_mistakes'].append({
                    'type': 'missed_opportunity',
                    'symbol': opp['symbol'],
                    'potential_gain': opp['potential_gain'],
                    'recommendation': f"Be more aggressive on {opp['symbol']}"
                })

            analysis['weakness'].append(
                f"Missed {len(missed_opportunities)} high-growth opportunities"
            )

        return analysis

    def _analyze_allocation(self, final_prices: Dict[str, float]) -> Dict:
        """Analyse l'allocation du portefeuille"""
        allocation = self.agent.portfolio.get_allocation(final_prices)

        analysis = {
            'cash_percentage': allocation.get('CASH', 0),
            'diversification': len([k for k in allocation.keys() if k != 'CASH']),
            'weakness': []
        }

        # Trop de cash?
        if analysis['cash_percentage'] > 50:
            analysis['weakness'].append(
                f"Cash allocation too high ({analysis['cash_percentage']:.1f}%). "
                "Capital is underutilized."
            )

        # Pas assez diversifié?
        if analysis['diversification'] < 3:
            analysis['weakness'].append(
                f"Only {analysis['diversification']} positions. "
                "Insufficient diversification increases risk."
            )

        # Trop diversifié?
        if analysis['diversification'] > 7:
            analysis['weakness'].append(
                f"{analysis['diversification']} positions may be over-diversified. "
                "Focus on top opportunities."
            )

        return analysis

    def _analyze_indicator_effectiveness(self) -> Dict:
        """Analyse l'efficacité des indicateurs techniques"""
        # Compter combien de fois chaque raison apparaît dans les décisions
        buy_reasons = {}
        sell_reasons = {}

        for decision in self.agent.decisions_log:
            for action in decision['actions']:
                if action['action'] == 'BUY' and 'reasons' in action:
                    for reason in action['reasons']:
                        buy_reasons[reason] = buy_reasons.get(reason, 0) + 1
                elif action['action'] == 'SELL' and 'reason' in action:
                    reason = action['reason']
                    sell_reasons[reason] = sell_reasons.get(reason, 0) + 1

        analysis = {
            'most_common_buy_signals': sorted(buy_reasons.items(),
                                             key=lambda x: x[1], reverse=True)[:5],
            'most_common_sell_triggers': sorted(sell_reasons.items(),
                                               key=lambda x: x[1], reverse=True)[:5],
            'weakness': []
        }

        return analysis

    def _calculate_overall_score(self, metrics: Dict) -> float:
        """
        Calcule un score global de performance (0-100)

        Args:
            metrics: Métriques de performance

        Returns:
            Score de 0 à 100
        """
        score = 50  # Score de base

        # ROI (max 30 points)
        roi = metrics['roi']
        if roi > 0:
            score += min(roi / 2, 30)  # +1 point par 2% de ROI, max 30
        else:
            score += roi / 2  # Pénalité pour ROI négatif

        # Win rate (max 20 points)
        win_rate = metrics.get('win_rate', 0)
        score += (win_rate / 100) * 20

        # Pénalités
        if metrics.get('num_trades', 0) < 5:
            score -= 10  # Trop peu actif
        if metrics.get('total_fees', 0) > metrics['initial_balance'] * 0.1:
            score -= 10  # Trop de frais

        return max(0, min(100, score))

    def _print_analysis(self):
        """Affiche l'analyse détaillée"""
        report = self.analysis_report

        print(f"Overall Score: {report['overall_score']:.1f}/100")
        print(f"Performance Rating: {report['roi_analysis']['performance'].upper()}\n")

        print("=" * 60)
        print("WEAKNESSES IDENTIFIED:")
        print("=" * 60)

        all_weaknesses = []
        all_weaknesses.extend(report['roi_analysis']['weakness'])
        all_weaknesses.extend(report['trade_analysis']['weakness'])
        all_weaknesses.extend(report['error_analysis']['weakness'])
        all_weaknesses.extend(report['allocation_analysis']['weakness'])

        if all_weaknesses:
            for i, weakness in enumerate(all_weaknesses, 1):
                print(f"{i}. {weakness}")
        else:
            print("No major weaknesses identified!")

        if report['error_analysis']['top_mistakes']:
            print(f"\n{'='*60}")
            print("TOP MISTAKES:")
            print(f"{'='*60}")
            for i, mistake in enumerate(report['error_analysis']['top_mistakes'], 1):
                print(f"{i}. {mistake['type']}: {mistake['symbol']}")
                if 'loss' in mistake:
                    print(f"   Loss: {mistake['loss']:.1f}%")
                if 'potential_gain' in mistake:
                    print(f"   Potential gain: {mistake['potential_gain']:.1f}%")
                print(f"   → {mistake['recommendation']}")

    def suggest_improvements(self) -> Dict:
        """
        Suggère des améliorations des paramètres de stratégie basées sur l'historique complet

        Returns:
            Dict avec les nouveaux paramètres suggérés
        """
        print(f"\n{'='*60}")
        print("SUGGESTED IMPROVEMENTS FOR NEXT ITERATION")
        print(f"{'='*60}\n")

        current_params = self.agent.get_strategy_parameters()

        # Si on a un historique, utiliser l'optimisation avancée
        if self.history and len(self.history.iterations) > 0:
            return self._suggest_with_history(current_params)
        else:
            return self._suggest_without_history(current_params)

    def _suggest_with_history(self, current_params: Dict) -> Dict:
        """
        Suggère des paramètres basés sur l'analyse complète de l'historique

        Args:
            current_params: Paramètres actuels

        Returns:
            Dict avec paramètres optimisés
        """
        print(f"Analyzing {len(self.history.iterations)} previous iterations...\n")

        # Afficher le résumé de l'historique
        if len(self.history.iterations) >= 2:
            print("Historical performance:")
            for i, it in enumerate(self.history.iterations[-5:], 1):  # 5 dernières
                idx = len(self.history.iterations) - 5 + i
                if idx > 0:
                    print(f"  Iteration {idx}: ROI {it.get('roi', 0):+.2f}% | "
                          f"Score {it.get('score', 0):.1f}/100")
            print()

        # Utiliser l'optimisation basée sur l'historique
        optimization_result = self.history.suggest_optimal_parameters(current_params)

        suggested_params = optimization_result['parameters']
        notes = optimization_result['notes']
        best_historical_roi = optimization_result['best_historical_roi']

        print(f"Best historical ROI: {best_historical_roi:+.2f}%")
        print(f"Current iteration ROI: {self.analysis_report['roi_analysis']['roi']:+.2f}%")
        print()

        # Afficher les insights sur les paramètres
        insights = self.history.get_parameter_insights()
        high_correlation_params = [
            (name, data['correlation'])
            for name, data in insights.items()
            if abs(data.get('correlation', 0)) > 0.4
        ]

        if high_correlation_params:
            print("Parameters with strong correlation to ROI:")
            for param_name, correlation in sorted(high_correlation_params,
                                                  key=lambda x: abs(x[1]),
                                                  reverse=True)[:5]:
                direction = "positive" if correlation > 0 else "negative"
                print(f"  {param_name}: {correlation:+.2f} ({direction})")
            print()

        print("Recommended parameter adjustments:")
        if notes:
            for i, note in enumerate(notes, 1):
                print(f"{i}. {note}")
        else:
            print("1. Maintaining current parameters (performing well)")

        # Ajouter des suggestions contextuelles basées sur l'analyse actuelle
        roi = self.analysis_report['roi_analysis']['roi']
        win_rate = self.analysis_report['trade_analysis']['win_rate']

        additional_suggestions = []

        # Comparer avec le meilleur historique
        if roi < best_historical_roi * 0.8:
            additional_suggestions.append(
                f"Current ROI is {((roi/best_historical_roi - 1) * 100):.1f}% "
                f"below best historical. Moving toward best parameters."
            )

        # Win rate analysis
        if win_rate < 45:
            suggested_params['stop_loss'] = max(0.07, suggested_params.get('stop_loss', 0.10) * 0.9)
            suggested_params['take_profit'] = min(0.30, suggested_params.get('take_profit', 0.20) * 1.1)
            additional_suggestions.append(
                f"Adjusting stop-loss/take-profit for better win rate "
                f"(SL: {suggested_params['stop_loss']:.1%}, TP: {suggested_params['take_profit']:.1%})"
            )

        if additional_suggestions:
            print("\nAdditional context-based adjustments:")
            for i, suggestion in enumerate(additional_suggestions, len(notes) + 1):
                print(f"{i}. {suggestion}")

        print(f"\n{'='*60}\n")

        return suggested_params

    def _suggest_without_history(self, current_params: Dict) -> Dict:
        """
        Suggère des paramètres sans historique (première itération ou historique vide)

        Args:
            current_params: Paramètres actuels

        Returns:
            Dict avec paramètres suggérés
        """
        print("First iteration - using rule-based optimization\n")

        suggested_params = current_params.copy()

        roi = self.analysis_report['roi_analysis']['roi']
        win_rate = self.analysis_report['trade_analysis']['win_rate']
        cash_pct = self.analysis_report['allocation_analysis']['cash_percentage']

        improvements = []

        # Si ROI faible, être plus agressif
        if roi < 10:
            suggested_params['risk_per_trade'] = min(0.25, current_params['risk_per_trade'] * 1.3)
            suggested_params['max_allocation_per_coin'] = min(0.35,
                                                              current_params['max_allocation_per_coin'] * 1.2)
            improvements.append(
                f"Increase position sizes (risk_per_trade: {suggested_params['risk_per_trade']:.2f})"
            )

        # Si trop de cash, ajuster les seuils
        if cash_pct > 50:
            suggested_params['rsi_oversold'] = min(35, current_params['rsi_oversold'] + 5)
            suggested_params['rsi_overbought'] = max(65, current_params['rsi_overbought'] - 5)
            improvements.append(
                f"Adjust RSI thresholds to find more opportunities "
                f"(oversold: {suggested_params['rsi_oversold']}, "
                f"overbought: {suggested_params['rsi_overbought']})"
            )

        # Si mauvais win rate, ajuster stops et targets
        if win_rate < 40:
            suggested_params['stop_loss'] = max(0.05, current_params['stop_loss'] - 0.02)
            suggested_params['take_profit'] = min(0.30, current_params['take_profit'] + 0.05)
            improvements.append(
                f"Tighter stop-loss ({suggested_params['stop_loss']:.2%}) "
                f"and higher take-profit ({suggested_params['take_profit']:.2%})"
            )

        # Ajuster les périodes des indicateurs basé sur la volatilité
        if self.analysis_report['trade_analysis']['num_trades'] < 20:
            suggested_params['rsi_period'] = max(10, current_params['rsi_period'] - 2)
            suggested_params['ema_short'] = max(8, current_params['ema_short'] - 2)
            improvements.append(
                f"Shorter indicator periods for more signals "
                f"(RSI period: {suggested_params['rsi_period']})"
            )

        print("Recommended parameter adjustments:")
        for i, improvement in enumerate(improvements, 1):
            print(f"{i}. {improvement}")

        if not improvements:
            print("Strategy is performing well. Minor fine-tuning suggested:")
            print("1. Continue monitoring and adjust based on market conditions")

        print(f"\n{'='*60}\n")

        return suggested_params

    def generate_report(self, save_path: str = None) -> str:
        """
        Génère un rapport textuel complet

        Args:
            save_path: Chemin pour sauvegarder le rapport

        Returns:
            Contenu du rapport
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("AUTOCRITIQUE REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"\nOverall Score: {self.analysis_report['overall_score']:.1f}/100")
        report_lines.append(f"Performance: {self.analysis_report['roi_analysis']['performance']}")
        report_lines.append(f"ROI: {self.analysis_report['roi_analysis']['roi']:.2f}%")
        report_lines.append(f"Win Rate: {self.analysis_report['trade_analysis']['win_rate']:.1f}%")

        report_lines.append("\nWEAKNESSES:")
        all_weaknesses = (
            self.analysis_report['roi_analysis']['weakness'] +
            self.analysis_report['trade_analysis']['weakness'] +
            self.analysis_report['error_analysis']['weakness'] +
            self.analysis_report['allocation_analysis']['weakness']
        )
        for weakness in all_weaknesses:
            report_lines.append(f"- {weakness}")

        report = "\n".join(report_lines)

        if save_path:
            with open(save_path, 'w') as f:
                f.write(report)
            print(f"Report saved to {save_path}")

        return report
