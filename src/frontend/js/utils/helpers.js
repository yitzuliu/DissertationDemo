/**
 * Helper Utilities Module
 * Common utility functions used throughout the application
 */

/**
 * Show error message in the UI
 * @param {string} message - Error message to display
 */
export function showError(message) {
    const errorMsg = document.getElementById('errorMsg');
    console.log('🔍 showError called:', { message, element: errorMsg });
    if (errorMsg) {
        errorMsg.textContent = message;
        errorMsg.style.display = "block";
        console.log('✅ Error message displayed:', message);
    } else {
        console.warn('❌ Error message element not found');
    }
}

/**
 * Hide error message in the UI
 */
export function hideError() {
    const errorMsg = document.getElementById('errorMsg');
    if (errorMsg) {
        errorMsg.style.display = "none";
    }
}

/**
 * Add loading state to elements
 * @param {...HTMLElement} elements - Elements to add loading state to
 */
export function setLoadingState(...elements) {
    elements.forEach(element => {
        if (element) {
            element.classList.add('shimmer');
        }
    });
}

/**
 * Remove loading state from elements
 * @param {...HTMLElement} elements - Elements to remove loading state from
 */
export function removeLoadingState(...elements) {
    elements.forEach(element => {
        if (element) {
            element.classList.remove('shimmer');
        }
    });
}

/**
 * Debounce function to limit function calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function to limit function calls
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} Throttled function
 */
export function throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Format timestamp for display
 * @param {Date} date - Date object
 * @returns {string} Formatted time string
 */
export function formatTime(date = new Date()) {
    return date.toLocaleTimeString();
}

/**
 * Validate capture interval value
 * @param {string|number} interval - Interval value to validate
 * @param {number} defaultInterval - Default interval if validation fails
 * @returns {number} Valid interval in milliseconds
 */
export function validateCaptureInterval(interval, defaultInterval = 2000) {
    const intervalTime = parseInt(interval, 10);
    if (isNaN(intervalTime) || intervalTime < 100) {
        console.log("Invalid interval value, using default interval");
        return defaultInterval;
    }
    return intervalTime;
}

/**
 * Get optimal capture interval based on model and form validation
 * @param {string} modelName - Active model name
 * @param {number} selectedInterval - User selected interval
 * @returns {number} Optimal interval in milliseconds
 */
export function getOptimalInterval(modelName, selectedInterval) {
    const defaultInterval = 2000;
    
    // Return default if no selection or "none" selected
    if (!selectedInterval || selectedInterval === "none") {
        console.log("No valid interval config selected, using default interval");
        return defaultInterval;
    }
    
    // Parse and validate the selected interval
    const intervalTime = parseInt(selectedInterval, 10);
    if (isNaN(intervalTime) || intervalTime < 100) {
        console.log("Invalid interval value, using default interval");
        return defaultInterval;
    }
    
    // Adjust minimum intervals for optimized models
    if (modelName === "smolvlm2_500m_video_optimized") {
        return Math.max(intervalTime, 3000); // Minimum 3 seconds
    } else if (modelName === "smolvlm2_500m_video") {
        return Math.max(intervalTime, 5000); // Minimum 5 seconds
    }
    
    return intervalTime;
}

/**
 * Create a promise that resolves after a delay
 * @param {number} ms - Delay in milliseconds
 * @returns {Promise} Promise that resolves after delay
 */
export function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Check if an element is visible in the viewport
 * @param {HTMLElement} element - Element to check
 * @returns {boolean} True if element is visible
 */
export function isElementVisible(element) {
    if (!element) return false;
    
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Safely get DOM element by ID
 * @param {string} id - Element ID
 * @returns {HTMLElement|null} Element or null if not found
 */
export function getElementById(id) {
    const element = document.getElementById(id);
    if (!element) {
        console.warn(`Element with ID '${id}' not found`);
    }
    return element;
}

/**
 * Safely query selector
 * @param {string} selector - CSS selector
 * @param {HTMLElement} parent - Parent element (optional)
 * @returns {HTMLElement|null} Element or null if not found
 */
export function querySelector(selector, parent = document) {
    const element = parent.querySelector(selector);
    if (!element) {
        console.warn(`Element with selector '${selector}' not found`);
    }
    return element;
}

/**
 * Add event listener with error handling
 * @param {HTMLElement} element - Element to add listener to
 * @param {string} event - Event type
 * @param {Function} handler - Event handler
 * @param {Object} options - Event listener options
 */
export function addEventListenerSafe(element, event, handler, options = {}) {
    if (!element) {
        console.warn(`Cannot add event listener: element is null`);
        return;
    }
    
    const safeHandler = (e) => {
        try {
            handler(e);
        } catch (error) {
            console.error(`Error in event handler for ${event}:`, error);
        }
    };
    
    element.addEventListener(event, safeHandler, options);
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} True if successful
 */
export async function copyToClipboard(text) {
    try {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
            return true;
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            const result = document.execCommand('copy');
            textArea.remove();
            return result;
        }
    } catch (error) {
        console.error('Failed to copy text to clipboard:', error);
        return false;
    }
}