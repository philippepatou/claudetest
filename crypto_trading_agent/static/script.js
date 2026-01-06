// Configuration de l'API
const API_URL = 'http://localhost:5000/api';
let pollInterval = null;

// Variables globales pour l'autocritique
let currentAutocritiqueData = null;
let portfolioChart = null;
let portfolioDataPoints = [];
let lastIterationNumber = 0;
let lastPortfolioHistoryLength = 0;
let initialCapital = 1000; // Capital de départ pour le graphique

// Toast notification counter
let toastCounter = 0;

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
    document.getElementById('risk-dashboard-section').style.display = 'block';
    document.getElementById('results-section').style.display = 'none';

    // Réinitialiser les logs
    document.getElementById('logs').innerHTML = '';

    // Réinitialiser les variables de suivi
    lastIterationNumber = 0;
    lastPortfolioHistoryLength = 0;

    // Stocker le capital initial pour le graphique
    initialCapital = config.simulation_params.initial_balance;

    // Initialiser le graphique du portfolio
    initPortfolioChart();

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
            showToast('Simulation démarrée avec succès', 'success');
        } else {
            showToast('Erreur lors du démarrage de la simulation', 'error');
            startBtn.disabled = false;
            stopBtn.disabled = true;
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Erreur de connexion au serveur', 'error');
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
        showToast('Historique effacé avec succès', 'success');
    } catch (error) {
        console.error('Error:', error);
        showToast('Erreur lors de l\'effacement de l\'historique', 'error');
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

        // Mettre à jour le tableau de bord des risques
        if (status.running || status.results) {
            updateRiskDashboard();
        }

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

    // Détecter le changement d'itération pour réinitialiser le graphique
    if (status.current_iteration !== lastIterationNumber) {
        lastIterationNumber = status.current_iteration;
        lastPortfolioHistoryLength = 0;
        initPortfolioChart(); // Effacer et réinitialiser le graphique
    }

    // Mettre à jour la valeur du portfolio et le ROI en temps réel
    const currentValue = status.current_portfolio_value || status.results?.final_value || 0;
    const currentRoi = status.current_roi !== undefined ? status.current_roi : (status.results?.roi || 0);

    document.getElementById('portfolio-value').textContent = `${currentValue.toFixed(2)}€`;
    document.getElementById('current-roi').textContent = `${currentRoi >= 0 ? '+' : ''}${currentRoi.toFixed(2)}%`;

    // Mettre à jour le graphique avec l'historique complet du portfolio
    if (status.portfolio_history && status.portfolio_history.length > 0) {
        // Ajouter uniquement les nouveaux points depuis la dernière mise à jour
        for (let i = lastPortfolioHistoryLength; i < status.portfolio_history.length; i++) {
            const point = status.portfolio_history[i];
            updatePortfolioChart(point.day, point.value);
        }
        lastPortfolioHistoryLength = status.portfolio_history.length;
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

    // Ajouter un bouton pour appliquer ces paramètres
    // Vérifier si le bouton n'existe pas déjà
    if (!document.getElementById('apply-best-params-detailed-btn')) {
        const button = document.createElement('button');
        button.id = 'apply-best-params-detailed-btn';
        button.className = 'btn btn-success btn-sm';
        button.style.marginTop = '1.5rem';
        button.style.width = '100%';
        button.textContent = '✨ Appliquer Ces Paramètres';
        button.onclick = () => applyBestParameters();
        section.appendChild(button);
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

// Variable globale pour stocker les meilleurs paramètres
let currentBestParameters = null;

// Afficher les meilleurs paramètres inline (près de la config)
function displayBestParametersInline(bestIteration) {
    const section = document.getElementById('best-params-inline');
    section.style.display = 'block';

    // Afficher le bouton d'application des meilleurs paramètres
    const applyButton = document.getElementById('apply-best-params-btn');
    if (applyButton) {
        applyButton.style.display = 'inline-block';
    }

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
        showToast('Aucun paramètre optimal disponible', 'warning');
        return;
    }

    updateAllParameters(currentBestParameters);

    // Effet visuel de confirmation
    const section = document.getElementById('best-params-inline');
    section.style.animation = 'pulse 0.5s';
    setTimeout(() => {
        section.style.animation = '';
    }, 500);

    showToast('✅ Paramètres optimaux appliqués avec succès !', 'success');
}

// Appliquer les meilleurs paramètres historiques (depuis tout l'historique)
async function applyBestHistoricalParameters() {
    try {
        const response = await fetch(`${API_URL}/history/best`);
        if (!response.ok) {
            showToast('Impossible de charger les meilleurs paramètres historiques', 'error');
            return;
        }

        const data = await response.json();
        if (!data.parameters) {
            showToast('Aucun paramètre historique disponible', 'warning');
            return;
        }

        updateAllParameters(data.parameters);

        // Effet visuel de confirmation
        const button = document.getElementById('apply-best-params-btn');
        button.style.animation = 'pulse 0.5s';
        setTimeout(() => {
            button.style.animation = '';
        }, 500);

        // Scroll vers la section de configuration
        document.querySelector('.config-grid').scrollIntoView({ behavior: 'smooth', block: 'start' });

        showToast(`✅ Meilleurs paramètres historiques appliqués ! Itération: ${data.iteration}, ROI: ${data.roi.toFixed(2)}%, Score: ${data.score.toFixed(1)}/100`, 'success', 6000);
    } catch (error) {
        console.error('Error applying best historical parameters:', error);
        showToast('Erreur lors de l\'application des paramètres', 'error');
    }
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

        // Ajouter un bouton pour appliquer les poids suggérés
        // Vérifier si le bouton n'existe pas déjà
        if (!document.getElementById('apply-twitter-weights-btn')) {
            const button = document.createElement('button');
            button.id = 'apply-twitter-weights-btn';
            button.className = 'btn btn-primary btn-sm';
            button.style.marginTop = '1rem';
            button.style.width = '100%';
            button.textContent = '🎯 Appliquer les Poids Suggérés';
            button.onclick = () => applyTwitterWeights(suggestedWeights);
            weightsSection.appendChild(button);
        }
    }
}

// Appliquer les poids Twitter suggérés
function applyTwitterWeights(weights) {
    if (!weights || Object.keys(weights).length === 0) {
        showToast('Aucun poids suggéré disponible', 'warning');
        return;
    }

    // Calculer le poids moyen des influenceurs suggérés
    const avgWeight = Object.values(weights).reduce((sum, w) => sum + w, 0) / Object.keys(weights).length;

    // Mettre à jour le twitter_weight avec la moyenne
    const twitterWeightField = document.getElementById('twitter-weight');
    if (twitterWeightField) {
        twitterWeightField.value = (avgWeight * 100).toFixed(1);
    }

    showToast(`✅ Poids Twitter appliqué: ${(avgWeight * 100).toFixed(1)}% - Fiabilité moyenne des influenceurs bénéfiques`, 'success', 5000);
}

// ====== NOUVEAU: Module d'Autocritique ======

// Charger et afficher l'autocritique
async function loadAutocritique() {
    console.log('📊 Loading autocritique...');
    try {
        const response = await fetch(`${API_URL}/autocritique/latest`);
        console.log('📊 Autocritique response status:', response.status);

        if (!response.ok) {
            // Pas d'autocritique disponible
            console.warn('⚠️ No autocritique available (status:', response.status + ')');
            document.getElementById('autocritique-section').style.display = 'none';
            return;
        }

        const data = await response.json();
        console.log('✓ Autocritique data loaded:', data);

        // Stocker les données pour les boutons d'ajustement
        currentAutocritiqueData = data;

        // Afficher la section
        document.getElementById('autocritique-section').style.display = 'block';
        console.log('✓ Autocritique section displayed');

        // Afficher la comparaison historique
        displayHistoricalComparison(data.historical_comparison);

        // Afficher l'analyse des transactions
        displayTransactionAnalysis(data.transaction_analysis);

        // Afficher l'anticipation du marché
        displayMarketAnticipation(data.market_anticipation_analysis);

        // Afficher l'impact des influenceurs
        displayInfluencerImpact(data.influencer_impact_analysis);

        // Afficher les paramètres suggérés (NOUVEAU)
        displaySuggestedParameters(data.suggested_parameters);

        console.log('✓ All autocritique sections displayed');

    } catch (error) {
        console.error('❌ Error loading autocritique:', error);
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

// Variable globale pour stocker les paramètres suggérés
let currentSuggestedParameters = null;

// Afficher les paramètres suggérés par l'autocritique
function displaySuggestedParameters(params) {
    console.log('📊 Displaying suggested parameters:', params);

    if (!params) {
        console.warn('⚠️ No suggested parameters available');
        document.getElementById('suggested-params-section').style.display = 'none';
        return;
    }

    // Stocker les paramètres pour l'application ultérieure
    currentSuggestedParameters = params;

    const grid = document.getElementById('suggested-params-grid');

    // Définir les noms lisibles des paramètres
    const paramLabels = {
        'rsi_period': 'RSI Period',
        'rsi_oversold': 'RSI Oversold',
        'rsi_overbought': 'RSI Overbought',
        'ema_short': 'EMA Court',
        'ema_long': 'EMA Long',
        'risk_per_trade': 'Risque par Trade',
        'max_allocation_per_coin': 'Allocation Max',
        'stop_loss': 'Stop Loss',
        'take_profit': 'Take Profit',
        'twitter_weight': 'Poids Twitter',
        'macd_signal': 'MACD Signal',
        'bb_period': 'BB Period',
        'bb_std': 'BB Std Dev',
        'momentum_period': 'Momentum Period',
        'min_history': 'Historique Min'
    };

    // Créer les éléments de paramètres
    const paramItems = Object.entries(params).map(([key, value]) => {
        const label = paramLabels[key] || key;
        let displayValue = value;

        // Formater les valeurs en pourcentage si nécessaire
        if (['risk_per_trade', 'max_allocation_per_coin', 'stop_loss', 'take_profit', 'twitter_weight'].includes(key)) {
            displayValue = (value * 100).toFixed(0) + '%';
        } else if (Number.isInteger(value)) {
            displayValue = value;
        } else {
            displayValue = value.toFixed(2);
        }

        return `
            <div class="param-item">
                <div class="param-name">${label}</div>
                <div class="param-value">${displayValue}</div>
            </div>
        `;
    }).join('');

    grid.innerHTML = paramItems;
    document.getElementById('suggested-params-section').style.display = 'block';
    console.log('✓ Suggested parameters displayed');
}

// Appliquer les paramètres suggérés aux champs du formulaire
function applySuggestedParameters() {
    if (!currentSuggestedParameters) {
        showToast('Aucun paramètre suggéré disponible', 'warning');
        return;
    }

    console.log('✨ Applying suggested parameters:', currentSuggestedParameters);

    // Appliquer les paramètres en utilisant la fonction updateAllParameters existante
    updateAllParameters(currentSuggestedParameters);

    // Effet visuel de confirmation
    const section = document.getElementById('suggested-params-section');
    section.style.animation = 'fadeIn 0.5s';
    setTimeout(() => {
        section.style.animation = '';
    }, 500);

    // Scroll vers la section de configuration
    document.querySelector('.config-grid').scrollIntoView({ behavior: 'smooth', block: 'start' });

    showToast('✅ Paramètres suggérés appliqués avec succès ! Vous pouvez maintenant lancer une nouvelle simulation.', 'success', 5000);
}

// ====== NOUVEAU: Graphique Portfolio ======

// Initialiser le graphique du portfolio
function initPortfolioChart() {
    const ctx = document.getElementById('portfolio-chart');
    if (!ctx) return;

    // Détruire l'ancien graphique s'il existe
    if (portfolioChart) {
        portfolioChart.destroy();
    }

    // Réinitialiser les données
    portfolioDataPoints = [];

    portfolioChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Valeur du Portfolio (€)',
                    data: [],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,  // Retirer les points
                    pointHoverRadius: 4  // Afficher un point seulement au survol
                },
                {
                    label: 'Capital Initial',
                    data: [],
                    borderColor: '#fbbf24',
                    borderWidth: 2,
                    borderDash: [5, 5],  // Ligne pointillée
                    fill: false,
                    pointRadius: 0,
                    pointHoverRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#f8fafc'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    min: initialCapital - 300,  // Placeholder, sera mis à jour dynamiquement
                    max: initialCapital + 300,  // Placeholder, sera mis à jour dynamiquement
                    ticks: {
                        color: '#94a3b8',
                        callback: function(value) {
                            return value.toFixed(2) + '€';
                        }
                    },
                    grid: {
                        color: function(context) {
                            // Mettre en évidence la ligne du capital initial
                            if (context.tick.value === initialCapital) {
                                return 'rgba(251, 191, 36, 0.3)';
                            }
                            return 'rgba(148, 163, 184, 0.1)';
                        }
                    }
                },
                x: {
                    ticks: {
                        color: '#94a3b8'
                    },
                    grid: {
                        color: 'rgba(148, 163, 184, 0.1)'
                    }
                }
            }
        }
    });
}

