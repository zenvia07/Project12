// API Configuration
const API_BASE_URL = 'http://localhost:3000/api';

// State Management
let currentUser = null;
let accessToken = null;
let refreshToken = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
    checkAuthStatus();
});

// Initialize Application
function initializeApp() {
    // Check for tokens in localStorage
    accessToken = localStorage.getItem('accessToken');
    refreshToken = localStorage.getItem('refreshToken');
    
    // Check URL parameters for activation token
    const urlParams = new URLSearchParams(window.location.search);
    const activationToken = urlParams.get('token');
    
    // If we have a token in URL, treat it as activation
    if (activationToken) {
        console.log('Activation token found in URL:', activationToken);
        showActivationContainer();
        activateAccount(activationToken);
    } else if (accessToken) {
        // Verify token and load dashboard
        verifyTokenAndLoadDashboard();
    } else {
        showLoginContainer();
    }
}

// Setup Event Listeners
function setupEventListeners() {
    // Form submissions
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
    document.getElementById('forgotPasswordForm').addEventListener('submit', handleForgotPassword);
    document.getElementById('changePasswordForm').addEventListener('submit', handleChangePassword);
    
    // Navigation links
    document.getElementById('showRegisterLink').addEventListener('click', (e) => {
        e.preventDefault();
        showRegisterContainer();
    });
    
    document.getElementById('showLoginLink').addEventListener('click', (e) => {
        e.preventDefault();
        showLoginContainer();
    });
    
    document.getElementById('forgotPasswordLink').addEventListener('click', (e) => {
        e.preventDefault();
        showForgotPasswordContainer();
    });
    
    document.getElementById('backToLoginLink').addEventListener('click', (e) => {
        e.preventDefault();
        showLoginContainer();
    });
    
    document.getElementById('backToDashboardLink').addEventListener('click', (e) => {
        e.preventDefault();
        showDashboardContainer();
    });
    
    // Password toggles
    setupPasswordToggles();
    
    // Password strength indicators
    setupPasswordStrength();
    
    // Logout
    document.getElementById('logoutBtn').addEventListener('click', handleLogout);
    
    // Change password button
    document.getElementById('changePasswordBtn').addEventListener('click', () => {
        showChangePasswordContainer();
    });
    
    // Toast close
    document.getElementById('toastClose').addEventListener('click', hideToast);
}

// Password Toggle Setup
function setupPasswordToggles() {
    const toggles = [
        { input: 'loginPassword', toggle: 'toggleLoginPassword' },
        { input: 'registerPassword', toggle: 'toggleRegisterPassword' },
        { input: 'currentPassword', toggle: 'toggleCurrentPassword' },
        { input: 'newPassword', toggle: 'toggleNewPassword' }
    ];
    
    toggles.forEach(({ input, toggle }) => {
        const inputEl = document.getElementById(input);
        const toggleEl = document.getElementById(toggle);
        
        if (inputEl && toggleEl) {
            toggleEl.addEventListener('click', () => {
                const type = inputEl.getAttribute('type') === 'password' ? 'text' : 'password';
                inputEl.setAttribute('type', type);
            });
        }
    });
}

// Password Strength Setup
function setupPasswordStrength() {
    const passwordInputs = ['registerPassword', 'newPassword'];
    
    passwordInputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        const strengthEl = document.getElementById(inputId === 'registerPassword' ? 'passwordStrength' : 'newPasswordStrength');
        
        if (input && strengthEl) {
            input.addEventListener('input', () => {
                const strength = calculatePasswordStrength(input.value);
                strengthEl.className = `password-strength ${strength}`;
            });
        }
    });
}

// Calculate Password Strength
function calculatePasswordStrength(password) {
    if (password.length === 0) return '';
    
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[^a-zA-Z\d]/.test(password)) strength++;
    
    if (strength <= 2) return 'weak';
    if (strength <= 4) return 'medium';
    return 'strong';
}

// Show/Hide Containers
function showLoginContainer() {
    hideAllContainers();
    document.getElementById('loginContainer').classList.remove('hidden');
    clearForm('loginForm');
}

function showRegisterContainer() {
    hideAllContainers();
    document.getElementById('registerContainer').classList.remove('hidden');
    clearForm('registerForm');
}

