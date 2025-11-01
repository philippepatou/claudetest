// Game State
const gameState = {
    data: 0,
    nodes: 1,
    layers: 1,
    computers: 0,
    ensembles: 0,
    lastSave: Date.now(),

    // Purchased upgrades
    upgrades: {
        nodeEfficiency1: false,
        nodeEfficiency2: false,
        layerBonus1: false,
        trainingBoost1: false,
        trainingBoost2: false,
    }
};

// Game Configuration
const config = {
    // Base costs
    nodeCost: 10,
    layerCost: 100,
    computerCost: 1000,

    // Cost scaling
    nodeScaling: 1.15,
    layerScaling: 2.0,
    computerScaling: 1.5,

    // Production
    baseNodeProduction: 0.1,
    computerBonus: 0.1, // 10% per computer

    // Prestige
    prestigeThreshold: 10000,
    ensembleBonus: 0.15, // 15% per ensemble

    // Game loop
    tickRate: 100, // ms (10 ticks per second)
    saveInterval: 30000, // 30 seconds
};

// Upgrades Database
const upgradesDatabase = [
    {
        id: 'nodeEfficiency1',
        name: 'Optimized Nodes I',
        description: 'Nodes produce 50% more data',
        cost: 500,
        effect: () => 1.5,
        unlockCondition: () => gameState.layers >= 2,
    },
    {
        id: 'nodeEfficiency2',
        name: 'Optimized Nodes II',
        description: 'Nodes produce 100% more data',
        cost: 5000,
        effect: () => 2.0,
        unlockCondition: () => gameState.layers >= 3,
    },
    {
        id: 'layerBonus1',
        name: 'Deep Learning',
        description: 'Each layer multiplies production by 1.2x',
        cost: 2000,
        effect: () => Math.pow(1.2, gameState.layers),
        unlockCondition: () => gameState.layers >= 2,
    },
    {
        id: 'trainingBoost1',
        name: 'Better Training Algorithm I',
        description: 'Clicking produces 5 data instead of 1',
        cost: 100,
        effect: () => 5,
        unlockCondition: () => gameState.data >= 50,
    },
    {
        id: 'trainingBoost2',
        name: 'Better Training Algorithm II',
        description: 'Clicking produces 20 data instead of current amount',
        cost: 1000,
        effect: () => 20,
        unlockCondition: () => gameState.upgrades.trainingBoost1,
    },
];

// Calculate node cost
function getNodeCost() {
    return Math.floor(config.nodeCost * Math.pow(config.nodeScaling, gameState.nodes - 1));
}

// Calculate layer cost
function getLayerCost() {
    return Math.floor(config.layerCost * Math.pow(config.layerScaling, gameState.layers - 1));
}

// Calculate computer cost
function getComputerCost() {
    return Math.floor(config.computerCost * Math.pow(config.computerScaling, gameState.computers));
}

// Calculate data per second
function getDataPerSecond() {
    if (gameState.nodes === 0) return 0;

    let baseProduction = gameState.nodes * config.baseNodeProduction;

    // Apply ensemble bonus
    let ensembleMultiplier = 1 + (gameState.ensembles * config.ensembleBonus);

    // Apply computer bonus
    let computerMultiplier = 1 + (gameState.computers * config.computerBonus);

    // Apply upgrade bonuses
    let upgradeMultiplier = 1;
    if (gameState.upgrades.nodeEfficiency1) {
        upgradeMultiplier *= upgradesDatabase.find(u => u.id === 'nodeEfficiency1').effect();
    }
    if (gameState.upgrades.nodeEfficiency2) {
        upgradeMultiplier *= upgradesDatabase.find(u => u.id === 'nodeEfficiency2').effect();
    }
    if (gameState.upgrades.layerBonus1) {
        upgradeMultiplier *= upgradesDatabase.find(u => u.id === 'layerBonus1').effect();
    }

    return baseProduction * ensembleMultiplier * computerMultiplier * upgradeMultiplier;
}

// Calculate training click value
function getTrainingValue() {
    if (gameState.upgrades.trainingBoost2) {
        return upgradesDatabase.find(u => u.id === 'trainingBoost2').effect();
    }
    if (gameState.upgrades.trainingBoost1) {
        return upgradesDatabase.find(u => u.id === 'trainingBoost1').effect();
    }
    return 1;
}