// Mettre à jour le graphique du portfolio
function updatePortfolioChart(day, value) {
    if (!portfolioChart) {
        initPortfolioChart();
    }

    if (portfolioChart) {
        // Ajouter le point à la courbe du portfolio
        portfolioChart.data.labels.push(`Jour ${day}`);
        portfolioChart.data.datasets[0].data.push(value);

        // Ajouter le point à la ligne du capital initial (valeur constante)
        portfolioChart.data.datasets[1].data.push(initialCapital);

        // Calculer l'échelle Y pour garder le capital initial au centre
        const allValues = portfolioChart.data.datasets[0].data;
        if (allValues.length > 0) {
            const maxValue = Math.max(...allValues);
            const minValue = Math.min(...allValues);

            // Calculer l'écart maximum par rapport au capital initial
            const maxDeviation = Math.max(
                Math.abs(maxValue - initialCapital),
                Math.abs(minValue - initialCapital)
            );

            // Ajouter une marge de 10% pour l'aération
            const margin = maxDeviation * 0.1;
            const totalRange = maxDeviation + margin;

            // Mettre à jour l'échelle Y de façon symétrique autour du capital initial
            portfolioChart.options.scales.y.min = initialCapital - totalRange;
            portfolioChart.options.scales.y.max = initialCapital + totalRange;
        }

        portfolioChart.update('none'); // 'none' pour animation plus rapide
    }
}

