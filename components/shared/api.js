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
            const response = await fetch(url, options);
            const responseData = await response.json();
            
            if (!response.ok) {
                throw new Error(responseData.detail || 'Request failed');
            }
            
            return responseData;
        } catch (error) {
            console.error('API Error:', error);
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
     * Step 2: Verify face
     * @param {string} sessionToken - Token from login step
     * @param {string} faceImageBase64 - Base64 encoded face image
     * @returns {Promise<object>} - Face verification response
     */
    async function verifyFace(sessionToken, faceImageBase64) {
        return request('/auth/verify-face', 'POST', {
            session_token: sessionToken,
            face_image: faceImageBase64
        });
    }
    
    /**
     * Step 3a: Send OTP
     * @param {string} sessionToken - Token from face verification step
     * @returns {Promise<object>} - OTP send response
     */
    async function sendOtp(sessionToken) {
        return request('/auth/send-otp', 'POST', {
            session_token: sessionToken
        });
    }
    
    /**
     * Step 3b: Verify OTP
     * @param {string} sessionToken - Token from face verification step
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
        verifyFace,
        sendOtp,
        verifyOtp
    };
})();

// Export for module environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MFAApi;
}