// Buy node
function buyNode() {
    const cost = getNodeCost();
    if (gameState.data >= cost) {
        gameState.data -= cost;
        gameState.nodes++;
        updateUI();
        updateNetworkVisual();
    }
}

// Buy layer
function buyLayer() {
    const cost = getLayerCost();
    if (gameState.data >= cost) {
        gameState.data -= cost;
        gameState.layers++;
        updateUI();
        updateNetworkVisual();
        updateUpgrades();

        // Unlock prestige at layer 3
        if (gameState.layers >= 3) {
            document.getElementById('prestige-section').style.display = 'block';
        }
    }
}

// Buy computer
function buyComputer() {
    const cost = getComputerCost();
    if (gameState.data >= cost) {
        gameState.data -= cost;
        gameState.computers++;
        updateUI();
    }
}

// Train network (click)
function trainNetwork() {
    gameState.data += getTrainingValue();
    updateUI();
}

// Buy upgrade
function buyUpgrade(upgradeId) {
    const upgrade = upgradesDatabase.find(u => u.id === upgradeId);
    if (!upgrade || gameState.upgrades[upgradeId]) return;

    if (gameState.data >= upgrade.cost) {
        gameState.data -= upgrade.cost;
        gameState.upgrades[upgradeId] = true;
        updateUI();
        updateUpgrades();
    }
}

// Prestige
function prestige() {
    if (gameState.data >= config.prestigeThreshold) {
        if (confirm('Create an Ensemble? This will reset your progress but give you a permanent +15% production bonus!')) {
            gameState.ensembles++;

            // Reset everything except ensembles
            gameState.data = 0;
            gameState.nodes = 1;
            gameState.layers = 1;
            gameState.computers = 0;

            // Reset upgrades
            for (let key in gameState.upgrades) {
                gameState.upgrades[key] = false;
            }

            updateUI();
            updateNetworkVisual();
            updateUpgrades();

            // Hide prestige section until layer 3 again
            document.getElementById('prestige-section').style.display = 'none';
        }
    }
}

// Update network visual
function updateNetworkVisual() {
    const visual = document.getElementById('network-visual');
    visual.innerHTML = '';

    // Calculate nodes per layer
    const nodesPerLayer = Math.ceil(gameState.nodes / gameState.layers);

    for (let layer = 0; layer < gameState.layers; layer++) {
        const layerDiv = document.createElement('div');
        layerDiv.className = 'network-layer';

        const nodesInThisLayer = Math.min(nodesPerLayer, gameState.nodes - (layer * nodesPerLayer));

        for (let i = 0; i < nodesInThisLayer; i++) {
            const node = document.createElement('div');
            node.className = 'node active';
            layerDiv.appendChild(node);
        }

        visual.appendChild(layerDiv);
    }
}

// Update upgrades list
function updateUpgrades() {
    const container = document.getElementById('upgrades-container');

    // Filter available upgrades
    const availableUpgrades = upgradesDatabase.filter(upgrade =>
        !gameState.upgrades[upgrade.id] && upgrade.unlockCondition()
    );

    if (availableUpgrades.length === 0 && gameState.layers < 2) {
        container.innerHTML = '<p class="unlock-message">Unlock more layers to access the shop!</p>';
        return;
    }

    if (availableUpgrades.length === 0) {
        container.innerHTML = '<p class="unlock-message">All upgrades purchased!</p>';
        return;
    }

    container.innerHTML = '';

    availableUpgrades.forEach(upgrade => {
        const upgradeDiv = document.createElement('div');
        upgradeDiv.className = 'upgrade-item';

        upgradeDiv.innerHTML = `
            <h4>${upgrade.name}</h4>
            <p>${upgrade.description}</p>
            <button class="action-btn ${gameState.data >= upgrade.cost ? '' : 'disabled'}"
                    onclick="buyUpgrade('${upgrade.id}')"
                    ${gameState.data >= upgrade.cost ? '' : 'disabled'}>
                <span class="btn-name">Purchase</span>
                <span class="btn-cost">Cost: ${formatNumber(upgrade.cost)} Data</span>
            </button>
        `;

        container.appendChild(upgradeDiv);
    });
}

// Format numbers
function formatNumber(num) {
    if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return Math.floor(num).toString();
}

