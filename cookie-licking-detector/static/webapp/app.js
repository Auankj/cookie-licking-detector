// ========================================
// Cookie-Licking Detector - Web App
// Main Application Logic
// ========================================

const API_BASE_URL = window.location.origin + '/api/v1';
let authToken = localStorage.getItem('authToken');
let currentUser = null;

// ========================================
// Initialization
// ========================================
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkAuthentication();
    initializeApp();
});

function initializeApp() {
    // Only load dashboard if authenticated
    if (authToken) {
        loadDashboard();
    }
    
    // Setup auto-refresh
    setInterval(() => {
        if (authToken) {
            const activePage = document.querySelector('.page.active');
            if (activePage && activePage.id === 'dashboard-page') {
                loadDashboard();
            }
        }
    }, 30000); // Refresh every 30 seconds
}

// ========================================
// Event Listeners
// ========================================
function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = e.target.dataset.page;
            navigateToPage(page);
        });
    });
    
    // Login/Logout
    document.getElementById('loginBtn').addEventListener('click', () => {
        showModal('loginModal');
    });
    
    document.getElementById('logoutBtn').addEventListener('click', logout);
    
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    
    // Add Repository
    const addRepoBtn = document.getElementById('addRepoBtn');
    if (addRepoBtn) {
        addRepoBtn.addEventListener('click', () => {
            if (!authToken) {
                showToast('Please login to add repositories', 'info');
                showModal('loginModal');
            } else {
                showModal('addRepoModal');
            }
        });
    }
    
    document.getElementById('addRepoForm')?.addEventListener('submit', handleAddRepository);
    
    // Modal close buttons
    document.querySelectorAll('.close').forEach(btn => {
        btn.addEventListener('click', () => {
            hideAllModals();
        });
    });
    
    // Close modal on outside click
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            hideAllModals();
        }
    });
    
    // Filters
    document.getElementById('repoSearch')?.addEventListener('input', filterRepositories);
    document.getElementById('repoFilter')?.addEventListener('change', filterRepositories);
    document.getElementById('claimSearch')?.addEventListener('input', filterClaims);
    document.getElementById('claimStatusFilter')?.addEventListener('change', filterClaims);
}

// ========================================
// Authentication
// ========================================
function checkAuthentication() {
    if (authToken) {
        fetchCurrentUser();
    } else {
        updateAuthUI(false);
    }
}

async function fetchCurrentUser() {
    try {
        const response = await apiRequest('/users/me');
        currentUser = response;
        updateAuthUI(true);
    } catch (error) {
        console.error('Authentication check failed:', error);
        authToken = null;
        localStorage.removeItem('authToken');
        updateAuthUI(false);
    }
}

function updateAuthUI(isAuthenticated) {
    const loginBtn = document.getElementById('loginBtn');
    const userMenu = document.getElementById('userMenu');
    const username = document.getElementById('username');
    
    if (isAuthenticated && currentUser) {
        loginBtn.style.display = 'none';
        userMenu.style.display = 'flex';
        username.textContent = currentUser.username || currentUser.github_username || 'User';
    } else {
        loginBtn.style.display = 'block';
        userMenu.style.display = 'none';
    }
}

async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
        
        if (!response.ok) {
            throw new Error('Invalid email or password');
        }
        
        const data = await response.json();
        authToken = data.access_token;
        localStorage.setItem('authToken', authToken);
        
        await fetchCurrentUser();
        hideAllModals();
        showToast('Login successful!', 'success');
        loadDashboard();
        
    } catch (error) {
        console.error('Login error:', error);
        showError('loginError', 'Invalid username or password');
    } finally {
        hideLoading();
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    updateAuthUI(false);
    showToast('Logged out successfully', 'info');
}

// ========================================
// Navigation
// ========================================
function navigateToPage(pageName) {
    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.page === pageName) {
            link.classList.add('active');
        }
    });
    
    // Show active page
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    const targetPage = document.getElementById(`${pageName}-page`);
    if (targetPage) {
        targetPage.classList.add('active');
        
        // Load page-specific data
        switch(pageName) {
            case 'dashboard':
                loadDashboard();
                break;
            case 'repositories':
                loadRepositories();
                break;
            case 'claims':
                loadClaims();
                break;
            case 'analytics':
                loadAnalytics();
                break;
        }
    }
}

// ========================================
// Dashboard
// ========================================
async function loadDashboard() {
    showLoading();
    
    try {
        const stats = await apiRequest('/dashboard/stats');
        updateDashboardStats(stats);
        
        // Load recent activity
        const activity = await apiRequest('/dashboard/activity');
        updateRecentActivity(activity);
        
    } catch (error) {
        console.error('Failed to load dashboard:', error);
        showToast('Failed to load dashboard data', 'error');
    } finally {
        hideLoading();
    }
}

