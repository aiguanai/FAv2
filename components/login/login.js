/**
 * MFA Login Component
 * Step 1: Email and password verification
 */

const MFALogin = (function() {
    let config = {
        container: null,
        apiUrl: 'http://localhost:8000',
        onSuccess: null,
        onError: null
    };
    
    /**
     * Initialize the login component
     * @param {object} options - Configuration options
     */
    function init(options) {
        config = { ...config, ...options };
        
        // Configure API
        if (typeof MFAApi !== 'undefined') {
            MFAApi.configure(config.apiUrl);
        }
        
        // Get container
        const container = typeof config.container === 'string' 
            ? document.querySelector(config.container)
            : config.container;
        
        if (!container) {
            console.error('MFALogin: Container not found');
            return;
        }
        
        // Render component
        render(container);
        
        // Attach event listeners
        attachEvents(container);
    }
    
    /**
     * Render the login form
     */
    function render(container) {
        container.innerHTML = `
            <div class="mfa-login-container">
                <div class="mfa-step-indicator">
                    <div class="mfa-step active"></div>
                    <div class="mfa-step"></div>
                    <div class="mfa-step"></div>
                </div>
                
                <div class="mfa-login-header">
                    <h2>Secure Login</h2>
                    <p>Step 1: Enter your credentials</p>
                </div>
                
                <form class="mfa-login-form" id="mfa-login-form">
                    <div class="mfa-error-message" id="mfa-error"></div>
                    
                    <div class="mfa-form-group">
                        <label for="mfa-email">Email Address</label>
                        <input 
                            type="email" 
                            id="mfa-email" 
                            name="email" 
                            placeholder="you@example.com"
                            required
                            autocomplete="email"
                        >
                    </div>
                    
                    <div class="mfa-form-group">
                        <label for="mfa-password">Password</label>
                        <input 
                            type="password" 
                            id="mfa-password" 
                            name="password" 
                            placeholder="Enter your password"
                            required
                            autocomplete="current-password"
                        >
                    </div>
                    
                    <button type="submit" class="mfa-login-btn" id="mfa-submit-btn">
                        Continue to Face Verification
                    </button>
                </form>
            </div>
        `;
    }
    
    /**
     * Attach event listeners
     */
    function attachEvents(container) {
        const form = container.querySelector('#mfa-login-form');
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleSubmit(container);
        });
    }
    
    /**
     * Handle form submission
     */
    async function handleSubmit(container) {
        const emailInput = container.querySelector('#mfa-email');
        const passwordInput = container.querySelector('#mfa-password');
        const submitBtn = container.querySelector('#mfa-submit-btn');
        const errorDiv = container.querySelector('#mfa-error');
        
        const email = emailInput.value.trim();
        const password = passwordInput.value;
        
        // Validate
        if (!email || !password) {
            showError(errorDiv, 'Please enter both email and password');
            return;
        }
        
        // Show loading state
        submitBtn.disabled = true;
        submitBtn.classList.add('loading');
        hideError(errorDiv);
        
        try {
            // Make API call
            let response;
            
            if (typeof MFAApi !== 'undefined') {
                response = await MFAApi.login(email, password);
            } else {
                // Fallback direct fetch
                const res = await fetch(`${config.apiUrl}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                
                response = await res.json();
                
                if (!res.ok) {
                    throw new Error(response.detail || 'Login failed');
                }
            }
            
            // Success callback
            if (config.onSuccess) {
                config.onSuccess({
                    sessionToken: response.session_token,
                    user: response.user,
                    nextStep: response.next_step
                });
            }
            
        } catch (error) {
            showError(errorDiv, error.message || 'Login failed. Please try again.');
            
            if (config.onError) {
                config.onError(error);
            }
        } finally {
            submitBtn.disabled = false;
            submitBtn.classList.remove('loading');
        }
    }
    
    /**
     * Show error message
     */
    function showError(errorDiv, message) {
        errorDiv.textContent = message;
        errorDiv.classList.add('show');
    }
    
    /**
     * Hide error message
     */
    function hideError(errorDiv) {
        errorDiv.classList.remove('show');
    }
    
    // Public API
    return {
        init
    };
})();

// Export for module environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MFALogin;
}

