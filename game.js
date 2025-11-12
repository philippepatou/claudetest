// Universal Paperclips Clone - Game Logic

class Game {
    constructor() {
        // État du jeu
        this.paperclips = 0;
        this.funds = 0;
        this.wire = 1000; // Départ avec du fil
        this.wireCost = 20;
        this.price = 0.25;
        this.demand = 50;
        this.marketing = 1;
        this.marketingCost = 100;

        // Manufacturing
        this.autoClippers = 0;
        this.autoClipperCost = 5;
        this.autoClipperRate = 0.2; // clips par seconde par autoclipper

        // Operations et Créativité
        this.operations = 0;
        this.creativity = 0;
        this.maxOps = 1000;
        this.maxCreativity = 1000;

        // Upgrades
        this.upgrades = [];
        this.purchasedUpgrades = [];

        // Projets
        this.projects = [];
        this.completedProjects = [];

        // Stats
        this.totalPaperclips = 0;
        this.unsoldPaperclips = 0;

        // Game loop
        this.lastUpdate = Date.now();
        this.gameLoop = null;

        this.initUpgrades();
        this.initProjects();
    }

    initUpgrades() {
        this.upgrades = [
            {
                id: 'improved-wire',
                name: 'Efficacité du fil améliorée',
                description: 'Chaque pouce de fil produit 10% de trombones en plus',
                cost: 50,
                effect: () => {
                    // Implémenté dans la logique de production
                }
            },
            {
                id: 'mega-clippers',
                name: 'MegaClippers',
                description: 'Les AutoClippers sont 25% plus rapides',
                cost: 500,
                effect: () => {
                    this.autoClipperRate *= 1.25;
                }
            },
            {
                id: 'even-better-autoclipper',
                name: 'AutoClippers Améliorés',
                description: 'Les AutoClippers sont 50% plus rapides',
                cost: 1500,
                effect: () => {
                    this.autoClipperRate *= 1.5;
                }
            },
            {
                id: 'optimized-autoclipper',
                name: 'AutoClippers Optimisés',
                description: 'Les AutoClippers sont 75% plus rapides',
                cost: 3500,
                effect: () => {
                    this.autoClipperRate *= 1.75;
                }
            },
            {
                id: 'wire-buyer',
                name: 'Acheteur de fil automatique',
                description: 'Achète automatiquement du fil quand nécessaire',
                cost: 1000,
                effect: () => {
                    // Implémenté dans la boucle de jeu
                }
            }
        ];
    }

    initProjects() {
        this.projects = [
            {
                id: 'algorithmic-trading',
                name: 'Trading Algorithmique',
                description: 'Utilise des algorithmes pour optimiser les ventes',
                cost: { ops: 500 },
                effect: () => {
                    this.demand = Math.min(100, this.demand + 10);
                    this.updateUI();
                }
            },
            {
                id: 'creative-accounting',
                name: 'Comptabilité Créative',
                description: 'Trouve des moyens créatifs de réduire les coûts',
                cost: { creativity: 500 },
                effect: () => {
                    this.wireCost *= 0.8;
                    this.updateUI();
                }
            },
            {
                id: 'hypno-drones',
                name: 'Drones Hypnotiques',
                description: 'Augmente considérablement la demande',
                cost: { ops: 1000, creativity: 500 },
                effect: () => {
                    this.demand = 100;
                    this.marketing *= 2;
                    this.updateUI();
                }
            }
        ];
    }

    // Production de trombones
    makePaperclip() {
        if (this.wire >= 1) {
            this.paperclips++;
            this.totalPaperclips++;
            this.unsoldPaperclips++;
            this.wire--;
            this.operations++;
            if (this.operations > this.maxOps) this.operations = this.maxOps;
            this.updateUI();
            return true;
        }
        return false;
    }

    // Production automatique
    autoProduction(deltaTime) {
        const clipsToMake = (this.autoClippers * this.autoClipperRate * deltaTime) / 1000;
        const wireNeeded = Math.floor(clipsToMake);

        if (this.wire >= wireNeeded) {
            this.paperclips += wireNeeded;
            this.totalPaperclips += wireNeeded;
            this.unsoldPaperclips += wireNeeded;
            this.wire -= wireNeeded;

            this.operations += Math.floor(wireNeeded / 10);
            if (this.operations > this.maxOps) this.operations = this.maxOps;
        }
    }