// ====== NOUVEAU: Fonctions d'Ajustement des Paramètres ======

// Ajuster le comportement des transactions (Stop-Loss / Take-Profit)
function adjustTransactionBehavior() {
    if (!currentAutocritiqueData || !currentAutocritiqueData.transaction_analysis) {
        alert('Aucune donnée d\'analyse disponible');
        return;
    }

    const timing = currentAutocritiqueData.transaction_analysis.timing_analysis || {};
    const total_exits = timing.early_exits + timing.late_exits + timing.good_exits;

    if (total_exits === 0) {
        showToast('Pas assez de données pour ajuster les paramètres', 'warning');
        return;
    }

    const early_pct = (timing.early_exits / total_exits) * 100;
    const late_pct = (timing.late_exits / total_exits) * 100;

    // Récupérer les valeurs actuelles
    let currentStopLoss = parseFloat(document.getElementById('stop-loss').value) / 100;
    let currentTakeProfit = parseFloat(document.getElementById('take-profit').value) / 100;

    let adjustments = [];

    // Ajuster en fonction de l'analyse
    if (early_pct > 40) {
        // Trop de sorties précoces → augmenter le take profit
        currentTakeProfit = Math.min(0.50, currentTakeProfit * 1.25);
        adjustments.push(`↗️ Take Profit augmenté à ${(currentTakeProfit * 100).toFixed(0)}% (sorties trop précoces)`);
    }

    if (late_pct > 40) {
        // Trop de sorties tardives → réduire le stop loss
        currentStopLoss = Math.max(0.05, currentStopLoss * 0.80);
        adjustments.push(`↘️ Stop Loss réduit à ${(currentStopLoss * 100).toFixed(0)}% (sorties trop tardives)`);
    }

    if (adjustments.length === 0) {
        showToast('✅ Le timing actuel est optimal ! Aucun ajustement nécessaire.', 'success', 4000);
        return;
    }

    // Appliquer les ajustements
    document.getElementById('stop-loss').value = (currentStopLoss * 100).toFixed(0);
    document.getElementById('take-profit').value = (currentTakeProfit * 100).toFixed(0);

    // Effet visuel
    document.getElementById('stop-loss').parentElement.style.animation = 'fadeIn 0.5s';
    document.getElementById('take-profit').parentElement.style.animation = 'fadeIn 0.5s';
    setTimeout(() => {
        document.getElementById('stop-loss').parentElement.style.animation = '';
        document.getElementById('take-profit').parentElement.style.animation = '';
    }, 500);

    showToast('✅ Paramètres ajustés ! ' + adjustments.join(', '), 'success', 6000);
}

