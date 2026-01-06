// Configuration de l'API
const API_URL = 'http://localhost:5000/api';
let pollInterval = null;

// Chargement initial
document.addEventListener('DOMContentLoaded', () => {
    loadHistory();
    loadBestParametersFromHistory();
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
            rsi_period: parseInt(document.getElementById('rsi-period').value),
            rsi_oversold: parseInt(document.getElementById('rsi-oversold').value),
            rsi_overbought: parseInt(document.getElementById('rsi-overbought').value),
            ema_short: parseInt(document.getElementById('ema-short').value),
            ema_long: parseInt(document.getElementById('ema-long').value),
            macd_signal: parseInt(document.getElementById('macd-signal').value),
            bb_period: parseInt(document.getElementById('bb-period').value),
            bb_std: parseFloat(document.getElementById('bb-std').value),
            momentum_period: parseInt(document.getElementById('momentum-period').value),
            min_history: parseInt(document.getElementById('min-history').value),
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

            // Afficher les meilleurs paramètres si disponibles
            if (status.best_iteration) {
                displayBestParameters(status.best_iteration);
                displayBestParametersInline(status.best_iteration);
            }

            // Afficher le classement Twitter si disponible
            if (status.twitter_rankings) {
                displayTwitterRankings(status.twitter_rankings, status.suggested_twitter_weights);
            }

            // Charger et afficher l'autocritique (NOUVEAU)
            loadAutocritique();

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

// Afficher les meilleurs paramètres
function displayBestParameters(bestIteration) {
    const section = document.getElementById('best-params-section');
    section.style.display = 'block';

    // Mettre à jour l'en-tête
    document.getElementById('best-iteration-num').textContent =
        `${bestIteration.iteration}`;
    document.getElementById('best-iteration-roi').textContent =
        `${bestIteration.roi >= 0 ? '+' : ''}${bestIteration.roi.toFixed(2)}%`;
    document.getElementById('best-iteration-score').textContent =
        `${bestIteration.score.toFixed(1)}/100`;

    // Construire la grille de paramètres
    const params = bestIteration.parameters;
    const paramsGrid = document.getElementById('best-params-grid');

    const paramsList = [
        { name: 'RSI Period', value: params.rsi_period },
        { name: 'RSI Oversold', value: params.rsi_oversold },
        { name: 'RSI Overbought', value: params.rsi_overbought },
        { name: 'EMA Short', value: params.ema_short },
        { name: 'EMA Long', value: params.ema_long },
        { name: 'Risk per Trade', value: `${(params.risk_per_trade * 100).toFixed(1)}%` },
        { name: 'Max Allocation', value: `${(params.max_allocation_per_coin * 100).toFixed(1)}%` },
        { name: 'Stop Loss', value: `${(params.stop_loss * 100).toFixed(1)}%` },
        { name: 'Take Profit', value: `${(params.take_profit * 100).toFixed(1)}%` },
        { name: 'Twitter Weight', value: `${(params.twitter_weight * 100).toFixed(1)}%` }
    ];

    paramsGrid.innerHTML = paramsList.map(param => `
        <div class="param-item">
            <span class="param-name">${param.name}</span>
            <span class="param-value">${param.value}</span>
        </div>
    `).join('');
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

// Variable globale pour stocker les meilleurs paramètres
let currentBestParameters = null;

// Afficher les meilleurs paramètres inline (près de la config)
function displayBestParametersInline(bestIteration) {
    const section = document.getElementById('best-params-inline');
    section.style.display = 'block';

    // Stocker les paramètres pour l'application ultérieure
    currentBestParameters = bestIteration.parameters;

    // Mettre à jour l'en-tête
    document.getElementById('best-iter-num-inline').textContent = bestIteration.iteration;
    document.getElementById('best-roi-inline').textContent =
        `${bestIteration.roi >= 0 ? '+' : ''}${bestIteration.roi.toFixed(2)}%`;
    document.getElementById('best-score-inline').textContent =
        `${bestIteration.score.toFixed(1)}/100`;

    // Construire la grille compacte de paramètres avec TOUS les paramètres
    const params = bestIteration.parameters;
    const paramsGrid = document.getElementById('best-params-inline-grid');

    const paramsList = [
        { name: 'RSI Period', value: params.rsi_period || '-' },
        { name: 'RSI Oversold', value: params.rsi_oversold || '-' },
        { name: 'RSI Overbought', value: params.rsi_overbought || '-' },
        { name: 'EMA Short', value: params.ema_short || '-' },
        { name: 'EMA Long', value: params.ema_long || '-' },
        { name: 'MACD Signal', value: params.macd_signal || '-' },
        { name: 'BB Period', value: params.bb_period || '-' },
        { name: 'BB Std', value: params.bb_std || '-' },
        { name: 'Momentum', value: params.momentum_period || '-' },
        { name: 'Min History', value: params.min_history || '-' },
        { name: 'Risk/Trade', value: `${(params.risk_per_trade * 100).toFixed(0)}%` },
        { name: 'Max Alloc', value: `${(params.max_allocation_per_coin * 100).toFixed(0)}%` },
        { name: 'Stop Loss', value: `${(params.stop_loss * 100).toFixed(0)}%` },
        { name: 'Take Profit', value: `${(params.take_profit * 100).toFixed(0)}%` },
        { name: 'Twitter Weight', value: `${(params.twitter_weight * 100).toFixed(0)}%` }
    ];

    paramsGrid.innerHTML = paramsList.map(param => `
        <div class="param-compact-item">
            <div class="param-compact-name">${param.name}</div>
            <div class="param-compact-value">${param.value}</div>
        </div>
    `).join('');
}

// Charger les meilleurs paramètres de l'historique complet au démarrage
async function loadBestParametersFromHistory() {
    try {
        const response = await fetch(`${API_URL}/best-parameters`);
        if (!response.ok) return;

        const data = await response.json();

        if (data.parameters) {
            console.log('Loading best parameters from history:', data);
            updateAllParameters(data.parameters);

            // Afficher un message discret
            if (data.roi !== undefined) {
                console.log(`Using best parameters from history (ROI: ${data.roi.toFixed(2)}%)`);
            }
        }
    } catch (error) {
        console.error('Error loading best parameters:', error);
        // Silencieux - utilise les valeurs par défaut
    }
}

// Mettre à jour tous les champs de paramètres avec de nouvelles valeurs
function updateAllParameters(params) {
    // Indicateurs techniques
    if (params.rsi_period !== undefined) {
        document.getElementById('rsi-period').value = params.rsi_period;
    }
    if (params.rsi_oversold !== undefined) {
        document.getElementById('rsi-oversold').value = params.rsi_oversold;
    }
    if (params.rsi_overbought !== undefined) {
        document.getElementById('rsi-overbought').value = params.rsi_overbought;
    }
    if (params.ema_short !== undefined) {
        document.getElementById('ema-short').value = params.ema_short;
    }
    if (params.ema_long !== undefined) {
        document.getElementById('ema-long').value = params.ema_long;
    }
    if (params.macd_signal !== undefined) {
        document.getElementById('macd-signal').value = params.macd_signal;
    }
    if (params.bb_period !== undefined) {
        document.getElementById('bb-period').value = params.bb_period;
    }
    if (params.bb_std !== undefined) {
        document.getElementById('bb-std').value = params.bb_std;
    }
    if (params.momentum_period !== undefined) {
        document.getElementById('momentum-period').value = params.momentum_period;
    }
    if (params.min_history !== undefined) {
        document.getElementById('min-history').value = params.min_history;
    }

    // Paramètres de risque
    if (params.risk_per_trade !== undefined) {
        document.getElementById('risk-per-trade').value = (params.risk_per_trade * 100).toFixed(0);
    }
    if (params.max_allocation_per_coin !== undefined) {
        document.getElementById('max-allocation').value = (params.max_allocation_per_coin * 100).toFixed(0);
    }
    if (params.stop_loss !== undefined) {
        document.getElementById('stop-loss').value = (params.stop_loss * 100).toFixed(0);
    }
    if (params.take_profit !== undefined) {
        document.getElementById('take-profit').value = (params.take_profit * 100).toFixed(0);
    }
    if (params.twitter_weight !== undefined) {
        document.getElementById('twitter-weight').value = (params.twitter_weight * 100).toFixed(0);
    }
}

// Appliquer les meilleurs paramètres aux champs de configuration
function applyBestParameters() {
    if (!currentBestParameters) {
        alert('Aucun paramètre optimal disponible');
        return;
    }

    updateAllParameters(currentBestParameters);

    // Effet visuel de confirmation
    const section = document.getElementById('best-params-inline');
    section.style.animation = 'pulse 0.5s';
    setTimeout(() => {
        section.style.animation = '';
    }, 500);

    alert('✅ Paramètres optimaux appliqués avec succès !');
}

// Afficher le classement Twitter
function displayTwitterRankings(rankings, suggestedWeights) {
    const section = document.getElementById('twitter-rankings-section');
    section.style.display = 'block';

    const grid = document.getElementById('twitter-rankings-grid');

    if (!rankings || rankings.length === 0) {
        grid.innerHTML = '<p class="no-data">Aucune donnée Twitter disponible</p>';
        return;
    }

    grid.innerHTML = rankings.map((rank, index) => `
        <div class="twitter-rank-item">
            <div class="rank-position">${index + 1}</div>
            <div class="rank-influencer">${rank.influencer}</div>
            <div class="rank-stat">
                <span class="rank-stat-label">Win Rate</span>
                <span class="rank-stat-value ${rank.win_rate >= 50 ? 'positive' : 'negative'}">
                    ${rank.win_rate.toFixed(1)}%
                </span>
            </div>
            <div class="rank-stat">
                <span class="rank-stat-label">Trades</span>
                <span class="rank-stat-value">${rank.total_trades}</span>
            </div>
            <div class="rank-stat">
                <span class="rank-stat-label">PNL Moyen</span>
                <span class="rank-stat-value ${rank.avg_pnl >= 0 ? 'positive' : 'negative'}">
                    ${rank.avg_pnl >= 0 ? '+' : ''}${rank.avg_pnl.toFixed(2)}%
                </span>
            </div>
            <div class="rank-stat">
                <span class="rank-stat-label">Score</span>
                <span class="rank-stat-value">${rank.reliability_score.toFixed(1)}</span>
            </div>
        </div>
    `).join('');

    // Afficher les poids suggérés
    if (suggestedWeights && Object.keys(suggestedWeights).length > 0) {
        const weightsSection = document.getElementById('suggested-weights-section');
        weightsSection.style.display = 'block';

        const weightsGrid = document.getElementById('suggested-weights-grid');

        // Trier par poids décroissant
        const sortedWeights = Object.entries(suggestedWeights)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 10);

        weightsGrid.innerHTML = sortedWeights.map(([influencer, weight]) => `
            <div class="weight-item">
                <span class="weight-influencer">${influencer}</span>
                <span class="weight-value">${weight.toFixed(2)}</span>
            </div>
        `).join('');
    }
}

// ====== NOUVEAU: Module d'Autocritique ======

// Charger et afficher l'autocritique
async function loadAutocritique() {
    try {
        const response = await fetch(`${API_URL}/autocritique/latest`);

        if (!response.ok) {
            // Pas d'autocritique disponible
            document.getElementById('autocritique-section').style.display = 'none';
            return;
        }

        const data = await response.json();

        // Afficher la section
        document.getElementById('autocritique-section').style.display = 'block';

        // Afficher la comparaison historique
        displayHistoricalComparison(data.historical_comparison);

        // Afficher l'analyse des transactions
        displayTransactionAnalysis(data.transaction_analysis);

        // Afficher l'anticipation du marché
        displayMarketAnticipation(data.market_anticipation_analysis);

        // Afficher l'impact des influenceurs
        displayInfluencerImpact(data.influencer_impact_analysis);

    } catch (error) {
        console.error('Error loading autocritique:', error);
        document.getElementById('autocritique-section').style.display = 'none';
    }
}

// Afficher la comparaison historique
function displayHistoricalComparison(comparison) {
    const container = document.getElementById('historical-comparison');

    if (!comparison || !comparison.has_history) {
        container.style.display = 'none';
        return;
    }

    container.style.display = 'block';
    container.innerHTML = `
        <strong>📊 Comparaison Historique (${comparison.total_iterations} itérations)</strong><br>
        ${comparison.comparison_text}
    `;
}

// Afficher l'analyse des transactions
function displayTransactionAnalysis(analysis) {
    if (!analysis) return;

    const timing = analysis.timing_analysis || {};

    document.getElementById('ac-total-transactions').textContent = analysis.total_transactions || 0;
    document.getElementById('ac-early-exits').textContent = timing.early_exits || 0;
    document.getElementById('ac-late-exits').textContent = timing.late_exits || 0;
    document.getElementById('ac-good-exits').textContent = timing.good_exits || 0;
    document.getElementById('ac-good-entries').textContent = timing.good_entries || 0;
    document.getElementById('ac-bad-entries').textContent = timing.bad_entries || 0;

    // Afficher les recommandations
    const recommendationsList = document.getElementById('timing-recommendations');
    if (analysis.recommendations && analysis.recommendations.length > 0) {
        recommendationsList.innerHTML = analysis.recommendations.map(rec =>
            `<li>${rec}</li>`
        ).join('');
    } else {
        recommendationsList.innerHTML = '<li>✅ Timing des transactions optimal</li>';
    }

    // Afficher les transactions détaillées
    displayDetailedTransactions(analysis.transactions || []);
}

// Afficher les transactions détaillées
function displayDetailedTransactions(transactions) {
    const container = document.getElementById('detailed-transactions');

    if (!transactions || transactions.length === 0) {
        container.innerHTML = '<p class="no-data">Aucune transaction disponible</p>';
        return;
    }

    // Prendre les 10 premières transactions
    const topTransactions = transactions.slice(0, 10);

    container.innerHTML = topTransactions.map(tx => {
        const badgeClass = tx.action === 'BUY' ? 'success' :
                          tx.pnl_pct && tx.pnl_pct > 0 ? 'success' : 'danger';
        const pnlText = tx.pnl_pct ? `${tx.pnl_pct > 0 ? '+' : ''}${tx.pnl_pct.toFixed(2)}%` : '';

        return `
            <div class="transaction-item ${tx.action.toLowerCase()}">
                <div class="transaction-header">
                    <div>
                        <span class="badge ${badgeClass}">${tx.action}</span>
                        <strong>${tx.symbol}</strong>
                        ${pnlText ? `<span class="metric-value ${tx.pnl_pct > 0 ? 'positive' : 'negative'}">${pnlText}</span>` : ''}
                    </div>
                    <span class="transaction-details">${tx.price ? tx.price.toFixed(2) + '€' : ''}</span>
                </div>
                <div class="transaction-details">
                    ${tx.date} • Score: ${tx.score || 0}
                </div>
                ${tx.reasons && tx.reasons.length > 0 ? `
                    <div class="transaction-details" style="margin-top: 0.5rem;">
                        Raisons: ${tx.reasons.join(', ')}
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

// Afficher l'anticipation du marché
function displayMarketAnticipation(analysis) {
    if (!analysis) return;

    const scores = analysis.anticipation_scores || {};

    document.getElementById('ac-early-detection').textContent = scores.early_detection || 0;
    document.getElementById('ac-missed-signals').textContent = scores.missed_signals || 0;
    document.getElementById('ac-detection-rate').textContent =
        (analysis.early_detection_rate || 0).toFixed(1) + '%';

    const quality = analysis.anticipation_quality || 'N/A';
    const qualityElement = document.getElementById('ac-anticipation-quality');
    qualityElement.textContent = quality.toUpperCase();
    qualityElement.className = 'metric-value';
    if (quality === 'excellent' || quality === 'good') {
        qualityElement.classList.add('positive');
    } else if (quality === 'poor') {
        qualityElement.classList.add('negative');
    }

    // Afficher les détails d'anticipation
    const detailsContainer = document.getElementById('anticipation-details');
    if (analysis.details && analysis.details.length > 0) {
        detailsContainer.innerHTML = analysis.details.map(detail => `
            <div style="padding: 0.5rem; margin-bottom: 0.5rem; background: rgba(51, 65, 85, 0.3); border-radius: 4px; font-size: 0.875rem;">
                <span class="badge ${detail.anticipation === 'early' ? 'success' : 'danger'}">
                    ${detail.anticipation === 'early' ? '✓' : '✗'}
                </span>
                ${detail.description}
            </div>
        `).join('');
    } else {
        detailsContainer.innerHTML = '<p style="font-size: 0.875rem; color: var(--text-muted);">Aucun mouvement majeur détecté</p>';
    }
}

// Afficher l'impact des influenceurs
function displayInfluencerImpact(analysis) {
    if (!analysis) return;

    document.getElementById('ac-beneficial-count').textContent = analysis.beneficial_count || 0;
    document.getElementById('ac-neutral-count').textContent = analysis.neutral_count || 0;
    document.getElementById('ac-harmful-count').textContent = analysis.harmful_count || 0;

    // Afficher les recommandations
    const recommendationsList = document.getElementById('influencer-recommendations');
    if (analysis.recommendations && analysis.recommendations.length > 0) {
        recommendationsList.innerHTML = analysis.recommendations.map(rec =>
            `<li>${rec}</li>`
        ).join('');
    } else {
        recommendationsList.innerHTML = '<li>Aucune recommandation spécifique</li>';
    }
}
