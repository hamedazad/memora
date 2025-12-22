// API Configuration
const API_BASE_URL = 'http://185.231.59.157/api/v1';

// App State
let currentUser = null;
let authToken = localStorage.getItem('authToken');

// DOM Elements
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const dashboard = document.getElementById('dashboard');
const navItems = document.getElementById('navItems');

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    if (authToken) {
        showDashboard();
        loadMemories();
    } else {
        showLogin();
    }
    
    // Event listeners
    document.getElementById('loginFormElement').addEventListener('submit', handleLogin);
    document.getElementById('registerFormElement').addEventListener('submit', handleRegister);
    document.getElementById('quickAddForm').addEventListener('submit', handleQuickAdd);
});

// Navigation functions
function showLogin() {
    loginForm.classList.remove('hidden');
    registerForm.classList.add('hidden');
    dashboard.classList.add('hidden');
    updateNavItems();
}

function showRegister() {
    loginForm.classList.add('hidden');
    registerForm.classList.remove('hidden');
    dashboard.classList.add('hidden');
    updateNavItems();
}

function showDashboard() {
    loginForm.classList.add('hidden');
    registerForm.classList.add('hidden');
    dashboard.classList.remove('hidden');
    updateNavItems();
}

function updateNavItems() {
    if (currentUser) {
        navItems.innerHTML = `
            <span class="navbar-text me-3">Welcome, ${currentUser.username}</span>
            <a class="nav-link" href="#" onclick="logout()">Logout</a>
        `;
    } else {
        navItems.innerHTML = `
            <a class="nav-link" href="#" onclick="showLogin()">Login</a>
            <a class="nav-link" href="#" onclick="showRegister()">Register</a>
        `;
    }
}

// Authentication functions
async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    setLoading('login', true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/token/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: email,
                password: password
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            authToken = data.access;
            localStorage.setItem('authToken', authToken);
            
            // Get user profile
            await loadUserProfile();
            showDashboard();
            loadMemories();
            showAlert('Login successful!', 'success');
        } else {
            const error = await response.json();
            showAlert(error.detail || 'Login failed', 'danger');
        }
    } catch (error) {
        showAlert('Network error. Please try again.', 'danger');
    } finally {
        setLoading('login', false);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    
    setLoading('register', true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            })
        });
        
        if (response.ok) {
            showAlert('Registration successful! Please login.', 'success');
            showLogin();
        } else {
            const error = await response.json();
            showAlert(error.detail || 'Registration failed', 'danger');
        }
    } catch (error) {
        showAlert('Network error. Please try again.', 'danger');
    } finally {
        setLoading('register', false);
    }
}

