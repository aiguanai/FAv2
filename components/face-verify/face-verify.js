/**
 * MFA Face Verification Component
 * Step 2: Webcam capture and face verification
 */

const MFAFaceVerify = (function() {
    let config = {
        container: null,
        apiUrl: 'http://localhost:8000',
        sessionToken: null,
        onSuccess: null,
        onError: null
    };
    
    let videoStream = null;
    let videoElement = null;
    let canvasElement = null;
    
    /**
     * Initialize the face verification component
     * @param {object} options - Configuration options
     */
    function init(options) {
        config = { ...config, ...options };
        
        if (!config.sessionToken) {
            console.error('MFAFaceVerify: Session token is required');
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
            console.error('MFAFaceVerify: Container not found');
            return;
        }
        
        // Render component
        render(container);
        
        // Initialize camera
        initCamera(container);
    }
    
    /**
     * Render the face verification UI
     */
    function render(container) {
        container.innerHTML = `
            <div class="mfa-face-container">
                <div class="mfa-step-indicator">
                    <div class="mfa-step completed"></div>
                    <div class="mfa-step active"></div>
                    <div class="mfa-step"></div>
                </div>
                
                <div class="mfa-face-header">
                    <h2>Face Verification</h2>
                    <p>Step 2: Look at the camera</p>
                </div>
                
                <div class="mfa-error-message" id="mfa-face-error"></div>
                
                <div class="mfa-instructions">
                    <h4>📸 Tips for best results:</h4>
                    <ul>
                        <li>Ensure good lighting on your face</li>
                        <li>Look directly at the camera</li>
                        <li>Remove sunglasses or hats</li>
                        <li>Keep your face within the oval guide</li>
                    </ul>
                </div>
                
                <div class="mfa-camera-container" id="mfa-camera-container">
                    <div class="mfa-camera-permission" id="mfa-camera-permission">
                        <div class="icon">📷</div>
                        <p>Camera access is required for face verification</p>
                        <button id="mfa-enable-camera">Enable Camera</button>
                    </div>
                    
                    <video class="mfa-camera-video" id="mfa-video" autoplay playsinline></video>
                    <canvas class="mfa-camera-canvas" id="mfa-canvas"></canvas>
                    
                    <div class="mfa-camera-overlay">
                        <div class="mfa-face-guide" id="mfa-face-guide"></div>
                    </div>
                    
                    <div class="mfa-camera-status" id="mfa-camera-status">Initializing camera...</div>
                </div>
                
                <button class="mfa-capture-btn" id="mfa-capture-btn" disabled>
                    <span>Verify My Face</span>
                </button>
            </div>
        `;
    }
    
    /**
     * Initialize camera access
     */
    async function initCamera(container) {
        const video = container.querySelector('#mfa-video');
        const canvas = container.querySelector('#mfa-canvas');
        const permissionDiv = container.querySelector('#mfa-camera-permission');
        const statusDiv = container.querySelector('#mfa-camera-status');
        const captureBtn = container.querySelector('#mfa-capture-btn');
        const enableBtn = container.querySelector('#mfa-enable-camera');
        
        videoElement = video;
        canvasElement = canvas;
        
        // Enable camera button click
        enableBtn.addEventListener('click', async () => {
            await startCamera(container);
        });
        
        // Capture button click
        captureBtn.addEventListener('click', async () => {
            await captureAndVerify(container);
        });
        
        // Try to auto-start camera
        await startCamera(container);
    }
    
    /**
     * Start the camera stream
     */
    async function startCamera(container) {
        const video = container.querySelector('#mfa-video');
        const permissionDiv = container.querySelector('#mfa-camera-permission');
        const statusDiv = container.querySelector('#mfa-camera-status');
        const captureBtn = container.querySelector('#mfa-capture-btn');
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                }
            });
            
            videoStream = stream;
            video.srcObject = stream;
            
            // Hide permission prompt, show video
            permissionDiv.style.display = 'none';
            video.style.display = 'block';
            
            // Update status
            statusDiv.textContent = 'Position your face in the oval';
            statusDiv.classList.remove('error');
            
            // Enable capture button
            captureBtn.disabled = false;
            
        } catch (error) {
            console.error('Camera error:', error);
            
            statusDiv.textContent = 'Camera access denied';
            statusDiv.classList.add('error');
            
            showError(container.querySelector('#mfa-face-error'), 
                'Could not access camera. Please allow camera permissions and try again.');
        }
    }
    
    /**
     * Capture image and verify face
     */
    async function captureAndVerify(container) {
        const canvas = container.querySelector('#mfa-canvas');
        const video = container.querySelector('#mfa-video');
        const statusDiv = container.querySelector('#mfa-camera-status');
        const captureBtn = container.querySelector('#mfa-capture-btn');
        const errorDiv = container.querySelector('#mfa-face-error');
        const faceGuide = container.querySelector('#mfa-face-guide');
        
        // Show loading state
        captureBtn.disabled = true;
        captureBtn.innerHTML = '<span>Verifying...</span>';
        captureBtn.classList.add('loading');
        statusDiv.textContent = 'Capturing...';
        hideError(errorDiv);
        
        try {
            // Capture frame from video
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');
            
            // Flip horizontally to match mirror view
            ctx.translate(canvas.width, 0);
            ctx.scale(-1, 1);
            ctx.drawImage(video, 0, 0);
            
            // Convert to base64
            const imageBase64 = canvas.toDataURL('image/jpeg', 0.8);
            
            statusDiv.textContent = 'Analyzing face...';
            
            // Make API call
            let response;
            
            if (typeof MFAApi !== 'undefined') {
                response = await MFAApi.verifyFace(config.sessionToken, imageBase64);
            } else {
                const res = await fetch(`${config.apiUrl}/auth/verify-face`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_token: config.sessionToken,
                        face_image: imageBase64
                    })
                });
                
                response = await res.json();
                
                if (!res.ok) {
                    throw new Error(response.detail || 'Face verification failed');
                }
            }
            
            // Success
            statusDiv.textContent = 'Face verified!';
            statusDiv.classList.add('success');
            faceGuide.classList.add('detected');
            
            // Stop camera
            stopCamera();
            
            // Callback
            if (config.onSuccess) {
                config.onSuccess({
                    sessionToken: response.session_token,
                    phoneMasked: response.phone_masked,
                    nextStep: response.next_step
                });
            }
            
        } catch (error) {
            statusDiv.textContent = 'Verification failed';
            statusDiv.classList.add('error');
            
            showError(errorDiv, error.message || 'Face verification failed. Please try again.');
            
            if (config.onError) {
                config.onError(error);
            }
        } finally {
            captureBtn.disabled = false;
            captureBtn.innerHTML = '<span>Verify My Face</span>';
            captureBtn.classList.remove('loading');
        }
    }
    
    /**
     * Stop the camera stream
     */
    function stopCamera() {
        if (videoStream) {
            videoStream.getTracks().forEach(track => track.stop());
            videoStream = null;
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
     * Cleanup resources
     */
    function destroy() {
        stopCamera();
    }
    
    // Public API
    return {
        init,
        destroy
    };
})();

// Export for module environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MFAFaceVerify;
}