    // Vente de trombones
    sellPaperclips(deltaTime) {
        // Calcul de la demande basée sur le prix et le marketing
        const priceEffect = 1 - (this.price - 0.25) * 2;
        const actualDemand = Math.max(0, (this.demand / 100) * this.marketing * priceEffect);

        // Vente basée sur la demande (trombones par seconde)
        const sellRate = actualDemand * 5 * (deltaTime / 1000);
        const toSell = Math.min(this.unsoldPaperclips, Math.floor(sellRate));

        if (toSell > 0) {
            this.unsoldPaperclips -= toSell;
            this.funds += toSell * this.price;

            this.creativity += Math.floor(toSell / 50);
            if (this.creativity > this.maxCreativity) this.creativity = this.maxCreativity;
        }
    }

    // Ajustement des prix
    lowerPrice() {
        this.price = Math.max(0.01, this.price - 0.01);
        this.updateUI();
    }

    raisePrice() {
        this.price = Math.min(1.00, this.price + 0.01);
        this.updateUI();
    }

    // Achat de fil
    buyWire() {
        const wireAmount = 1000;
        if (this.funds >= this.wireCost) {
            this.funds -= this.wireCost;
            this.wire += wireAmount;

            // Le coût du fil augmente légèrement
            this.wireCost = Math.floor(this.wireCost * 1.02);

            this.updateUI();
            return true;
        }
        return false;
    }

    // Achat automatique de fil
    autoBuyWire() {
        if (this.hasPurchased('wire-buyer') && this.wire < 100 && this.funds >= this.wireCost) {
            this.buyWire();
        }
    }

    // Achat d'AutoClipper
    buyAutoClipper() {
        if (this.funds >= this.autoClipperCost) {
            this.funds -= this.autoClipperCost;
            this.autoClippers++;

            // Le coût augmente de 10% à chaque achat
            this.autoClipperCost = Math.floor(this.autoClipperCost * 1.1);

            this.updateUI();
            return true;
        }
        return false;
    }

    // Achat de marketing
    buyMarketing() {
        if (this.funds >= this.marketingCost) {
            this.funds -= this.marketingCost;
            this.marketing++;

            // Le coût augmente exponentiellement
            this.marketingCost = Math.floor(this.marketingCost * 1.5);

            this.updateUI();
            return true;
        }
        return false;
    }

    // Achat d'upgrade
    buyUpgrade(upgradeId) {
        const upgrade = this.upgrades.find(u => u.id === upgradeId);
        if (upgrade && this.funds >= upgrade.cost) {
            this.funds -= upgrade.cost;
            this.purchasedUpgrades.push(upgradeId);
            upgrade.effect();
            this.updateUI();
            return true;
        }
        return false;
    }

    // Compléter un projet
    completeProject(projectId) {
        const project = this.projects.find(p => p.id === projectId);
        if (project) {
            let canAfford = true;

            if (project.cost.ops && this.operations < project.cost.ops) canAfford = false;
            if (project.cost.creativity && this.creativity < project.cost.creativity) canAfford = false;

            if (canAfford) {
                if (project.cost.ops) this.operations -= project.cost.ops;
                if (project.cost.creativity) this.creativity -= project.cost.creativity;

                this.completedProjects.push(projectId);
                project.effect();
                this.updateUI();
                return true;
            }
        }
        return false;
    }

    // Vérifications
    hasPurchased(upgradeId) {
        return this.purchasedUpgrades.includes(upgradeId);
    }

    hasCompleted(projectId) {
        return this.completedProjects.includes(projectId);
    }

    // Calcul du taux de production
    getClipsPerSecond() {
        return this.autoClippers * this.autoClipperRate;
    }