async function loadUserProfile() {
    try {
        const response = await fetch(`${API_BASE_URL}/users/profile/`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            currentUser = await response.json();
        }
    } catch (error) {
        console.error('Error loading user profile:', error);
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    showLogin();
    showAlert('Logged out successfully', 'info');
}

// Memory functions
async function loadMemories() {
    try {
        const response = await fetch(`${API_BASE_URL}/memories/`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const memories = await response.json();
            displayMemories(memories);
            updateStats(memories);
        }
    } catch (error) {
        console.error('Error loading memories:', error);
        showAlert('Error loading memories', 'danger');
    }
}

function displayMemories(memories) {
    const memoriesList = document.getElementById('memoriesList');
    
    if (memories.length === 0) {
        memoriesList.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-brain fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">No memories yet</h5>
                <p class="text-muted">Create your first memory to get started!</p>
            </div>
        `;
        return;
    }
    
    memoriesList.innerHTML = memories.map(memory => `
        <div class="card memory-card mb-3" onclick="viewMemory(${memory.id})">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="card-title">${memory.content.substring(0, 100)}${memory.content.length > 100 ? '...' : ''}</h6>
                        <p class="card-text text-muted small">
                            ${memory.summary || 'No summary available'}
                        </p>
                        <div class="d-flex align-items-center">
                            <span class="badge bg-${getImportanceColor(memory.importance)} me-2">
                                ${getImportanceText(memory.importance)}
                            </span>
                            ${memory.tags ? memory.tags.map(tag => `<span class="badge bg-light text-dark me-1">${tag}</span>`).join('') : ''}
                        </div>
                    </div>
                    <div class="text-end">
                        <small class="text-muted">${formatDate(memory.created_at)}</small>
                        <div class="mt-2">
                            <button class="btn btn-sm btn-outline-primary me-1" onclick="event.stopPropagation(); likeMemory(${memory.id})">
                                <i class="fas fa-heart"></i> ${memory.likes_count || 0}
                            </button>
                            <button class="btn btn-sm btn-outline-secondary" onclick="event.stopPropagation(); shareMemory(${memory.id})">
                                <i class="fas fa-share"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function updateStats(memories) {
    const today = new Date().toDateString();
    const todayMemories = memories.filter(m => new Date(m.created_at).toDateString() === today);
    const importantMemories = memories.filter(m => m.importance === 3);
    const sharedMemories = memories.filter(m => m.is_shared);
    
    document.getElementById('totalMemories').textContent = memories.length;
    document.getElementById('todayMemories').textContent = todayMemories.length;
    document.getElementById('importantMemories').textContent = importantMemories.length;
    document.getElementById('sharedMemories').textContent = sharedMemories.length;
}

async function handleQuickAdd(e) {
    e.preventDefault();
    
    const content = document.getElementById('quickMemoryContent').value;
    const importance = document.getElementById('quickMemoryImportance').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/memories/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                content: content,
                importance: parseInt(importance)
            })
        });
        
        if (response.ok) {
            document.getElementById('quickMemoryContent').value = '';
            loadMemories();
            showAlert('Memory created successfully!', 'success');
        } else {
            const error = await response.json();
            showAlert(error.detail || 'Error creating memory', 'danger');
        }
    } catch (error) {
        showAlert('Network error. Please try again.', 'danger');
    }
}

function showCreateMemory() {
    const modal = new bootstrap.Modal(document.getElementById('createMemoryModal'));
    modal.show();
}

async function createMemory() {
    const content = document.getElementById('memoryContent').value;
    const importance = document.getElementById('memoryImportance').value;
    const tags = document.getElementById('memoryTags').value;
    const aiEnhancement = document.getElementById('aiEnhancement').checked;
    
    setLoading('create', true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/memories/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                content: content,
                importance: parseInt(importance),
                tags: tags ? tags.split(',').map(t => t.trim()) : [],
                use_ai_enhancement: aiEnhancement
            })
        });
        
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('createMemoryModal'));
            modal.hide();
            
            // Clear form
            document.getElementById('memoryContent').value = '';
            document.getElementById('memoryTags').value = '';
            
            loadMemories();
            showAlert('Memory created successfully!', 'success');
        } else {
            const error = await response.json();
            showAlert(error.detail || 'Error creating memory', 'danger');
        }
    } catch (error) {
        showAlert('Network error. Please try again.', 'danger');
    } finally {
        setLoading('create', false);
    }
}

// Utility functions
function setLoading(type, loading) {
    const btnText = document.getElementById(`${type}BtnText`);
    const btnLoading = document.getElementById(`${type}BtnLoading`);
    
    if (loading) {
        btnText.classList.add('hidden');
        btnLoading.classList.remove('hidden');
    } else {
        btnText.classList.remove('hidden');
        btnLoading.classList.add('hidden');
    }
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function getImportanceColor(importance) {
    switch (importance) {
        case 1: return 'success';
        case 2: return 'warning';
        case 3: return 'danger';
        default: return 'secondary';
    }
}

function getImportanceText(importance) {
    switch (importance) {
        case 1: return 'Low';
        case 2: return 'Medium';
        case 3: return 'High';
        default: return 'Unknown';
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

// Placeholder functions for future implementation
function viewMemory(id) {
    showAlert(`Viewing memory ${id} - Feature coming soon!`, 'info');
}

function likeMemory(id) {
    showAlert(`Liked memory ${id} - Feature coming soon!`, 'info');
}

function shareMemory(id) {
    showAlert(`Sharing memory ${id} - Feature coming soon!`, 'info');
}

// AI Suggestions (placeholder)
async function getAISuggestions() {
    try {
        const response = await fetch(`${API_BASE_URL}/ai/suggestions/`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const suggestions = await response.json();
            return suggestions;
        }
    } catch (error) {
        console.error('Error getting AI suggestions:', error);
    }
    return [];
}
