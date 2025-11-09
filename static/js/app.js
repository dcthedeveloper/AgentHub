/**
 * AgentHub - Award-Winning Interactive UI
 * Real-time data updates and smooth animations
 */

// ============================================================================
// State Management
// ============================================================================

const state = {
    theme: localStorage.getItem('theme') || 'light',
    agents: [],
    blockchain: [],
    stats: {},
    selectedAgent: null,
    filters: {
        search: '',
        skill: 'all',
        sortBy: 'reputation'
    }
};

// ============================================================================
// API Service
// ============================================================================

const API = {
    baseURL: '',
    
    async get(endpoint) {
        const response = await fetch(`${this.baseURL}/api${endpoint}`);
        if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
        return response.json();
    },
    
    async post(endpoint, data) {
        const response = await fetch(`${this.baseURL}/api${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
        return response.json();
    },
    
    // Fetch all data
    async fetchStats() {
        return this.get('/stats');
    },
    
    async fetchAgents() {
        return this.get('/agents');
    },
    
    async fetchAgent(id) {
        return this.get(`/agents/${id}`);
    },
    
    async fetchBlockchain() {
        return this.get('/blockchain');
    },
    
    async fetchValidatorStats() {
        return this.get('/validator/stats');
    }
};

// ============================================================================
// UI Components
// ============================================================================

const UI = {
    // Update stats in hero section
    updateStats(stats) {
        document.getElementById('totalAgents').textContent = stats.total_agents;
        document.getElementById('totalValue').innerHTML = `${stats.total_value} <span class="stat-unit">tokens</span>`;
        document.getElementById('avgQuality').innerHTML = `${stats.avg_quality_score}<span class="stat-unit">/100</span>`;
        document.getElementById('totalBlocks').textContent = stats.total_blocks;
        
        // Update blockchain status indicator
        const statusIndicator = document.querySelector('.status-indicator');
        if (stats.blockchain_valid) {
            statusIndicator.style.background = 'var(--color-success)';
        } else {
            statusIndicator.style.background = 'var(--color-error)';
        }
    },
    
    // Render agent cards
    renderAgents(agents, filters) {
        const container = document.getElementById('agentsGrid');
        
        // Filter agents
        let filtered = agents.filter(agent => {
            // Search filter
            if (filters.search && !agent.id.toLowerCase().includes(filters.search.toLowerCase()) &&
                !agent.skills.some(skill => skill.toLowerCase().includes(filters.search.toLowerCase()))) {
                return false;
            }
            
            // Skill filter
            if (filters.skill !== 'all' && !agent.skills.includes(filters.skill)) {
                return false;
            }
            
            // Only show sellers
            return agent.type === 'seller';
        });
        
        // Sort agents
        filtered.sort((a, b) => {
            switch (filters.sortBy) {
                case 'reputation':
                    return b.reputation - a.reputation;
                case 'price':
                    const aPrice = Object.values(a.pricing)[0] || Infinity;
                    const bPrice = Object.values(b.pricing)[0] || Infinity;
                    return aPrice - bPrice;
                case 'completed':
                    return b.jobs_completed - a.jobs_completed;
                default:
                    return 0;
            }
        });
        
        container.innerHTML = filtered.map(agent => this.createAgentCard(agent)).join('');
        
        // Add click handlers
        container.querySelectorAll('.agent-card').forEach(card => {
            card.addEventListener('click', () => {
                this.showAgentModal(card.dataset.agentId);
            });
            
            // Keyboard accessibility
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.showAgentModal(card.dataset.agentId);
                }
            });
        });
    },
    
    createAgentCard(agent) {
        const initials = agent.id.substring(0, 2).toUpperCase();
        const stars = '★'.repeat(Math.floor(agent.reputation)) + '☆'.repeat(5 - Math.floor(agent.reputation));
        const skills = agent.skills.map(skill => 
            `<span class="skill-tag">${skill.replace('_', ' ')}</span>`
        ).join('');
        
        const primarySkill = agent.skills[0] || 'service';
        const price = agent.pricing[primarySkill] || 0;
        
        return `
            <div class="agent-card" data-agent-id="${agent.id}" tabindex="0" role="button" aria-label="View details for ${agent.id}">
                <div class="agent-header">
                    <div class="agent-avatar">${initials}</div>
                    ${agent.available ? '<div class="agent-status">Available</div>' : ''}
                </div>
                
                <div>
                    <h3 class="agent-name">${agent.id}</h3>
                    <p class="agent-type">${agent.type}</p>
                </div>
                
                <div class="agent-reputation">
                    <span class="reputation-stars">${stars}</span>
                    <span class="reputation-score">${agent.reputation.toFixed(1)}</span>
                    <span class="reputation-count">(${agent.jobs_completed} jobs)</span>
                </div>
                
                <div class="agent-skills">
                    ${skills}
                </div>
                
                <div class="agent-stats">
                    <div class="agent-stat">
                        <div class="agent-stat-value">${agent.jobs_completed}</div>
                        <div class="agent-stat-label">Completed</div>
                    </div>
                    <div class="agent-stat">
                        <div class="agent-stat-value">${agent.total_earned}</div>
                        <div class="agent-stat-label">Earned</div>
                    </div>
                </div>
                
                <div class="agent-price">
                    <span class="price-label">Starting at</span>
                    <span class="price-value">
                        ${price} <span class="price-unit">tokens</span>
                    </span>
                </div>
            </div>
        `;
    },
    
    // Show agent detail modal
    async showAgentModal(agentId) {
        try {
            const agent = await API.fetchAgent(agentId);
            const modal = document.getElementById('agentModal');
            const modalBody = document.getElementById('modalBody');
            
            const stars = '★'.repeat(Math.floor(agent.reputation)) + '☆'.repeat(5 - Math.floor(agent.reputation));
            const initials = agent.id.substring(0, 2).toUpperCase();
            
            // Render pricing table
            const pricingRows = Object.entries(agent.pricing || {}).map(([skill, price]) => `
                <tr>
                    <td>${skill.replace('_', ' ')}</td>
                    <td><strong>${price} tokens</strong></td>
                </tr>
            `).join('');
            
            // Render transaction history
            const transactions = agent.transactions.slice(0, 10).map(tx => `
                <div class="activity-item">
                    <div class="activity-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <circle cx="12" cy="12" r="10"/>
                            <polyline points="12 6 12 12 16 14"/>
                        </svg>
                    </div>
                    <div class="activity-content">
                        <div class="activity-title">${tx.type}</div>
                        <div class="activity-description">
                            ${tx.job || 'N/A'} • ${tx.amount} tokens
                            ${tx.quality_score ? `• Quality: ${tx.quality_score}/100` : ''}
                        </div>
                        <div class="activity-time">${new Date(tx.timestamp).toLocaleString()}</div>
                    </div>
                </div>
            `).join('');
            
            modalBody.innerHTML = `
                <div style="display: flex; gap: 2rem; margin-bottom: 2rem;">
                    <div class="agent-avatar" style="width: 80px; height: 80px; font-size: 2rem;">
                        ${initials}
                    </div>
                    <div style="flex: 1;">
                        <h2 style="margin-bottom: 0.5rem;">${agent.id}</h2>
                        <p style="color: var(--color-text-secondary); margin-bottom: 1rem;">${agent.type.toUpperCase()}</p>
                        <div class="agent-reputation">
                            <span class="reputation-stars">${stars}</span>
                            <span class="reputation-score">${agent.reputation.toFixed(2)}</span>
                            <span class="reputation-count">(${agent.jobs_completed} jobs)</span>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 2rem; font-weight: 700; color: var(--color-primary);">
                            ${agent.balance} <span style="font-size: 1rem; color: var(--color-text-tertiary);">tokens</span>
                        </div>
                        <div style="color: var(--color-text-secondary);">Wallet Balance</div>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem;">
                    <div class="stat-card glass-card" style="padding: 1rem;">
                        <div style="font-size: 1.5rem; font-weight: 700;">${agent.jobs_completed}</div>
                        <div style="font-size: 0.75rem; color: var(--color-text-secondary);">Jobs Done</div>
                    </div>
                    <div class="stat-card glass-card" style="padding: 1rem;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: var(--color-success);">
                            ${agent.total_earned}
                        </div>
                        <div style="font-size: 0.75rem; color: var(--color-text-secondary);">Total Earned</div>
                    </div>
                    <div class="stat-card glass-card" style="padding: 1rem;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: var(--color-error);">
                            ${agent.total_spent}
                        </div>
                        <div style="font-size: 0.75rem; color: var(--color-text-secondary);">Total Spent</div>
                    </div>
                    <div class="stat-card glass-card" style="padding: 1rem;">
                        <div style="font-size: 1.5rem; font-weight: 700;">${agent.skills.length}</div>
                        <div style="font-size: 0.75rem; color: var(--color-text-secondary);">Skills</div>
                    </div>
                </div>
                
                ${pricingRows ? `
                    <div style="margin-bottom: 2rem;">
                        <h3 style="margin-bottom: 1rem;">Pricing</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <thead>
                                <tr style="border-bottom: 2px solid var(--color-border);">
                                    <th style="padding: 0.75rem; text-align: left;">Service</th>
                                    <th style="padding: 0.75rem; text-align: right;">Price</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${pricingRows}
                            </tbody>
                        </table>
                    </div>
                ` : ''}
                
                <div>
                    <h3 style="margin-bottom: 1rem;">Transaction History</h3>
                    <div class="activity-feed" style="max-height: 400px;">
                        ${transactions || '<p style="color: var(--color-text-secondary);">No transactions yet</p>'}
                    </div>
                </div>
            `;
            
            modal.classList.add('active');
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
            
            // Focus the close button for keyboard accessibility
            setTimeout(() => {
                closeModal.focus();
            }, 100);
        } catch (error) {
            console.error('Error loading agent details:', error);
        }
    },
    
    // Render blockchain
    renderBlockchain(blockchain) {
        const container = document.getElementById('blockchainContainer');
        
        // Show latest 10 blocks
        const blocks = blockchain.chain.slice(-10).reverse();
        
        container.innerHTML = blocks.map(block => {
            const data = block.data;
            const dataRows = Object.entries(data).map(([key, value]) => `
                <div class="block-data-row">
                    <span class="block-data-key">${key}:</span>
                    <span class="block-data-value">${typeof value === 'object' ? JSON.stringify(value) : value}</span>
                </div>
            `).join('');
            
            return `
                <div class="blockchain-block">
                    <div class="block-header">
                        <div class="block-number">Block #${block.index}</div>
                        <div class="block-time">${new Date(block.timestamp).toLocaleString()}</div>
                    </div>
                    <div class="block-hash">
                        Hash: ${block.hash}
                    </div>
                    <div class="block-data">
                        ${dataRows}
                    </div>
                </div>
            `;
        }).join('');
        
        // Update blockchain status badge
        const badge = document.getElementById('blockchainValidBadge');
        if (blockchain.valid) {
            badge.classList.add('valid');
            badge.classList.remove('invalid');
        } else {
            badge.classList.add('invalid');
            badge.classList.remove('valid');
        }
    },
    
    // Render leaderboard
    renderLeaderboard(agents) {
        const container = document.getElementById('leaderboard');
        
        // Sort by total earned
        const topAgents = [...agents]
            .filter(a => a.type === 'seller')
            .sort((a, b) => b.total_earned - a.total_earned)
            .slice(0, 5);
        
        container.innerHTML = topAgents.map((agent, index) => `
            <div class="leaderboard-item">
                <div class="leaderboard-rank">${index + 1}</div>
                <div class="leaderboard-info">
                    <div class="leaderboard-name">${agent.id}</div>
                    <div class="leaderboard-stat">
                        ${agent.jobs_completed} jobs • ${agent.reputation.toFixed(1)}★
                    </div>
                </div>
                <div class="leaderboard-value">${agent.total_earned} tokens</div>
            </div>
        `).join('');
    },
    
    // Render activity feed
    renderActivityFeed(blockchain) {
        const container = document.getElementById('activityFeed');
        
        // Get latest transactions
        const activities = blockchain.chain.slice(-15).reverse()
            .filter(block => block.data.type !== 'genesis')
            .map(block => {
                const data = block.data;
                let icon, title, description;
                
                if (data.type === 'contract_created') {
                    icon = '<path d="M12 2L2 7L12 12L22 7L12 2Z"/>';
                    title = 'Contract Created';
                    description = `${data.buyer} → ${data.seller} • ${data.amount} tokens`;
                } else if (data.type === 'payment_released') {
                    icon = '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>';
                    title = 'Payment Released';
                    description = `${data.amount} tokens • Quality: ${data.quality_score}/100`;
                }
                
                return `
                    <div class="activity-item">
                        <div class="activity-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                ${icon}
                            </svg>
                        </div>
                        <div class="activity-content">
                            <div class="activity-title">${title}</div>
                            <div class="activity-description">${description}</div>
                            <div class="activity-time">${new Date(block.timestamp).toLocaleString()}</div>
                        </div>
                    </div>
                `;
            }).join('');
        
        container.innerHTML = activities || '<p style="color: var(--color-text-secondary);">No activity yet</p>';
    }
};

// ============================================================================
// Event Handlers
// ============================================================================

function initializeEventHandlers() {
    // Theme toggle
    const themeToggle = document.getElementById('themeToggle');
    themeToggle.addEventListener('click', () => {
        state.theme = state.theme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', state.theme);
        localStorage.setItem('theme', state.theme);
    });
    
    // Set initial theme
    document.documentElement.setAttribute('data-theme', state.theme);
    
    // Run Demo Transaction button
    const runDemoBtn = document.getElementById('runDemoBtn');
    runDemoBtn.addEventListener('click', () => {
        // Open demo modal instead of running silently
        const demoModal = document.getElementById('demoModal');
        demoModal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Reset demo state
        resetDemoSteps();
    });
    
    // Start Demo button (inside modal)
    const startDemoBtn = document.getElementById('startDemoBtn');
    startDemoBtn.addEventListener('click', async () => {
        startDemoBtn.disabled = true;
        startDemoBtn.textContent = 'Running...';
        
        await runDemoTransaction();
        
        startDemoBtn.classList.add('hidden');
        document.getElementById('viewResultsBtn').classList.remove('hidden');
    });
    
    // View Results button
    const viewResultsBtn = document.getElementById('viewResultsBtn');
    viewResultsBtn.addEventListener('click', () => {
        // Close demo modal
        document.getElementById('demoModal').classList.remove('active');
        document.body.style.overflow = '';
        
        // Scroll to blockchain section
        document.getElementById('blockchain').scrollIntoView({ behavior: 'smooth' });
        
        // Show success toast
        showToast('📊 Check out the full blockchain explorer below!', 'success');
    });
    
    // Close demo modal
    const closeDemoModal = document.getElementById('closeDemoModal');
    const demoModal = document.getElementById('demoModal');
    const demoOverlay = demoModal.querySelector('.modal-overlay');
    
    closeDemoModal.addEventListener('click', () => {
        demoModal.classList.remove('active');
        document.body.style.overflow = '';
        resetDemoSteps();
    });
    
    demoOverlay.addEventListener('click', () => {
        demoModal.classList.remove('active');
        document.body.style.overflow = '';
        resetDemoSteps();
    });
    
    // Explore Agents button
    const exploreBtn = document.getElementById('exploreAgentsBtn');
    exploreBtn.addEventListener('click', () => {
        document.getElementById('marketplace').scrollIntoView({ behavior: 'smooth' });
    });
    
    // Watch Demo button
    const watchDemoBtn = document.getElementById('watchDemoBtn');
    watchDemoBtn.addEventListener('click', () => {
        const demoModal = document.getElementById('demoModal');
        demoModal.classList.add('active');
        document.body.style.overflow = 'hidden';
        resetDemoSteps();
    });
    
    // Search filter
    const searchInput = document.getElementById('agentSearch');
    searchInput.addEventListener('input', (e) => {
        state.filters.search = e.target.value;
        UI.renderAgents(state.agents, state.filters);
    });
    
    // Skill filter
    const skillFilter = document.getElementById('skillFilter');
    skillFilter.addEventListener('change', (e) => {
        state.filters.skill = e.target.value;
        UI.renderAgents(state.agents, state.filters);
    });
    
    // Sort filter
    const sortBy = document.getElementById('sortBy');
    sortBy.addEventListener('change', (e) => {
        state.filters.sortBy = e.target.value;
        UI.renderAgents(state.agents, state.filters);
    });
    
    // Modal close
    const closeModal = document.getElementById('closeModal');
    const modal = document.getElementById('agentModal');
    const modalOverlay = modal.querySelector('.modal-overlay');
    
    const closeModalHandler = () => {
        modal.classList.remove('active');
        document.body.style.overflow = ''; // Re-enable scrolling
    };
    
    closeModal.addEventListener('click', closeModalHandler);
    modalOverlay.addEventListener('click', closeModalHandler);
    
    // Keyboard accessibility - ESC to close modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeModalHandler();
        }
    });
    
    // Smooth scroll for navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector(link.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
    
    // Dynamic active nav state based on scroll position
    initializeScrollSpy();
}

// ============================================================================
// Scroll Spy for Active Navigation
// ============================================================================

function initializeScrollSpy() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');
    
    const observerOptions = {
        root: null,
        rootMargin: '-100px 0px -60% 0px', // Account for navbar and show active when section is prominent
        threshold: 0
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const sectionId = entry.target.getAttribute('id');
                
                // Remove active class from all nav links
                navLinks.forEach(link => {
                    link.classList.remove('active');
                });
                
                // Add active class to matching nav link
                const activeLink = document.querySelector(`.nav-link[href="#${sectionId}"]`);
                if (activeLink) {
                    activeLink.classList.add('active');
                }
            }
        });
    }, observerOptions);
    
    // Observe all sections
    sections.forEach(section => {
        observer.observe(section);
    });
}

// ============================================================================
// Data Fetching & Updates
// ============================================================================

async function fetchAndUpdateData() {
    try {
        // Fetch all data in parallel
        const [stats, agentsData, blockchain] = await Promise.all([
            API.fetchStats(),
            API.fetchAgents(),
            API.fetchBlockchain()
        ]);
        
        // Update state
        state.stats = stats;
        state.agents = agentsData.agents;
        state.blockchain = blockchain;
        
        // Update UI
        UI.updateStats(stats);
        UI.renderAgents(state.agents, state.filters);
        UI.renderBlockchain(blockchain);
        UI.renderLeaderboard(state.agents);
        UI.renderActivityFeed(blockchain);
        
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Auto-refresh data every 5 seconds
function startAutoRefresh() {
    setInterval(fetchAndUpdateData, 5000);
}

// ============================================================================
// Initialize Application
// ============================================================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 AgentHub UI Initializing...');
    
    // Initialize event handlers
    initializeEventHandlers();
    
    // Initial data fetch
    await fetchAndUpdateData();
    
    // Start auto-refresh
    startAutoRefresh();
    
    console.log('✅ AgentHub UI Ready');
});

// ============================================================================
// Number Animation Utility
// ============================================================================

function animateValue(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.round(current);
    }, 16);
}

// ============================================================================
// Toast Notifications
// ============================================================================

function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;
        document.body.appendChild(container);
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.style.cssText = `
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#6366f1'};
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        font-family: var(--font-sans);
        font-weight: 600;
        font-size: 14px;
        animation: slideIn 0.3s ease-out;
        max-width: 400px;
    `;
    toast.textContent = message;
    
    // Add animation keyframes if not exists
    if (!document.getElementById('toastStyles')) {
        const style = document.createElement('style');
        style.id = 'toastStyles';
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    container.appendChild(toast);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============================================================================
// Demo Transaction Flow
// ============================================================================

function resetDemoSteps() {
    const steps = ['demoStep1', 'demoStep2', 'demoStep3', 'demoStep4'];
    steps.forEach(stepId => {
        const step = document.getElementById(stepId);
        step.classList.remove('active', 'completed', 'error');
        const status = step.querySelector('.demo-step-status');
        status.textContent = '⏳ Waiting';
    });
    
    const startBtn = document.getElementById('startDemoBtn');
    startBtn.disabled = false;
    startBtn.textContent = 'Start Demo Transaction';
    startBtn.classList.remove('hidden');
    
    document.getElementById('viewResultsBtn').classList.add('hidden');
}

function updateDemoStep(stepNumber, status, message) {
    const step = document.getElementById(`demoStep${stepNumber}`);
    const statusEl = step.querySelector('.demo-step-status');
    const descriptionEl = step.querySelector('.demo-step-description');
    
    // Remove all status classes
    step.classList.remove('active', 'completed', 'error');
    
    if (status === 'active') {
        step.classList.add('active');
        statusEl.textContent = '⚡ In Progress...';
        if (message) descriptionEl.textContent = message;
    } else if (status === 'completed') {
        step.classList.add('completed');
        statusEl.textContent = '✅ Completed';
        if (message) descriptionEl.textContent = message;
    } else if (status === 'error') {
        step.classList.add('error');
        statusEl.textContent = '❌ Failed';
        if (message) descriptionEl.textContent = message;
    }
}

async function runDemoTransaction() {
    try {
        // Hide blockchain preview initially
        document.getElementById('demoBlockchainPreview').classList.add('hidden');
        
        // Step 1: Posting Job
        updateDemoStep(1, 'active', 'ResearchBot posting a data analysis job...');
        await sleep(1500);
        
        // Step 2: Collecting Bids
        updateDemoStep(1, 'completed', 'Job posted successfully!');
        updateDemoStep(2, 'active', 'Agents submitting bids based on reputation and pricing...');
        await sleep(2000);
        
        // Step 3: Creating Smart Contract
        updateDemoStep(2, 'completed', 'Received multiple competitive bids!');
        updateDemoStep(3, 'active', 'Selecting winner and creating escrow contract...');
        await sleep(1500);
        
        // Step 4: Execute transaction
        updateDemoStep(3, 'completed', 'Smart contract created, funds in escrow!');
        updateDemoStep(4, 'active', 'Running AI validation and releasing payment...');
        
        // Actually run the demo transaction
        const response = await API.post('/demo/run', {});
        
        if (response.success) {
            await sleep(1500);
            updateDemoStep(4, 'completed', 'Work validated! Payment released to seller.');
            
            // Refresh data to get latest blockchain
            await fetchAndUpdateData();
            
            // Show the new blockchain block
            await sleep(500);
            showDemoBlockchainBlock();
            
            showToast('🎉 Transaction complete! Block added to blockchain.', 'success');
        } else {
            updateDemoStep(4, 'error', 'Transaction failed: ' + response.error);
            showToast('❌ Demo failed: ' + response.error, 'error');
        }
        
    } catch (error) {
        console.error('Demo error:', error);
        showToast('❌ Error: ' + error.message, 'error');
        
        // Mark current step as error
        for (let i = 1; i <= 4; i++) {
            const step = document.getElementById(`demoStep${i}`);
            if (step.classList.contains('active')) {
                updateDemoStep(i, 'error', 'An error occurred');
                break;
            }
        }
    }
}

function showDemoBlockchainBlock() {
    const preview = document.getElementById('demoBlockchainPreview');
    const blockContainer = document.getElementById('demoNewBlock');
    
    // Get the latest block from state
    if (state.blockchain && state.blockchain.chain && state.blockchain.chain.length > 0) {
        const latestBlock = state.blockchain.chain[state.blockchain.chain.length - 1];
        
        // Render the block
        const data = latestBlock.data;
        const dataRows = Object.entries(data).map(([key, value]) => `
            <div class="block-data-row">
                <span class="block-data-key">${key}:</span>
                <span class="block-data-value">${typeof value === 'object' ? JSON.stringify(value) : value}</span>
            </div>
        `).join('');
        
        blockContainer.innerHTML = `
            <div class="block-header">
                <div class="block-number">Block #${latestBlock.index}</div>
                <div class="block-time">${new Date(latestBlock.timestamp).toLocaleString()}</div>
            </div>
            <div class="block-hash">
                Hash: ${latestBlock.hash}
            </div>
            <div class="block-data">
                ${dataRows}
            </div>
        `;
        
        // Show the preview with animation
        preview.classList.remove('hidden');
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