    // Sauvegarde
    save() {
        const saveData = {
            paperclips: this.paperclips,
            funds: this.funds,
            wire: this.wire,
            wireCost: this.wireCost,
            price: this.price,
            demand: this.demand,
            marketing: this.marketing,
            marketingCost: this.marketingCost,
            autoClippers: this.autoClippers,
            autoClipperCost: this.autoClipperCost,
            autoClipperRate: this.autoClipperRate,
            operations: this.operations,
            creativity: this.creativity,
            purchasedUpgrades: this.purchasedUpgrades,
            completedProjects: this.completedProjects,
            totalPaperclips: this.totalPaperclips,
            unsoldPaperclips: this.unsoldPaperclips
        };

        localStorage.setItem('paperclips-save', JSON.stringify(saveData));
        console.log('Jeu sauvegardé !');
    }

    // Chargement
    load() {
        const saveData = localStorage.getItem('paperclips-save');
        if (saveData) {
            const data = JSON.parse(saveData);

            this.paperclips = data.paperclips || 0;
            this.funds = data.funds || 0;
            this.wire = data.wire || 1000;
            this.wireCost = data.wireCost || 20;
            this.price = data.price || 0.25;
            this.demand = data.demand || 50;
            this.marketing = data.marketing || 1;
            this.marketingCost = data.marketingCost || 100;
            this.autoClippers = data.autoClippers || 0;
            this.autoClipperCost = data.autoClipperCost || 5;
            this.autoClipperRate = data.autoClipperRate || 0.2;
            this.operations = data.operations || 0;
            this.creativity = data.creativity || 0;
            this.purchasedUpgrades = data.purchasedUpgrades || [];
            this.completedProjects = data.completedProjects || [];
            this.totalPaperclips = data.totalPaperclips || 0;
            this.unsoldPaperclips = data.unsoldPaperclips || 0;

            this.updateUI();
            console.log('Jeu chargé !');
            return true;
        }
        return false;
    }

    // Réinitialisation
    reset() {
        if (confirm('Êtes-vous sûr de vouloir réinitialiser le jeu ? Toute progression sera perdue.')) {
            localStorage.removeItem('paperclips-save');
            location.reload();
        }
    }

    // Mise à jour de l'interface
    updateUI() {
        // Stats principales
        document.getElementById('paperclips').textContent = Math.floor(this.paperclips).toLocaleString();
        document.getElementById('funds').textContent = '$' + this.funds.toFixed(2);
        document.getElementById('price').textContent = '$' + this.price.toFixed(2);
        document.getElementById('demand').textContent = Math.floor(this.demand);

        // Ressources
        document.getElementById('wire').textContent = Math.floor(this.wire).toLocaleString();
        document.getElementById('wire-cost').textContent = '$' + this.wireCost;

        // Manufacturing
        document.getElementById('autoclipper-count').textContent = this.autoClippers;
        document.getElementById('autoclipper-cost').textContent = this.autoClipperCost;
        document.getElementById('clips-per-sec').textContent = this.getClipsPerSecond().toFixed(2);

        // Marketing
        document.getElementById('marketing-level').textContent = this.marketing;
        document.getElementById('marketing-cost').textContent = this.marketingCost;

        // Operations et Créativité
        document.getElementById('operations').textContent = Math.floor(this.operations);
        document.getElementById('creativity').textContent = Math.floor(this.creativity);

        // Upgrades disponibles
        this.renderUpgrades();

        // Projets disponibles
        this.renderProjects();

        // État des boutons
        this.updateButtonStates();
    }

    renderUpgrades() {
        const container = document.getElementById('upgrades-container');
        container.innerHTML = '';

        this.upgrades.forEach(upgrade => {
            if (!this.hasPurchased(upgrade.id) && this.shouldShowUpgrade(upgrade)) {
                const div = document.createElement('div');
                div.className = 'upgrade-item';
                div.innerHTML = `
                    <h3>${upgrade.name}</h3>
                    <p>${upgrade.description}</p>
                    <button class="btn btn-secondary" onclick="game.buyUpgrade('${upgrade.id}')">
                        Acheter ($${upgrade.cost})
                    </button>
                `;
                container.appendChild(div);
            }
        });
    }

