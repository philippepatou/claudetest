"""
Module de gestion de l'historique des itérations
Permet d'analyser les performances passées pour optimiser les paramètres futurs
"""
import json
import os
from datetime import datetime
from typing import Dict, List
import numpy as np


class IterationHistory:
    """Gère l'historique de toutes les itérations et l'optimisation des paramètres"""

    def __init__(self, history_file: str = "iteration_history.json"):
        """
        Initialise le gestionnaire d'historique

        Args:
            history_file: Chemin du fichier d'historique
        """
        self.history_file = history_file
        self.iterations = []
        self.load_history()

    def load_history(self):
        """Charge l'historique depuis le fichier"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.iterations = data.get('iterations', [])
                print(f"Loaded {len(self.iterations)} previous iterations from history")
            except Exception as e:
                print(f"Warning: Could not load history: {e}")
                self.iterations = []
        else:
            print("No previous history found. Starting fresh.")
            self.iterations = []

    def save_history(self):
        """Sauvegarde l'historique dans le fichier"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump({
                    'iterations': self.iterations,
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2, default=str)
            print(f"History saved to {self.history_file}")
        except Exception as e:
            print(f"Error saving history: {e}")

    def add_iteration(self, iteration_data: Dict):
        """
        Ajoute une nouvelle itération à l'historique

        Args:
            iteration_data: Données de l'itération
        """
        # Ajouter un timestamp
        iteration_data['timestamp'] = datetime.now().isoformat()
        iteration_data['iteration_number'] = len(self.iterations) + 1

        self.iterations.append(iteration_data)
        self.save_history()

    def get_best_iteration(self) -> Dict:
        """
        Retourne l'itération avec le meilleur ROI

        Returns:
            Dict de la meilleure itération
        """
        if not self.iterations:
            return None

        return max(self.iterations, key=lambda x: x.get('roi', -1000))

    def get_worst_iteration(self) -> Dict:
        """
        Retourne l'itération avec le pire ROI

        Returns:
            Dict de la pire itération
        """
        if not self.iterations:
            return None

        return min(self.iterations, key=lambda x: x.get('roi', 1000))

    def analyze_parameter_correlation(self, param_name: str) -> Dict:
        """
        Analyse la corrélation entre un paramètre et le ROI

        Args:
            param_name: Nom du paramètre à analyser

        Returns:
            Dict avec les statistiques
        """
        if not self.iterations:
            return {}

        values = []
        rois = []

        for iteration in self.iterations:
            params = iteration.get('parameters', {})
            if param_name in params:
                values.append(params[param_name])
                rois.append(iteration.get('roi', 0))

        if not values:
            return {}

        # Calculer la corrélation (gérer le cas où il n'y a pas de variance)
        if len(values) > 1:
            try:
                correlation = np.corrcoef(values, rois)[0, 1]
                # Remplacer NaN par 0 (cas où stddev = 0)
                if np.isnan(correlation):
                    correlation = 0
            except:
                correlation = 0
        else:
            correlation = 0

        return {
            'param_name': param_name,
            'correlation': correlation,
            'values': values,
            'rois': rois,
            'best_value': values[rois.index(max(rois))] if rois else None,
            'worst_value': values[rois.index(min(rois))] if rois else None
        }

    def get_parameter_insights(self) -> Dict:
        """
        Analyse tous les paramètres pour trouver les corrélations avec le ROI

        Returns:
            Dict avec les insights pour chaque paramètre
        """
        if not self.iterations:
            return {}

        # Récupérer tous les noms de paramètres
        all_param_names = set()
        for iteration in self.iterations:
            params = iteration.get('parameters', {})
            all_param_names.update(params.keys())

        # Analyser chaque paramètre
        insights = {}
        for param_name in all_param_names:
            insights[param_name] = self.analyze_parameter_correlation(param_name)

        return insights

    def suggest_optimal_parameters(self, current_params: Dict) -> Dict:
        """
        Suggère les paramètres optimaux basés sur l'historique

        Args:
            current_params: Paramètres actuels

        Returns:
            Dict avec les paramètres suggérés
        """
        if len(self.iterations) < 3:
            # Pas assez d'historique, utiliser la logique simple
            return self._simple_optimization(current_params)

        # Optimisation basée sur l'analyse complète de l'historique
        best_iteration = self.get_best_iteration()
        insights = self.get_parameter_insights()

        suggested_params = current_params.copy()
        optimization_notes = []

        # Pour chaque paramètre, décider de la meilleure valeur
        for param_name, param_insight in insights.items():
            correlation = param_insight.get('correlation', 0)
            best_value = param_insight.get('best_value')

            if best_value is not None and abs(correlation) > 0.3:
                # Corrélation significative, utiliser la valeur qui a donné le meilleur ROI
                if param_name in suggested_params:
                    # Interpoler entre la valeur actuelle et la meilleure valeur
                    current_value = suggested_params[param_name]
                    # 70% vers la meilleure valeur, 30% actuelle (exploration vs exploitation)
                    suggested_params[param_name] = best_value * 0.7 + current_value * 0.3

                    optimization_notes.append(
                        f"{param_name}: {current_value:.4f} → {suggested_params[param_name]:.4f} "
                        f"(correlation: {correlation:+.2f})"
                    )

        # Si le meilleur ROI était vraiment bon (>30%), se rapprocher de ces paramètres
        if best_iteration and best_iteration.get('roi', 0) > 30:
            best_params = best_iteration.get('parameters', {})
            for param_name, best_value in best_params.items():
                if param_name in suggested_params:
                    current_value = suggested_params[param_name]
                    # Encore plus vers les paramètres de la meilleure itération
                    suggested_params[param_name] = best_value * 0.8 + current_value * 0.2

        return {
            'parameters': suggested_params,
            'notes': optimization_notes,
            'based_on_iterations': len(self.iterations),
            'best_historical_roi': best_iteration.get('roi', 0) if best_iteration else 0
        }

    def _simple_optimization(self, current_params: Dict) -> Dict:
        """
        Optimisation simple quand il n'y a pas assez d'historique

        Args:
            current_params: Paramètres actuels

        Returns:
            Dict avec suggestions simples
        """
        if not self.iterations:
            return {
                'parameters': current_params,
                'notes': ["Première itération, pas d'optimisation"],
                'based_on_iterations': 0,
                'best_historical_roi': 0
            }

        last_iteration = self.iterations[-1]
        last_roi = last_iteration.get('roi', 0)

        suggested_params = current_params.copy()
        notes = []

        # Logique simple basée sur le dernier ROI
        if last_roi < 10:
            # ROI faible, être plus agressif
            suggested_params['risk_per_trade'] = min(0.25, current_params.get('risk_per_trade', 0.15) * 1.2)
            suggested_params['max_allocation_per_coin'] = min(0.35, current_params.get('max_allocation_per_coin', 0.25) * 1.15)
            notes.append("Low ROI: Increasing position sizes")
        elif last_roi > 50:
            # ROI excellent, conserver l'approche
            notes.append("Excellent ROI: Maintaining strategy")
        else:
            # ROI moyen, ajustements légers
            suggested_params['stop_loss'] = max(0.08, current_params.get('stop_loss', 0.10) * 0.95)
            notes.append("Moderate ROI: Fine-tuning parameters")

        return {
            'parameters': suggested_params,
            'notes': notes,
            'based_on_iterations': len(self.iterations),
            'best_historical_roi': max((it.get('roi', 0) for it in self.iterations), default=0)
        }

    def print_summary(self):
        """Affiche un résumé de l'historique"""
        if not self.iterations:
            print("No iteration history available")
            return

        print(f"\n{'='*60}")
        print("ITERATION HISTORY SUMMARY")
        print(f"{'='*60}")
        print(f"Total iterations: {len(self.iterations)}")

        rois = [it.get('roi', 0) for it in self.iterations]
        print(f"Average ROI: {np.mean(rois):.2f}%")
        print(f"Best ROI: {max(rois):.2f}%")
        print(f"Worst ROI: {min(rois):.2f}%")
        print(f"ROI improvement trend: {rois[-1] - rois[0]:.2f}% (first to last)")

        print(f"\nAll iterations:")
        for i, iteration in enumerate(self.iterations, 1):
            roi = iteration.get('roi', 0)
            score = iteration.get('score', 0)
            print(f"  {i}. ROI: {roi:+.2f}% | Score: {score:.1f}/100")

        # Meilleure itération
        best = self.get_best_iteration()
        print(f"\nBest iteration: #{best.get('iteration_number', '?')} with ROI: {best.get('roi', 0):+.2f}%")

        print(f"{'='*60}\n")

    def clear_history(self):
        """Efface tout l'historique"""
        self.iterations = []
        if os.path.exists(self.history_file):
            os.remove(self.history_file)
        print("History cleared")