function updateDashboardStats(stats) {
    document.getElementById('totalRepos').textContent = stats.total_repositories || 0;
    document.getElementById('activeClaims').textContent = stats.active_claims || 0;
    document.getElementById('completedClaims').textContent = stats.completed_claims || 0;
    document.getElementById('totalNudges').textContent = stats.total_nudges_sent || 0;
    
    // Update charts (placeholder for now)
    updateCharts(stats);
}

function updateCharts(stats) {
    // Placeholder for chart rendering
    const claimsTrendChart = document.getElementById('claimsTrendChart');
    const claimStatusChart = document.getElementById('claimStatusChart');
    
    claimsTrendChart.innerHTML = '<p>📊 Claims trend chart will be displayed here</p>';
    claimStatusChart.innerHTML = `
        <div style="text-align: left;">
            <p>✅ Completed: ${stats.completed_claims || 0}</p>
            <p>🎯 Active: ${stats.active_claims || 0}</p>
            <p>🔄 Released: ${stats.released_claims || 0}</p>
            <p>⏱️ Expired: ${stats.expired_claims || 0}</p>
        </div>
    `;
}

function updateRecentActivity(activity) {
    const activityList = document.getElementById('recentActivity');
    
    if (!activity || activity.length === 0) {
        activityList.innerHTML = '<p style="color: var(--text-secondary);">No recent activity</p>';
        return;
    }
    
    activityList.innerHTML = activity.slice(0, 10).map(item => `
        <div class="activity-item">
            <div class="activity-icon">${getActivityIcon(item.type)}</div>
            <div class="activity-content">
                <div class="activity-title">${item.description}</div>
                <div class="activity-meta">
                    ${item.user || 'System'} • ${formatDate(item.timestamp)}
                </div>
            </div>
        </div>
    `).join('');
}

function getActivityIcon(type) {
    const icons = {
        'claim': '🎯',
        'release': '🔄',
        'complete': '✅',
        'nudge': '🔔',
        'repository': '📦'
    };
    return icons[type] || '📌';
}

// ========================================
// Repositories
// ========================================
async function loadRepositories() {
    showLoading();
    
    try {
        const repositories = await apiRequest('/repositories');
        displayRepositories(repositories);
    } catch (error) {
        console.error('Failed to load repositories:', error);
        showToast('Failed to load repositories', 'error');
    } finally {
        hideLoading();
    }
}

function displayRepositories(repositories) {
    const reposList = document.getElementById('repositoriesList');
    
    if (!repositories || repositories.length === 0) {
        reposList.innerHTML = '<p style="color: var(--text-secondary);">No repositories found</p>';
        return;
    }
    
    reposList.innerHTML = repositories.map(repo => `
        <div class="repo-card" data-repo-id="${repo.id}">
            <div class="repo-header">
                <div>
                    <div class="repo-title">${repo.owner_name}/${repo.name}</div>
                    <div style="color: var(--text-secondary); font-size: 0.9rem;">
                        ${repo.description || 'No description'}
                    </div>
                </div>
                <span class="repo-badge badge-${repo.is_monitored ? 'monitored' : 'inactive'}">
                    ${repo.is_monitored ? 'Monitored' : 'Inactive'}
                </span>
            </div>
            <div class="repo-stats">
                <div class="repo-stat">
                    <strong>${repo.active_claims_count || 0}</strong> Active Claims
                </div>
                <div class="repo-stat">
                    <strong>${repo.total_issues || 0}</strong> Total Issues
                </div>
                <div class="repo-stat">
                    <strong>${repo.grace_period_days || 7}</strong> Days Grace Period
                </div>
                <div class="repo-stat">
                    <strong>${repo.nudge_count || 2}</strong> Nudges
                </div>
            </div>
        </div>
    `).join('');
}

function filterRepositories() {
    const search = document.getElementById('repoSearch').value.toLowerCase();
    const filter = document.getElementById('repoFilter').value;
    
    document.querySelectorAll('.repo-card').forEach(card => {
        const title = card.querySelector('.repo-title').textContent.toLowerCase();
        const isMonitored = card.querySelector('.badge-monitored') !== null;
        
        let matchesSearch = title.includes(search);
        let matchesFilter = filter === 'all' || 
            (filter === 'monitored' && isMonitored) ||
            (filter === 'inactive' && !isMonitored);
        
        card.style.display = matchesSearch && matchesFilter ? 'block' : 'none';
    });
}

async function handleAddRepository(e) {
    e.preventDefault();
    
    // Check if user is logged in
    if (!authToken) {
        hideAllModals();
        showToast('Please login to add repositories', 'error');
        setTimeout(() => showModal('loginModal'), 500);
        return;
    }
    
    const owner = document.getElementById('repoOwner').value;
    const name = document.getElementById('repoName').value;
    const gracePeriod = parseInt(document.getElementById('gracePeriod').value);
    
    showLoading();
    
    try {
        await apiRequest('/repositories', 'POST', {
            owner,
            name,
            grace_period_days: gracePeriod
        });
        
        hideAllModals();
        showToast('Repository added successfully!', 'success');
        loadRepositories();
        
        // Clear form
        document.getElementById('addRepoForm').reset();
        
    } catch (error) {
        console.error('Failed to add repository:', error);
        const errorMsg = error.message.includes('Authentication required') 
            ? 'Please login to add repositories' 
            : error.message.includes('already registered')
            ? 'This repository is already registered'
            : 'Failed to add repository. Please check the owner and name.';
        showError('addRepoError', errorMsg);
    } finally {
        hideLoading();
    }
}