// Ajuster le comportement d'anticipation du marché
function adjustAnticipationBehavior() {
    if (!currentAutocritiqueData || !currentAutocritiqueData.market_anticipation_analysis) {
        alert('Aucune donnée d\'anticipation disponible');
        return;
    }

    const analysis = currentAutocritiqueData.market_anticipation_analysis;
    const detectionRate = analysis.early_detection_rate || 0;

    let adjustments = [];
    let currentRsiOversold = parseInt(document.getElementById('rsi-oversold').value);
    let currentRsiOverbought = parseInt(document.getElementById('rsi-overbought').value);

    if (detectionRate < 30) {
        // Faible taux de détection → être plus agressif
        currentRsiOversold = Math.min(35, currentRsiOversold + 3);
        currentRsiOverbought = Math.max(65, currentRsiOverbought - 3);
        adjustments.push('🎯 Seuils RSI élargis pour plus de signaux');
        adjustments.push(`RSI Oversold: ${currentRsiOversold}`);
        adjustments.push(`RSI Overbought: ${currentRsiOverbought}`);
    } else if (detectionRate > 70) {
        // Très bon taux → rester conservateur
        showToast('✅ Excellente anticipation du marché ! Taux de détection: ' + detectionRate.toFixed(1) + '%', 'success', 5000);
        return;
    } else {
        // Taux moyen → ajustements légers
        currentRsiOversold = Math.min(35, currentRsiOversold + 2);
        currentRsiOverbought = Math.max(65, currentRsiOverbought - 2);
        adjustments.push('⚖️ Ajustements légers pour améliorer la détection');
        adjustments.push(`RSI Oversold: ${currentRsiOversold}`);
        adjustments.push(`RSI Overbought: ${currentRsiOverbought}`);
    }

    // Appliquer
    document.getElementById('rsi-oversold').value = currentRsiOversold;
    document.getElementById('rsi-overbought').value = currentRsiOverbought;

    // Effet visuel
    document.getElementById('rsi-oversold').parentElement.style.animation = 'fadeIn 0.5s';
    document.getElementById('rsi-overbought').parentElement.style.animation = 'fadeIn 0.5s';
    setTimeout(() => {
        document.getElementById('rsi-oversold').parentElement.style.animation = '';
        document.getElementById('rsi-overbought').parentElement.style.animation = '';
    }, 500);

    showToast('✅ Sensibilité ajustée ! ' + adjustments.join(', '), 'success', 6000);
}

