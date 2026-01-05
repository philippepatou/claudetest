// Configuration de l'API
const API_URL = 'http://localhost:5000/api';
let pollInterval = null;

// Chargement initial
document.addEventListener('DOMContentLoaded', () => {
    loadHistory();
});

// Démarrer la simulation
async function startSimulation() {
    const config = getConfig();

    // Désactiver le bouton de démarrage
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    startBtn.disabled = true;
    stopBtn.disabled = false;

    // Afficher la section de progression
    document.getElementById('progress-section').style.display = 'block';
    document.getElementById('results-section').style.display = 'none';

    // Réinitialiser les logs
    document.getElementById('logs').innerHTML = '';

    try {
        const response = await fetch(`${API_URL}/simulation/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });

        if (response.ok) {
            // Démarrer le polling pour suivre la progression
            startPolling();
        } else {
            alert('Erreur lors du démarrage de la simulation');
            startBtn.disabled = false;
            stopBtn.disabled = true;
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Erreur de connexion au serveur');
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }
}

// Arrêter la simulation
async function stopSimulation() {
    try {
        await fetch(`${API_URL}/simulation/stop`, {
            method: 'POST'
        });

        stopPolling();

        document.getElementById('start-btn').disabled = false;
        document.getElementById('stop-btn').disabled = true;
    } catch (error) {
        console.error('Error:', error);
    }
}

// Effacer l'historique
async function clearHistory() {
    if (!confirm('Êtes-vous sûr de vouloir effacer tout l\'historique ?')) {
        return;
    }

    try {
        await fetch(`${API_URL}/history/clear`, {
            method: 'POST'
        });

        loadHistory();
        alert('Historique effacé avec succès');
    } catch (error) {
        console.error('Error:', error);
        alert('Erreur lors de l\'effacement de l\'historique');
    }
}

// Récupérer la configuration du formulaire
function getConfig() {
    return {
        simulation_params: {
            initial_balance: parseFloat(document.getElementById('initial-balance').value),
            iterations: parseInt(document.getElementById('iterations').value),
            start_date: document.getElementById('start-date').value,
            end_date: document.getElementById('end-date').value,
            use_twitter: document.getElementById('use-twitter').checked
        },
        strategy_params: {
            rsi_period: 14,
            rsi_oversold: 30,
            rsi_overbought: 70,
            ema_short: 12,
            ema_long: 26,
            macd_signal: 9,
            bb_period: 20,
            bb_std: 2,
            momentum_period: 10,
            min_history: 30,
            risk_per_trade: parseFloat(document.getElementById('risk-per-trade').value) / 100,
            max_allocation_per_coin: parseFloat(document.getElementById('max-allocation').value) / 100,
            stop_loss: parseFloat(document.getElementById('stop-loss').value) / 100,
            take_profit: parseFloat(document.getElementById('take-profit').value) / 100,
            twitter_weight: parseFloat(document.getElementById('twitter-weight').value) / 100
        }
    };
}

// Démarrer le polling
function startPolling() {
    pollInterval = setInterval(updateStatus, 1000);
}

// Arrêter le polling
function stopPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
}

// Mettre à jour le statut
async function updateStatus() {
    try {
        const response = await fetch(`${API_URL}/simulation/status`);
        const status = await response.json();

        // Mettre à jour la barre de progression
        updateProgress(status);

        // Mettre à jour les logs
        updateLogs(status.logs);

        // Si la simulation est terminée
        if (!status.running && status.progress === 100) {
            stopPolling();
            document.getElementById('start-btn').disabled = false;
            document.getElementById('stop-btn').disabled = true;

            // Afficher les résultats
            if (status.results) {
                displayResults(status.results);
            }

            // Recharger l'historique
            loadHistory();
        }
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

// Mettre à jour la barre de progression
function updateProgress(status) {
    const progress = status.progress || 0;
    document.getElementById('progress-fill').style.width = `${progress}%`;
    document.getElementById('progress-percent').textContent = `${progress}%`;

    if (status.running) {
        document.getElementById('progress-text').textContent =
            `Itération ${status.current_iteration} / ${status.total_iterations} - Jour ${status.current_day} / ${status.total_days}`;
    } else if (progress === 100) {
        document.getElementById('progress-text').textContent = 'Simulation terminée !';
    }

    // Mettre à jour les stats
    document.getElementById('current-iteration').textContent =
        `${status.current_iteration} / ${status.total_iterations}`;
    document.getElementById('current-day').textContent =
        `${status.current_day} / ${status.total_days}`;

    if (status.results) {
        document.getElementById('portfolio-value').textContent =
            `${status.results.final_value?.toFixed(2) || '-'}€`;
        document.getElementById('current-roi').textContent =
            `${status.results.roi >= 0 ? '+' : ''}${status.results.roi?.toFixed(2) || '-'}%`;
    }
}

// Mettre à jour les logs
function updateLogs(logs) {
    const logsContainer = document.getElementById('logs');
    logsContainer.innerHTML = logs.map(log =>
        `<div class="log-entry">▸ ${log}</div>`
    ).join('');
    logsContainer.scrollTop = logsContainer.scrollHeight;
}

// Afficher les résultats
function displayResults(results) {
    document.getElementById('results-section').style.display = 'block';

    document.getElementById('final-roi').textContent =
        `${results.roi >= 0 ? '+' : ''}${results.roi.toFixed(2)}%`;
    document.getElementById('final-value').textContent =
        `${results.final_value.toFixed(2)}€`;
    document.getElementById('profit-loss').textContent =
        `${results.profit_loss >= 0 ? '+' : ''}${results.profit_loss.toFixed(2)}€`;
    document.getElementById('num-trades').textContent = results.num_trades;
    document.getElementById('win-rate').textContent = `${results.win_rate.toFixed(1)}%`;
    document.getElementById('score').textContent = `${results.score.toFixed(1)}/100`;

    // Animer le ROI
    const roiCard = document.getElementById('final-roi').parentElement;
    if (results.roi >= 0) {
        roiCard.classList.add('success');
    } else {
        roiCard.classList.remove('success');
    }
}

// Charger l'historique
async function loadHistory() {
    try {
        const response = await fetch(`${API_URL}/history`);
        const data = await response.json();

        // Mettre à jour le résumé
        document.getElementById('total-iterations').textContent = data.summary.total;
        document.getElementById('avg-roi').textContent =
            `${data.summary.avg_roi >= 0 ? '+' : ''}${data.summary.avg_roi.toFixed(2)}%`;
        document.getElementById('best-roi').textContent =
            `${data.summary.best_roi >= 0 ? '+' : ''}${data.summary.best_roi.toFixed(2)}%`;
        document.getElementById('worst-roi').textContent =
            `${data.summary.worst_roi >= 0 ? '+' : ''}${data.summary.worst_roi.toFixed(2)}%`;

        // Mettre à jour le tableau
        const tbody = document.getElementById('history-tbody');

        if (data.iterations.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="no-data">Aucun historique disponible</td></tr>';
            return;
        }

        tbody.innerHTML = data.iterations.map((iteration, index) => {
            const roiClass = iteration.roi >= 0 ? 'roi-positive' : 'roi-negative';
            const date = iteration.timestamp ? new Date(iteration.timestamp).toLocaleString('fr-FR') : '-';

            return `
                <tr>
                    <td>${data.iterations.length - index}</td>
                    <td>${date}</td>
                    <td class="${roiClass}">${iteration.roi >= 0 ? '+' : ''}${iteration.roi.toFixed(2)}%</td>
                    <td>${iteration.score.toFixed(1)}/100</td>
                    <td>${iteration.win_rate?.toFixed(1) || '-'}%</td>
                    <td>${iteration.num_trades || '-'}</td>
                </tr>
            `;
        }).reverse().join('');
    } catch (error) {
        console.error('Error loading history:', error);
    }
}
