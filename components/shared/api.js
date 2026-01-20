/**
 * Shared API utilities for MFA components.
 * This file provides common functions for making API calls.
 */

const MFAApi = (function() {
    // Default API URL - can be overridden
    let apiUrl = 'http://localhost:8000';
    
    /**
     * Configure the API URL
     * @param {string} url - The base API URL
     */
    function configure(url) {
        apiUrl = url.replace(/\/$/, ''); // Remove trailing slash
    }
    
    /**
     * Make an API request
     * @param {string} endpoint - API endpoint (e.g., '/auth/login')
     * @param {string} method - HTTP method
     * @param {object} data - Request body data
     * @param {string} token - Optional auth token
     * @returns {Promise<object>} - Response data
     */
    async function request(endpoint, method = 'GET', data = null, token = null) {
        const url = `${apiUrl}${endpoint}`;
        
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        const options = {
            method,
            headers
        };
        
        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }
        
        try {
            console.log(`[MFAApi] Making ${method} request to: ${url}`);
            if (data) {
                console.log(`[MFAApi] Request data:`, data);
            }
            
            const response = await fetch(url, options);
            console.log(`[MFAApi] Response status: ${response.status}`);
            
            const responseData = await response.json();
            console.log(`[MFAApi] Response data:`, responseData);
            
            if (!response.ok) {
                const errorMsg = responseData.detail || 'Request failed';
                console.error(`[MFAApi] Error: ${errorMsg}`);
                throw new Error(errorMsg);
            }
            
            return responseData;
        } catch (error) {
            console.error('[MFAApi] Request failed:', error);
            console.error('[MFAApi] Error details:', {
                message: error.message,
                stack: error.stack
            });
            throw error;
        }
    }
    
    /**
     * Step 1: Login with email and password
     * @param {string} email 
     * @param {string} password 
     * @returns {Promise<object>} - Login response with session token
     */
    async function login(email, password) {
        return request('/auth/login', 'POST', { email, password });
    }
    
    /**
     * Initialize OTP by email (looks up Aadhaar and phone automatically)
     * @param {string} email - User's email address
     * @returns {Promise<object>} - OTP send response with session token
     */
    async function initOtpByEmail(email) {
        return request('/auth/init-otp-by-email', 'POST', {
            email: email
        });
    }
    
    /**
     * Step 2a: Send OTP
     * @param {string} sessionToken - Token from login step
     * @returns {Promise<object>} - OTP send response
     */
    async function sendOtp(sessionToken) {
        return request('/auth/send-otp', 'POST', {
            session_token: sessionToken
        });
    }
    
    /**
     * Step 2b: Verify OTP
     * @param {string} sessionToken - Token from login step
     * @param {string} otp - 6-digit OTP
     * @returns {Promise<object>} - Final verification response with access token
     */
    async function verifyOtp(sessionToken, otp) {
        return request('/auth/verify-otp', 'POST', {
            session_token: sessionToken,
            otp: otp
        });
    }
    
    // Public API
    return {
        configure,
        request,
        login,
        initOtpByEmail,
        sendOtp,
        verifyOtp
    };
})();

// Export for module environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MFAApi;
}