// Update UI
function updateUI() {
    // Update header stats
    document.getElementById('data-display').textContent = formatNumber(gameState.data);
    document.getElementById('data-rate').textContent = formatNumber(getDataPerSecond());

    // Update network stats
    document.getElementById('nodes-count').textContent = gameState.nodes;
    document.getElementById('layers-count').textContent = gameState.layers;
    document.getElementById('computing-power').textContent = gameState.computers;
    document.getElementById('training-speed').textContent =
        (1 + gameState.computers * config.computerBonus).toFixed(2) + 'x';

    // Update costs and effects
    document.getElementById('node-cost').textContent = formatNumber(getNodeCost());
    document.getElementById('node-effect').textContent = (config.baseNodeProduction).toFixed(1);
    document.getElementById('layer-cost').textContent = formatNumber(getLayerCost());
    document.getElementById('computer-cost').textContent = formatNumber(getComputerCost());

    // Update button states
    const nodeCost = getNodeCost();
    const layerCost = getLayerCost();
    const computerCost = getComputerCost();

    document.getElementById('buy-node-btn').disabled = gameState.data < nodeCost;
    document.getElementById('buy-layer-btn').disabled = gameState.data < layerCost;
    document.getElementById('buy-computer-btn').disabled = gameState.data < computerCost;

    // Enable layer and computer buttons once certain conditions are met
    if (gameState.nodes >= 5) {
        document.getElementById('buy-layer-btn').disabled = gameState.data < layerCost;
    }
    if (gameState.layers >= 2) {
        document.getElementById('buy-computer-btn').disabled = gameState.data < computerCost;
    }

    // Update prestige
    document.getElementById('ensemble-count').textContent = gameState.ensembles;
    document.getElementById('ensemble-bonus').textContent =
        (1 + gameState.ensembles * config.ensembleBonus).toFixed(2) + 'x';

    const canPrestige = gameState.data >= config.prestigeThreshold;
    document.getElementById('prestige-btn').disabled = !canPrestige;
}

// Game loop
function gameTick() {
    const deltaTime = config.tickRate / 1000; // Convert to seconds
    gameState.data += getDataPerSecond() * deltaTime;
    updateUI();
}

// Save game
function saveGame() {
    gameState.lastSave = Date.now();
    localStorage.setItem('perceptronSave', JSON.stringify(gameState));
    console.log('Game saved!');
}

// Load game
function loadGame() {
    const save = localStorage.getItem('perceptronSave');
    if (save) {
        const loaded = JSON.parse(save);
        Object.assign(gameState, loaded);

        // Calculate offline progress
        const now = Date.now();
        const timePassed = (now - gameState.lastSave) / 1000; // seconds
        const offlineData = getDataPerSecond() * timePassed;

        if (offlineData > 0) {
            gameState.data += offlineData;
            alert(`Welcome back! You earned ${formatNumber(offlineData)} data while offline (${Math.floor(timePassed / 60)} minutes)`);
        }

        gameState.lastSave = now;
        console.log('Game loaded!');
    }
}

// Hard reset
function hardReset() {
    if (confirm('Are you sure? This will delete ALL progress including Ensembles!')) {
        if (confirm('Really? This cannot be undone!')) {
            localStorage.removeItem('perceptronSave');
            location.reload();
        }
    }
}

// Initialize game
function initGame() {
    // Load saved game
    loadGame();

    // Set up event listeners
    document.getElementById('train-btn').addEventListener('click', trainNetwork);
    document.getElementById('buy-node-btn').addEventListener('click', buyNode);
    document.getElementById('buy-layer-btn').addEventListener('click', buyLayer);
    document.getElementById('buy-computer-btn').addEventListener('click', buyComputer);
    document.getElementById('prestige-btn').addEventListener('click', prestige);
    document.getElementById('save-btn').addEventListener('click', saveGame);
    document.getElementById('reset-btn').addEventListener('click', hardReset);

    // Initial UI update
    updateUI();
    updateNetworkVisual();
    updateUpgrades();

    // Show prestige if unlocked
    if (gameState.layers >= 3) {
        document.getElementById('prestige-section').style.display = 'block';
    }

    // Start game loop
    setInterval(gameTick, config.tickRate);

    // Auto-save every 30 seconds
    setInterval(saveGame, config.saveInterval);

    console.log('Perceptron game initialized!');
}

// Start game when page loads
window.addEventListener('DOMContentLoaded', initGame);