// Ajuster les poids des influenceurs
function adjustInfluencerWeights() {
    if (!currentAutocritiqueData || !currentAutocritiqueData.influencer_impact_analysis) {
        alert('Aucune donnée d\'influenceurs disponible');
        return;
    }

    const analysis = currentAutocritiqueData.influencer_impact_analysis;
    const beneficial = analysis.beneficial_influencers || [];
    const harmful = analysis.harmful_influencers || [];

    if (beneficial.length === 0 && harmful.length === 0) {
        showToast('Pas assez de données sur les influenceurs', 'warning');
        return;
    }

    let message = '📊 Analyse des Influenceurs Twitter\n\n';

    if (beneficial.length > 0) {
        message += '✅ INFLUENCEURS BÉNÉFIQUES :\n';
        beneficial.forEach(inf => {
            message += `  • ${inf.influencer}: Win Rate ${inf.win_rate.toFixed(1)}%, PNL ${inf.avg_pnl >= 0 ? '+' : ''}${inf.avg_pnl.toFixed(2)}%\n`;
        });
        message += '\n';
    }

    if (harmful.length > 0) {
        message += '⚠️ INFLUENCEURS NUISIBLES :\n';
        harmful.forEach(inf => {
            message += `  • ${inf.influencer}: Win Rate ${inf.win_rate.toFixed(1)}%, PNL ${inf.avg_pnl >= 0 ? '+' : ''}${inf.avg_pnl.toFixed(2)}%\n`;
        });
        message += '\n';
    }

    const totalInfluencers = analysis.total_influencers_tracked || 0;
    const beneficialPct = beneficial.length > 0 ? (beneficial.length / totalInfluencers * 100) : 0;

    let twitterWeight = parseFloat(document.getElementById('twitter-weight').value) / 100;

    if (beneficialPct > 60) {
        // Beaucoup d'influenceurs bénéfiques → augmenter le poids
        twitterWeight = Math.min(0.50, twitterWeight * 1.2);
        message += `\n✨ Poids Twitter augmenté à ${(twitterWeight * 100).toFixed(0)}%`;
    } else if (beneficialPct < 30) {
        // Peu d'influenceurs bénéfiques → réduire le poids
        twitterWeight = Math.max(0.10, twitterWeight * 0.8);
        message += `\n⚠️ Poids Twitter réduit à ${(twitterWeight * 100).toFixed(0)}%`;
    } else {
        message += `\n⚖️ Poids Twitter maintenu à ${(twitterWeight * 100).toFixed(0)}%`;
    }

    // Appliquer
    document.getElementById('twitter-weight').value = (twitterWeight * 100).toFixed(0);

    // Effet visuel
    document.getElementById('twitter-weight').parentElement.style.animation = 'fadeIn 0.5s';
    setTimeout(() => {
        document.getElementById('twitter-weight').parentElement.style.animation = '';
    }, 500);

    showToast(message, 'info', 8000);
}