// ========================================
// Claims
// ========================================
async function loadClaims() {
    showLoading();
    
    try {
        const claims = await apiRequest('/claims');
        displayClaims(claims);
    } catch (error) {
        console.error('Failed to load claims:', error);
        showToast('Failed to load claims', 'error');
    } finally {
        hideLoading();
    }
}

function displayClaims(claims) {
    const claimsList = document.getElementById('claimsList');
    
    if (!claims || claims.length === 0) {
        claimsList.innerHTML = '<p style="color: var(--text-secondary);">No claims found</p>';
        return;
    }
    
    claimsList.innerHTML = claims.map(claim => `
        <div class="claim-card" data-claim-id="${claim.id}">
            <div class="claim-header">
                <div>
                    <div class="claim-title">
                        #${claim.issue_number || claim.issue?.github_issue_number} - ${claim.issue?.title || 'Issue'}
                    </div>
                    <div class="claim-repo">
                        ${claim.repository || claim.issue?.repository?.owner}/${claim.issue?.repository?.name}
                    </div>
                </div>
                <span class="claim-status status-${claim.status.toLowerCase()}">
                    ${claim.status}
                </span>
            </div>
            <div class="claim-meta">
                <span>👤 ${claim.github_username}</span>
                <span>📅 Claimed ${formatDate(claim.claim_timestamp)}</span>
                <span>🎯 ${claim.confidence_score}% confidence</span>
            </div>
        </div>
    `).join('');
}

function filterClaims() {
    const search = document.getElementById('claimSearch').value.toLowerCase();
    const statusFilter = document.getElementById('claimStatusFilter').value;
    
    document.querySelectorAll('.claim-card').forEach(card => {
        const title = card.querySelector('.claim-title').textContent.toLowerCase();
        const status = card.querySelector('.claim-status').textContent.trim().toLowerCase();
        
        let matchesSearch = title.includes(search);
        let matchesFilter = statusFilter === 'all' || status === statusFilter;
        
        card.style.display = matchesSearch && matchesFilter ? 'block' : 'none';
    });
}

// ========================================
// Analytics
// ========================================
async function loadAnalytics() {
    showLoading();
    
    try {
        const analytics = await apiRequest('/dashboard/analytics');
        updateAnalytics(analytics);
    } catch (error) {
        console.error('Failed to load analytics:', error);
        showToast('Failed to load analytics', 'error');
        // Show placeholder data
        updateAnalytics({});
    } finally {
        hideLoading();
    }
}

function updateAnalytics(analytics) {
    document.getElementById('avgDuration').textContent = analytics.avg_claim_duration || '5.2 days';
    document.getElementById('completionRate').textContent = analytics.completion_rate || '68%';
    document.getElementById('detectionAccuracy').textContent = analytics.detection_accuracy || '92%';
    document.getElementById('activeContributors').textContent = analytics.active_contributors || '142';
    
    // Update charts (placeholders)
    document.getElementById('topContributorsChart').innerHTML = '<p>📊 Top contributors chart</p>';
    document.getElementById('responseTimeChart').innerHTML = '<p>⏰ Response time chart</p>';
}

// ========================================
// API Request Helper
// ========================================
async function apiRequest(endpoint, method = 'GET', body = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    const options = {
        method,
        headers
    };
    
    if (body && method !== 'GET') {
        options.body = JSON.stringify(body);
    }
    
    const response = await fetch(url, options);
    
    if (!response.ok) {
        if (response.status === 401) {
            // Unauthorized - logout and show login
            authToken = null;
            localStorage.removeItem('authToken');
            updateAuthUI(false);
            showToast('Session expired. Please login again.', 'warning');
            setTimeout(() => showModal('loginModal'), 500);
            throw new Error('Authentication required');
        }
        throw new Error(`API request failed: ${response.statusText}`);
    }
    
    return response.json();
}

// ========================================
// UI Helpers
// ========================================
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function hideAllModals() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.classList.remove('active');
    });
    
    // Clear error messages
    document.querySelectorAll('.error-message').forEach(error => {
        error.classList.remove('active');
        error.textContent = '';
    });
}

function showError(errorId, message) {
    const errorElement = document.getElementById(errorId);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.add('active');
    }
}

function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 4000);
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    if (days < 30) return `${Math.floor(days / 7)} weeks ago`;
    
    return date.toLocaleDateString();
}