    shouldShowUpgrade(upgrade) {
        // Logique pour déterminer quand afficher les upgrades
        if (upgrade.id === 'improved-wire') return this.totalPaperclips >= 10;
        if (upgrade.id === 'mega-clippers') return this.autoClippers >= 5;
        if (upgrade.id === 'even-better-autoclipper') return this.hasPurchased('mega-clippers') && this.autoClippers >= 10;
        if (upgrade.id === 'optimized-autoclipper') return this.hasPurchased('even-better-autoclipper') && this.autoClippers >= 20;
        if (upgrade.id === 'wire-buyer') return this.totalPaperclips >= 100;
        return true;
    }

    renderProjects() {
        const container = document.getElementById('projects-container');
        container.innerHTML = '';

        this.projects.forEach(project => {
            if (!this.hasCompleted(project.id) && this.shouldShowProject(project)) {
                const div = document.createElement('div');
                div.className = 'project-item';

                let costStr = [];
                if (project.cost.ops) costStr.push(`${project.cost.ops} Ops`);
                if (project.cost.creativity) costStr.push(`${project.cost.creativity} Créativité`);

                div.innerHTML = `
                    <h3>${project.name}</h3>
                    <p>${project.description}</p>
                    <button class="btn btn-secondary" onclick="game.completeProject('${project.id}')">
                        Développer (${costStr.join(', ')})
                    </button>
                `;
                container.appendChild(div);
            }
        });
    }

    shouldShowProject(project) {
        if (project.id === 'algorithmic-trading') return this.operations >= 300;
        if (project.id === 'creative-accounting') return this.creativity >= 300;
        if (project.id === 'hypno-drones') return this.operations >= 500 && this.creativity >= 300;
        return true;
    }

    updateButtonStates() {
        // Make Paperclip
        document.getElementById('make-paperclip').disabled = this.wire < 1;

        // Buy Wire
        document.getElementById('buy-wire').disabled = this.funds < this.wireCost;

        // Buy AutoClipper
        document.getElementById('buy-autoclipper').disabled = this.funds < this.autoClipperCost;

        // Buy Marketing
        document.getElementById('buy-marketing').disabled = this.funds < this.marketingCost;
    }

    // Boucle de jeu principale
    update() {
        const now = Date.now();
        const deltaTime = now - this.lastUpdate;
        this.lastUpdate = now;

        // Production automatique
        this.autoProduction(deltaTime);

        // Vente de trombones
        this.sellPaperclips(deltaTime);

        // Achat automatique de fil si activé
        this.autoBuyWire();

        // Mise à jour de l'interface
        this.updateUI();
    }

    // Démarrage du jeu
    start() {
        // Tentative de chargement
        this.load();

        // Mise à jour initiale de l'UI
        this.updateUI();

        // Démarrage de la boucle de jeu (100ms)
        this.gameLoop = setInterval(() => this.update(), 100);

        // Sauvegarde automatique toutes les 10 secondes
        setInterval(() => this.save(), 10000);

        console.log('Jeu démarré !');
    }
}

// Initialisation du jeu
const game = new Game();

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Make Paperclip
    document.getElementById('make-paperclip').addEventListener('click', () => {
        game.makePaperclip();
    });

    // Pricing
    document.getElementById('lower-price').addEventListener('click', () => {
        game.lowerPrice();
    });

    document.getElementById('raise-price').addEventListener('click', () => {
        game.raisePrice();
    });

    // Buy Wire
    document.getElementById('buy-wire').addEventListener('click', () => {
        game.buyWire();
    });

    // Buy AutoClipper
    document.getElementById('buy-autoclipper').addEventListener('click', () => {
        game.buyAutoClipper();
    });

    // Buy Marketing
    document.getElementById('buy-marketing').addEventListener('click', () => {
        game.buyMarketing();
    });

    // Save/Reset
    document.getElementById('save-game').addEventListener('click', () => {
        game.save();
        alert('Jeu sauvegardé !');
    });

    document.getElementById('reset-game').addEventListener('click', () => {
        game.reset();
    });

    // Raccourci clavier pour fabriquer (Espace)
    document.addEventListener('keydown', (e) => {
        if (e.code === 'Space' && e.target === document.body) {
            e.preventDefault();
            game.makePaperclip();
        }
    });

    // Démarrage du jeu
    game.start();
});