// ========================================
// ACCORDION SYSTEM
// ========================================

/**
 * Toggle accordion item open/closed
 * @param {HTMLElement} header - The accordion header button that was clicked
 */
function toggleAccordion(header) {
    const accordionItem = header.parentElement;
    const content = header.nextElementSibling;
    const icon = header.querySelector('.accordion-icon');

    // Check if currently open
    const isOpen = content.style.display === 'block';

    if (isOpen) {
        // Close it
        content.style.display = 'none';
        icon.textContent = '▼';
        accordionItem.classList.remove('active');
    } else {
        // Open it
        content.style.display = 'block';
        icon.textContent = '▲';
        accordionItem.classList.add('active');
    }
}

// ========================================
// TOAST NOTIFICATION SYSTEM
// ========================================

/**
 * Show a toast notification
 * @param {string} message - The message to display
 * @param {string} type - Type of toast: 'success', 'error', 'warning', 'info'
 * @param {number} duration - Duration in milliseconds (default: 4000)
 */
function showToast(message, type = 'info', duration = 4000) {
    const toastId = `toast-${toastCounter++}`;
    const container = document.getElementById('toast-container');

    // Create toast element
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast toast-${type}`;

    // Icon based on type
    const icons = {
        success: '✓',
        error: '✗',
        warning: '⚠',
        info: 'ℹ'
    };

    toast.innerHTML = `
        <div class="toast-icon">${icons[type]}</div>
        <div class="toast-message">${message}</div>
        <button class="toast-close" onclick="closeToast('${toastId}')">×</button>
    `;

    // Add to container
    container.appendChild(toast);

    // Trigger animation
    setTimeout(() => {
        toast.classList.add('toast-show');
    }, 10);

    // Auto-remove after duration
    setTimeout(() => {
        closeToast(toastId);
    }, duration);
}

/**
 * Close a toast notification
 * @param {string} toastId - ID of the toast to close
 */
function closeToast(toastId) {
    const toast = document.getElementById(toastId);
    if (toast) {
        toast.classList.remove('toast-show');
        toast.classList.add('toast-hide');

        // Remove from DOM after animation
        setTimeout(() => {
            toast.remove();
        }, 300);
    }
}

// ========================================
// RISK DASHBOARD FUNCTIONS
// ========================================

/**
 * Update risk dashboard with real-time metrics
 */
async function updateRiskDashboard() {
    try {
        const response = await fetch(`${API_URL}/risk/metrics`);

        if (!response.ok) {
            // Risk data not available yet
            return;
        }

        const risk = await response.json();

        // Update risk level banner
        updateRiskLevel(risk.risk_level);

        // Update drawdown metrics
        document.getElementById('risk-drawdown').textContent = `${risk.drawdown.toFixed(2)}%`;
        document.getElementById('risk-max-drawdown').textContent = `${risk.max_drawdown.toFixed(2)}%`;

        // Color code the drawdown
        const drawdownEl = document.getElementById('risk-drawdown');
        drawdownEl.className = 'risk-metric-value';
        if (risk.drawdown <= -15) {
            drawdownEl.style.color = '#dc2626'; // red
        } else if (risk.drawdown <= -10) {
            drawdownEl.style.color = '#ea580c'; // orange
        } else if (risk.drawdown <= -5) {
            drawdownEl.style.color = '#facc15'; // yellow
        } else {
            drawdownEl.style.color = '#22c55e'; // green
        }

        // Update circuit breaker status
        const cbStatus = risk.circuit_breaker.triggered ? '🚨 DÉCLENCHÉ' : '✓ ACTIF';
        const cbColor = risk.circuit_breaker.triggered ? '#dc2626' : '#22c55e';

        document.getElementById('risk-circuit-breaker').textContent = cbStatus;
        document.getElementById('risk-circuit-breaker').style.color = cbColor;
        document.getElementById('risk-cb-distance').textContent =
            `${risk.circuit_breaker.distance_to_trigger.toFixed(1)}%`;

        // Update VaR
        document.getElementById('risk-var').textContent = `${risk.var_95.toFixed(2)}%`;

        // Update Sharpe ratio
        const sharpeEl = document.getElementById('risk-sharpe');
        sharpeEl.textContent = risk.sharpe_ratio.toFixed(2);

        // Color code Sharpe ratio (> 1 is good, > 2 is excellent)
        if (risk.sharpe_ratio > 2) {
            sharpeEl.style.color = '#22c55e'; // green
        } else if (risk.sharpe_ratio > 1) {
            sharpeEl.style.color = '#84cc16'; // lime
        } else if (risk.sharpe_ratio > 0) {
            sharpeEl.style.color = '#facc15'; // yellow
        } else {
            sharpeEl.style.color = '#dc2626'; // red
        }

        // Update position risks table
        updatePositionRisksTable(risk.position_risks);

    } catch (error) {
        console.error('Error updating risk dashboard:', error);
    }
}

/**
 * Update risk level banner
 */
function updateRiskLevel(level) {
    const banner = document.getElementById('risk-level-banner');
    const valueEl = document.getElementById('risk-level-value');

    // Remove all risk level classes
    banner.className = 'risk-level-banner';

    // Add appropriate class and text
    switch (level) {
        case 'low':
            banner.classList.add('risk-low');
            valueEl.textContent = 'BAS';
            break;
        case 'medium':
            banner.classList.add('risk-medium');
            valueEl.textContent = 'MOYEN';
            break;
        case 'high':
            banner.classList.add('risk-high');
            valueEl.textContent = 'ÉLEVÉ';
            break;
        case 'critical':
            banner.classList.add('risk-critical');
            valueEl.textContent = 'CRITIQUE';
            break;
    }
}

/**
 * Update position risks table
 */
function updatePositionRisksTable(positions) {
    const tableEl = document.getElementById('position-risks-table');

    if (!positions || positions.length === 0) {
        tableEl.innerHTML = '<div class="position-risks-empty">Aucune position active</div>';
        return;
    }

    // Build table
    let html = '<table class="position-risks-table">';
    html += '<thead><tr>';
    html += '<th>Asset</th>';
    html += '<th>P&L</th>';
    html += '<th>Valeur</th>';
    html += '<th>Allocation</th>';
    html += '<th>High Watermark</th>';
    html += '<th>Trailing DD</th>';
    html += '</tr></thead>';
    html += '<tbody>';

    positions.forEach(pos => {
        const pnlClass = pos.pnl >= 0 ? 'positive' : 'negative';
        const trailingClass = pos.trailing_drawdown <= -5 ? 'negative' : '';

        html += '<tr>';
        html += `<td><strong>${pos.symbol}</strong></td>`;
        html += `<td class="${pnlClass}">${pos.pnl >= 0 ? '+' : ''}${pos.pnl.toFixed(2)}%</td>`;
        html += `<td>${pos.value.toFixed(2)}€</td>`;
        html += `<td>${pos.allocation.toFixed(1)}%</td>`;
        html += `<td>${pos.high_watermark.toFixed(2)}€</td>`;
        html += `<td class="${trailingClass}">${pos.trailing_drawdown.toFixed(2)}%</td>`;
        html += '</tr>';
    });

    html += '</tbody></table>';
    tableEl.innerHTML = html;
}
