/**
 * MFA OTP Verification Component
 * Step 3: OTP verification via Aadhaar-linked phone
 */

const MFAOtpVerify = (function() {
    let config = {
        container: null,
        apiUrl: 'http://localhost:8000',
        sessionToken: null,
        phoneMasked: '****',
        expirySeconds: 300,
        onSuccess: null,
        onError: null
    };
    
    let timerInterval = null;
    let remainingSeconds = 0;
    
    /**
     * Initialize the OTP verification component
     * @param {object} options - Configuration options
     */
    function init(options) {
        config = { ...config, ...options };
        
        if (!config.sessionToken) {
            console.error('MFAOtpVerify: Session token is required');
            return;
        }
        
        // Configure API
        if (typeof MFAApi !== 'undefined') {
            MFAApi.configure(config.apiUrl);
        }
        
        // Get container
        const container = typeof config.container === 'string' 
            ? document.querySelector(config.container)
            : config.container;
        
        if (!container) {
            console.error('MFAOtpVerify: Container not found');
            return;
        }
        
        // Render component
        render(container);
        
        // Attach events
        attachEvents(container);
        
        // Send OTP automatically
        sendOtp(container);
    }
    
    /**
     * Render the OTP verification UI
     */
    function render(container) {
        container.innerHTML = `
            <div class="mfa-otp-container">
                <div class="mfa-step-indicator">
                    <div class="mfa-step completed"></div>
                    <div class="mfa-step completed"></div>
                    <div class="mfa-step active"></div>
                </div>
                
                <div class="mfa-otp-header">
                    <h2>OTP Verification</h2>
                    <p>Step 3: Enter the code sent to your phone</p>
                </div>
                
                <div class="mfa-error-message" id="mfa-otp-error"></div>
                
                <div class="mfa-success-message" id="mfa-otp-success">
                    <div class="icon">✓</div>
                    <h3>Authentication Successful!</h3>
                    <p>You have been securely logged in.</p>
                </div>
                
                <div id="mfa-otp-form-container">
                    <div class="mfa-phone-display">
                        <div class="icon">📱</div>
                        <div class="label">OTP sent to</div>
                        <div class="number" id="mfa-phone-number">${config.phoneMasked}</div>
                    </div>
                    
                    <form class="mfa-otp-form" id="mfa-otp-form">
                        <div class="mfa-otp-inputs" id="mfa-otp-inputs">
                            <input type="text" class="mfa-otp-input" maxlength="1" data-index="0" inputmode="numeric" autocomplete="one-time-code">
                            <input type="text" class="mfa-otp-input" maxlength="1" data-index="1" inputmode="numeric">
                            <input type="text" class="mfa-otp-input" maxlength="1" data-index="2" inputmode="numeric">
                            <input type="text" class="mfa-otp-input" maxlength="1" data-index="3" inputmode="numeric">
                            <input type="text" class="mfa-otp-input" maxlength="1" data-index="4" inputmode="numeric">
                            <input type="text" class="mfa-otp-input" maxlength="1" data-index="5" inputmode="numeric">
                        </div>
                        
                        <div class="mfa-timer" id="mfa-timer">
                            Code expires in <span class="time" id="mfa-timer-value">5:00</span>
                        </div>
                        
                        <button type="submit" class="mfa-verify-btn" id="mfa-verify-btn" disabled>
                            Verify OTP
                        </button>
                        
                        <div class="mfa-resend-link">
                            <button type="button" id="mfa-resend-btn" disabled>
                                Resend OTP
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;
    }
    
    /**
     * Attach event listeners
     */
    function attachEvents(container) {
        const inputs = container.querySelectorAll('.mfa-otp-input');
        const form = container.querySelector('#mfa-otp-form');
        const resendBtn = container.querySelector('#mfa-resend-btn');
        
        // OTP input handling
        inputs.forEach((input, index) => {
            // Handle input
            input.addEventListener('input', (e) => {
                const value = e.target.value;
                
                // Only allow digits
                if (!/^\d*$/.test(value)) {
                    e.target.value = '';
                    return;
                }
                
                if (value) {
                    e.target.classList.add('filled');
                    // Move to next input
                    if (index < inputs.length - 1) {
                        inputs[index + 1].focus();
                    }
                } else {
                    e.target.classList.remove('filled');
                }
                
                // Check if all filled
                updateVerifyButton(container);
            });
            
            // Handle backspace
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Backspace' && !e.target.value && index > 0) {
                    inputs[index - 1].focus();
                    inputs[index - 1].value = '';
                    inputs[index - 1].classList.remove('filled');
                }
            });
            
            // Handle paste
            input.addEventListener('paste', (e) => {
                e.preventDefault();
                const pastedData = e.clipboardData.getData('text').replace(/\D/g, '');
                
                // Fill inputs with pasted data
                for (let i = 0; i < Math.min(pastedData.length, inputs.length); i++) {
                    inputs[i].value = pastedData[i];
                    inputs[i].classList.add('filled');
                }
                
                // Focus last filled or next empty
                const lastIndex = Math.min(pastedData.length, inputs.length) - 1;
                if (lastIndex >= 0) {
                    inputs[Math.min(lastIndex + 1, inputs.length - 1)].focus();
                }
                
                updateVerifyButton(container);
            });
        });
        
        // Form submit
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await verifyOtp(container);
        });
        
        // Resend button
        resendBtn.addEventListener('click', async () => {
            await sendOtp(container);
        });
    }
    
    /**
     * Update verify button state
     */
    function updateVerifyButton(container) {
        const inputs = container.querySelectorAll('.mfa-otp-input');
        const verifyBtn = container.querySelector('#mfa-verify-btn');
        
        const allFilled = Array.from(inputs).every(input => input.value.length === 1);
        verifyBtn.disabled = !allFilled;
    }
    
    /**
     * Send OTP to user's phone
     */
    async function sendOtp(container) {
        const errorDiv = container.querySelector('#mfa-otp-error');
        const resendBtn = container.querySelector('#mfa-resend-btn');
        
        hideError(errorDiv);
        resendBtn.disabled = true;
        resendBtn.textContent = 'Sending...';
        
        try {
            let response;
            
            if (typeof MFAApi !== 'undefined') {
                response = await MFAApi.sendOtp(config.sessionToken);
            } else {
                const res = await fetch(`${config.apiUrl}/auth/send-otp`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_token: config.sessionToken })
                });
                
                response = await res.json();
                
                if (!res.ok) {
                    throw new Error(response.detail || 'Failed to send OTP');
                }
            }
            
            // Start timer
            startTimer(container, response.expires_in || config.expirySeconds);
            
            resendBtn.textContent = 'Resend OTP';
            
        } catch (error) {
            showError(errorDiv, error.message || 'Failed to send OTP. Please try again.');
            resendBtn.textContent = 'Retry Send';
            resendBtn.disabled = false;
        }
    }
    
    /**
     * Start the countdown timer
     */
    function startTimer(container, seconds) {
        const timerDiv = container.querySelector('#mfa-timer');
        const timerValue = container.querySelector('#mfa-timer-value');
        const resendBtn = container.querySelector('#mfa-resend-btn');
        
        // Clear existing timer
        if (timerInterval) {
            clearInterval(timerInterval);
        }
        
        remainingSeconds = seconds;
        timerDiv.classList.remove('expired');
        
        const updateDisplay = () => {
            const mins = Math.floor(remainingSeconds / 60);
            const secs = remainingSeconds % 60;
            timerValue.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
        };
        
        updateDisplay();
        
        timerInterval = setInterval(() => {
            remainingSeconds--;
            updateDisplay();
            
            if (remainingSeconds <= 0) {
                clearInterval(timerInterval);
                timerDiv.classList.add('expired');
                timerValue.textContent = 'Expired';
                resendBtn.disabled = false;
            }
        }, 1000);
    }
    
    /**
     * Verify the OTP
     */
    async function verifyOtp(container) {
        const inputs = container.querySelectorAll('.mfa-otp-input');
        const verifyBtn = container.querySelector('#mfa-verify-btn');
        const errorDiv = container.querySelector('#mfa-otp-error');
        const successDiv = container.querySelector('#mfa-otp-success');
        const formContainer = container.querySelector('#mfa-otp-form-container');
        
        // Get OTP value
        const otp = Array.from(inputs).map(input => input.value).join('');
        
        if (otp.length !== 6) {
            showError(errorDiv, 'Please enter the complete 6-digit OTP');
            return;
        }
        
        // Show loading
        verifyBtn.disabled = true;
        verifyBtn.classList.add('loading');
        verifyBtn.textContent = '';
        hideError(errorDiv);
        
        try {
            let response;
            
            if (typeof MFAApi !== 'undefined') {
                response = await MFAApi.verifyOtp(config.sessionToken, otp);
            } else {
                const res = await fetch(`${config.apiUrl}/auth/verify-otp`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_token: config.sessionToken,
                        otp: otp
                    })
                });
                
                response = await res.json();
                
                if (!res.ok) {
                    throw new Error(response.detail || 'OTP verification failed');
                }
            }
            
            // Stop timer
            if (timerInterval) {
                clearInterval(timerInterval);
            }
            
            // Show success
            formContainer.style.display = 'none';
            successDiv.classList.add('show');
            
            // Callback
            if (config.onSuccess) {
                config.onSuccess({
                    accessToken: response.access_token,
                    tokenType: response.token_type
                });
            }
            
        } catch (error) {
            // Show error on inputs
            inputs.forEach(input => input.classList.add('error'));
            setTimeout(() => {
                inputs.forEach(input => input.classList.remove('error'));
            }, 500);
            
            showError(errorDiv, error.message || 'Invalid OTP. Please try again.');
            
            if (config.onError) {
                config.onError(error);
            }
        } finally {
            verifyBtn.disabled = false;
            verifyBtn.classList.remove('loading');
            verifyBtn.textContent = 'Verify OTP';
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
    
    /**
     * Cleanup
     */
    function destroy() {
        if (timerInterval) {
            clearInterval(timerInterval);
        }
    }
    
    // Public API
    return {
        init,
        destroy
    };
})();

// Export for module environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MFAOtpVerify;
}