function showForgotPasswordContainer() {
    hideAllContainers();
    document.getElementById('forgotPasswordContainer').classList.remove('hidden');
    clearForm('forgotPasswordForm');
}

function showActivationContainer() {
    hideAllContainers();
    document.getElementById('activationContainer').classList.remove('hidden');
}

function showDashboardContainer() {
    hideAllContainers();
    document.getElementById('dashboardContainer').classList.remove('hidden');
    loadUserProfile();
}

function showChangePasswordContainer() {
    hideAllContainers();
    document.getElementById('changePasswordContainer').classList.remove('hidden');
    clearForm('changePasswordForm');
}

function hideAllContainers() {
    document.querySelectorAll('.form-container').forEach(container => {
        container.classList.add('hidden');
    });
}

// Form Handlers
async function handleLogin(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    
    const data = {
        email: formData.get('email'),
        password: formData.get('password')
    };
    
    const btn = document.getElementById('loginBtn');
    setLoading(btn, true);
    clearErrors('loginForm');
    
    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Store tokens
            accessToken = result.tokens.access_token;
            refreshToken = result.tokens.refresh_token;
            localStorage.setItem('accessToken', accessToken);
            localStorage.setItem('refreshToken', refreshToken);
            
            // Store user info
            currentUser = result.user;
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            
            // Check remember me
            const rememberMe = document.getElementById('rememberMe').checked;
            if (!rememberMe) {
                // Tokens will be cleared on browser close (sessionStorage could be used)
            }
            
            showToast('Login successful!', 'success');
            setTimeout(() => {
                showDashboardContainer();
            }, 1000);
        } else {
            showFormError('loginForm', result.detail || 'Login failed');
            showToast(result.detail || 'Login failed', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
        console.error('Login error:', error);
    } finally {
        setLoading(btn, false);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    
    // Get date of birth and convert to ISO datetime format
    const dateOfBirth = formData.get('date_of_birth');
    // Convert "YYYY-MM-DD" to "YYYY-MM-DDTHH:MM:SS" format
    const dateOfBirthISO = dateOfBirth ? `${dateOfBirth}T00:00:00` : null;
    
    const data = {
        first_name: formData.get('first_name'),
        last_name: formData.get('last_name'),
        date_of_birth: dateOfBirthISO,
        email: formData.get('email'),
        phone_number: formData.get('phone_number'),
        password: formData.get('password')
    };
    
    const btn = document.getElementById('registerBtn');
    setLoading(btn, true);
    clearErrors('registerForm');
    
    try {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        let result;
        try {
            const responseText = await response.text();
            result = responseText ? JSON.parse(responseText) : {};
        } catch (e) {
            console.error('Error parsing response:', e);
            showToast('Server error: Invalid response format', 'error');
            setLoading(btn, false);
            return;
        }
        
        if (response.ok) {
            showToast('Registration successful! Please check your email to activate your account.', 'success');
            setTimeout(() => {
                showLoginContainer();
            }, 2000);
        } else {
            // Handle different error response formats
            let errorMessage = 'Registration failed';
            
            if (result.detail) {
                if (typeof result.detail === 'string') {
                    errorMessage = result.detail;
                    // Check if error is email-related and show it in the email field
                    const emailErrorKeywords = ['email', 'Email', 'EMAIL'];
                    const isEmailError = emailErrorKeywords.some(keyword => result.detail.includes(keyword));
                    
                    if (isEmailError) {
                        showFieldError('registerEmail', result.detail);
                    } else {
                        // For other errors, try to map to appropriate field
                        const fieldMappings = {
                            'first_name': 'firstName',
                            'last_name': 'lastName',
                            'date_of_birth': 'dateOfBirth',
                            'phone_number': 'phoneNumber',
                            'password': 'registerPassword'
                        };
                        
                        let fieldFound = false;
                        for (const [apiField, formField] of Object.entries(fieldMappings)) {
                            if (result.detail.toLowerCase().includes(apiField.replace('_', ' '))) {
                                showFieldError(formField, result.detail);
                                fieldFound = true;
                                break;
                            }
                        }
                        
                        if (!fieldFound) {
                            showFormError('registerForm', result.detail);
                        }
                    }
                } else if (Array.isArray(result.detail)) {
                    // Pydantic validation errors
                    const errors = [];
                    result.detail.forEach(error => {
                        const field = error.loc && error.loc.length > 0 ? error.loc[error.loc.length - 1] : 'field';
                        const msg = error.msg || 'Invalid value';
                        errors.push(`${field}: ${msg}`);
                        const fieldId = `register${field.charAt(0).toUpperCase() + field.slice(1)}`;
                        showFieldError(fieldId, msg);
                    });
                    errorMessage = errors.join(', ');
                } else if (typeof result.detail === 'object') {
                    // Convert object to readable string
                    errorMessage = Object.keys(result.detail).map(key => `${key}: ${result.detail[key]}`).join(', ');
                }
            } else if (result.message) {
                errorMessage = result.message;
            }
            
            console.error('Registration error:', result);
            showToast(errorMessage, 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
        console.error('Registration error:', error);
    } finally {
        setLoading(btn, false);
    }
}

async function handleForgotPassword(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    
    const data = {
        email: formData.get('email')
    };
    
    const btn = document.getElementById('forgotPasswordBtn');
    setLoading(btn, true);
    clearErrors('forgotPasswordForm');
    
    try {
        const response = await fetch(`${API_BASE_URL}/forgot-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showToast(result.message || 'If the email exists, a reset link has been sent.', 'success');
            setTimeout(() => {
                showLoginContainer();
            }, 2000);
        } else {
            showFormError('forgotPasswordForm', result.detail || 'Failed to send reset email');
            showToast(result.detail || 'Failed to send reset email', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
        console.error('Forgot password error:', error);
    } finally {
        setLoading(btn, false);
    }
}

async function handleChangePassword(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    
    const data = {
        current_password: formData.get('current_password'),
        new_password: formData.get('new_password')
    };
    
    const btn = document.getElementById('changePasswordSubmitBtn');
    setLoading(btn, true);
    clearErrors('changePasswordForm');
    
    try {
        const response = await fetch(`${API_BASE_URL}/change-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showToast('Password changed successfully!', 'success');
            clearForm('changePasswordForm');
            setTimeout(() => {
                showDashboardContainer();
            }, 1500);
        } else {
            if (response.status === 401) {
                // Token expired, try refresh
                const refreshed = await refreshAccessToken();
                if (refreshed) {
                    // Retry the request
                    return handleChangePassword(e);
                } else {
                    handleLogout();
                    return;
                }
            }
            showFormError('changePasswordForm', result.detail || 'Failed to change password');
            showToast(result.detail || 'Failed to change password', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
        console.error('Change password error:', error);
    } finally {
        setLoading(btn, false);
    }
}

// Account Activation
async function activateAccount(token) {
    const statusEl = document.getElementById('activationStatus');
    statusEl.textContent = 'Activating your account...';
    statusEl.className = 'activation-status';
    
    // Clean the token (remove any URL encoding or whitespace)
    token = decodeURIComponent(token).trim();
    console.log('Activating with token:', token);
    
    try {
        const response = await fetch(`${API_BASE_URL}/activate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token: token })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            statusEl.textContent = 'Account activated successfully! Redirecting to login...';
            statusEl.className = 'activation-status success';
            showToast('Account activated successfully!', 'success');
            setTimeout(() => {
                // Clear URL parameters and show login
                window.history.replaceState({}, document.title, window.location.pathname);
                showLoginContainer();
            }, 2000);
        } else {
            statusEl.textContent = result.detail || 'Activation failed';
            statusEl.className = 'activation-status error';
            showToast(result.detail || 'Activation failed', 'error');
        }
    } catch (error) {
        statusEl.textContent = 'Network error. Please try again.';
        statusEl.className = 'activation-status error';
        showToast('Network error. Please try again.', 'error');
        console.error('Activation error:', error);
    }
}

// User Profile
async function loadUserProfile() {
    try {
        const response = await fetch(`${API_BASE_URL}/me`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        
        if (response.ok) {
            const user = await response.json();
            currentUser = user;
            displayUserInfo(user);
        } else if (response.status === 401) {
            const refreshed = await refreshAccessToken();
            if (refreshed) {
                return loadUserProfile();
            } else {
                handleLogout();
            }
        } else {
            showToast('Failed to load profile', 'error');
        }
    } catch (error) {
        showToast('Network error', 'error');
        console.error('Load profile error:', error);
    }
}

function displayUserInfo(user) {
    const welcomeEl = document.getElementById('userWelcomeMessage');
    const infoEl = document.getElementById('userInfo');
    
    welcomeEl.textContent = `Welcome, ${user.first_name} ${user.last_name}!`;
    
    const infoHTML = `
        <div class="user-info-item">
            <span class="user-info-label">Email:</span>
            <span class="user-info-value">${user.email}</span>
        </div>
        <div class="user-info-item">
            <span class="user-info-label">Phone:</span>
            <span class="user-info-value">${user.phone_number}</span>
        </div>
        <div class="user-info-item">
            <span class="user-info-label">Date of Birth:</span>
            <span class="user-info-value">${new Date(user.date_of_birth).toLocaleDateString()}</span>
        </div>
        <div class="user-info-item">
            <span class="user-info-label">Account Status:</span>
            <span class="user-info-value">${user.is_active ? 'Active' : 'Inactive'}</span>
        </div>
    `;
    
    infoEl.innerHTML = infoHTML;
}

// Token Management
async function refreshAccessToken() {
    if (!refreshToken) {
        return false;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/refresh`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ refresh_token: refreshToken })
        });
        
        if (response.ok) {
            const result = await response.json();
            accessToken = result.access_token;
            localStorage.setItem('accessToken', accessToken);
            return true;
        } else {
            return false;
        }
    } catch (error) {
        console.error('Token refresh error:', error);
        return false;
    }
}

async function verifyTokenAndLoadDashboard() {
    try {
        const response = await fetch(`${API_BASE_URL}/me`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        
        if (response.ok) {
            currentUser = await response.json();
            showDashboardContainer();
        } else if (response.status === 401) {
            const refreshed = await refreshAccessToken();
            if (refreshed) {
                verifyTokenAndLoadDashboard();
            } else {
                handleLogout();
            }
        } else {
            handleLogout();
        }
    } catch (error) {
        console.error('Token verification error:', error);
        handleLogout();
    }
}

function checkAuthStatus() {
    // Check if user is already authenticated
    if (accessToken) {
        verifyTokenAndLoadDashboard();
    }
}

// Logout
function handleLogout() {
    accessToken = null;
    refreshToken = null;
    currentUser = null;
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('currentUser');
    showLoginContainer();
    showToast('Logged out successfully', 'success');
}

// Utility Functions
function setLoading(button, loading) {
    const btnText = button.querySelector('.btn-text');
    const btnLoader = button.querySelector('.btn-loader');
    
    if (loading) {
        button.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'block';
    } else {
        button.disabled = false;
        btnText.style.display = 'block';
        btnLoader.style.display = 'none';
    }
}

function clearForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.reset();
        clearErrors(formId);
    }
}

function clearErrors(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.querySelectorAll('.error-message').forEach(el => {
            el.textContent = '';
        });
        form.querySelectorAll('input').forEach(input => {
            input.classList.remove('error');
        });
    }
}

function showFormError(formId, message) {
    const form = document.getElementById(formId);
    if (form) {
        const firstErrorEl = form.querySelector('.error-message');
        if (firstErrorEl) {
            firstErrorEl.textContent = message;
        }
    }
}

function showFieldError(fieldId, message) {
    const errorEl = document.getElementById(`${fieldId}Error`);
    if (errorEl) {
        errorEl.textContent = message;
    }
    const inputEl = document.getElementById(fieldId);
    if (inputEl) {
        inputEl.classList.add('error');
    }
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    
    // Ensure message is a string (handle objects, arrays, etc.)
    let messageText = message;
    if (typeof message === 'object') {
        if (Array.isArray(message)) {
            messageText = message.join(', ');
        } else {
            messageText = JSON.stringify(message);
        }
    } else if (message === null || message === undefined) {
        messageText = 'An error occurred';
    }
    
    toastMessage.textContent = messageText;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        hideToast();
    }, 5000);
}

function hideToast() {
    const toast = document.getElementById('toast');
    toast.classList.remove('show');
}
