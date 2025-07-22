/**
 * Tab Management Module
 * Handles tab switching functionality in the sidebar
 */

import { addEventListenerSafe } from '../utils/helpers.js';

class TabManager {
    constructor() {
        this.tabButtons = [];
        this.tabPanels = [];
        this.activeTab = null;
        this.isInitialized = false;
    }

    /**
     * Initialize tab manager
     */
    initialize() {
        // Get tab buttons and panels
        this.tabButtons = document.querySelectorAll('.tab-btn');
        this.tabPanels = document.querySelectorAll('.tab-panel');

        console.log('🔍 Tab initialization:', {
            buttons: this.tabButtons.length,
            panels: this.tabPanels.length,
            buttonElements: Array.from(this.tabButtons).map(btn => ({
                target: btn.getAttribute('data-target'),
                text: btn.textContent.trim()
            })),
            panelElements: Array.from(this.tabPanels).map(panel => ({
                id: panel.id,
                display: panel.style.display
            }))
        });

        if (this.tabButtons.length === 0 || this.tabPanels.length === 0) {
            console.warn('No tabs found to initialize');
            return;
        }

        // Set up event listeners
        this.setupEventListeners();

        // Set initial active tab
        this.setInitialActiveTab();

        this.isInitialized = true;
        console.log('✅ Tab manager initialized successfully');
    }

    /**
     * Set up event listeners for tab buttons
     */
    setupEventListeners() {
        this.tabButtons.forEach(btn => {
            addEventListenerSafe(btn, 'click', () => {
                const targetId = btn.getAttribute('data-target');
                this.switchToTab(targetId);
            });

            // Add hover effect
            addEventListenerSafe(btn, 'mouseenter', () => {
                if (!btn.classList.contains('active-tab')) {
                    btn.style.opacity = '0.85';
                }
            });

            addEventListenerSafe(btn, 'mouseleave', () => {
                if (!btn.classList.contains('active-tab')) {
                    btn.style.opacity = '0.6';
                }
            });
        });
    }

    /**
     * Set the initial active tab
     */
    setInitialActiveTab() {
        console.log('🔧 Setting initial active tab...');
        
        // Find the first tab button with active-tab class
        const activeButton = Array.from(this.tabButtons).find(btn => 
            btn.classList.contains('active-tab')
        );

        if (activeButton) {
            const targetId = activeButton.getAttribute('data-target');
            console.log('📌 Found active tab button, switching to:', targetId);
            this.switchToTab(targetId, false); // Don't animate initial switch
        } else if (this.tabButtons.length > 0) {
            // If no active tab found, activate the first one
            const firstButton = this.tabButtons[0];
            const targetId = firstButton.getAttribute('data-target');
            console.log('📌 No active tab found, activating first tab:', targetId);
            
            // Set the first button as active
            firstButton.classList.add('active-tab');
            firstButton.style.opacity = '1';
            firstButton.style.borderBottom = '2px solid var(--primary)';
            
            this.switchToTab(targetId, false);
        }
    }

    /**
     * Switch to a specific tab
     * @param {string} targetId - ID of the target tab panel
     * @param {boolean} animate - Whether to animate the transition
     */
    switchToTab(targetId, animate = true) {
        console.log('🔄 Switching to tab:', targetId);
        
        if (!targetId) {
            console.warn('No target ID provided for tab switch');
            return;
        }

        const targetPanel = document.getElementById(targetId);
        if (!targetPanel) {
            console.warn(`Tab panel with ID '${targetId}' not found`);
            return;
        }

        console.log('📋 Tab switch details:', {
            targetId,
            targetPanel: targetPanel.id,
            currentDisplay: targetPanel.style.display,
            allPanels: Array.from(this.tabPanels).map(p => ({
                id: p.id,
                display: p.style.display,
                classes: p.className
            }))
        });

        // Hide all panels
        this.tabPanels.forEach(panel => {
            panel.style.display = 'none';
            panel.classList.remove('active');
        });

        // Show target panel
        targetPanel.style.display = 'block';
        targetPanel.classList.add('active');

        // Add animation if requested
        if (animate) {
            targetPanel.classList.add('animate-fade-in');
            // Remove animation class after animation completes
            setTimeout(() => {
                targetPanel.classList.remove('animate-fade-in');
            }, 300);
        }

        // Update tab button styles
        this.updateTabButtonStyles(targetId);

        // Update active tab reference
        this.activeTab = targetId;

        // Trigger custom event
        this.dispatchTabChangeEvent(targetId);
        
        console.log('✅ Tab switched successfully to:', targetId);
    }

    /**
     * Update tab button styles
     * @param {string} activeTargetId - ID of the active tab panel
     */
    updateTabButtonStyles(activeTargetId) {
        this.tabButtons.forEach(btn => {
            const targetId = btn.getAttribute('data-target');
            
            if (targetId === activeTargetId) {
                // Set active tab style
                btn.classList.add('active-tab');
                btn.style.opacity = '1';
                btn.style.borderBottom = '2px solid var(--primary)';
            } else {
                // Set inactive tab style
                btn.classList.remove('active-tab');
                btn.style.opacity = '0.6';
                btn.style.borderBottom = 'none';
            }
        });
    }

    /**
     * Dispatch custom tab change event
     * @param {string} tabId - ID of the new active tab
     */
    dispatchTabChangeEvent(tabId) {
        const event = new CustomEvent('tabchange', {
            detail: {
                activeTab: tabId,
                previousTab: this.activeTab
            }
        });
        document.dispatchEvent(event);
    }

    /**
     * Get the currently active tab ID
     * @returns {string|null} Active tab ID
     */
    getActiveTab() {
        return this.activeTab;
    }

    /**
     * Check if a specific tab is active
     * @param {string} tabId - Tab ID to check
     * @returns {boolean} True if tab is active
     */
    isTabActive(tabId) {
        return this.activeTab === tabId;
    }

    /**
     * Add a new tab programmatically
     * @param {string} tabId - ID for the new tab
     * @param {string} title - Title for the tab button
     * @param {string} content - HTML content for the tab panel
     * @param {string} icon - Font Awesome icon class (optional)
     */
    addTab(tabId, title, content, icon = '') {
        // Create tab button
        const tabButton = document.createElement('h2');
        tabButton.className = 'tab-btn';
        tabButton.setAttribute('data-target', tabId);
        tabButton.style.cssText = 'margin: 0; flex: 1; text-align: center; padding: 0.25rem; opacity: 0.6; cursor: pointer; font-size: 0.8rem;';
        
        const iconHtml = icon ? `<i class="${icon}"></i> ` : '';
        tabButton.innerHTML = `${iconHtml}${title}`;

        // Create tab panel
        const tabPanel = document.createElement('div');
        tabPanel.id = tabId;
        tabPanel.className = 'tab-panel';
        tabPanel.style.display = 'none';
        tabPanel.innerHTML = content;

        // Add to DOM
        const tabsHeader = document.querySelector('.tabs-header');
        const tabContent = document.querySelector('.tab-content');

        if (tabsHeader && tabContent) {
            tabsHeader.appendChild(tabButton);
            tabContent.appendChild(tabPanel);

            // Update internal arrays
            this.tabButtons = document.querySelectorAll('.tab-btn');
            this.tabPanels = document.querySelectorAll('.tab-panel');

            // Set up event listener for new button
            addEventListenerSafe(tabButton, 'click', () => {
                this.switchToTab(tabId);
            });

            return true;
        }

        return false;
    }

    /**
     * Remove a tab
     * @param {string} tabId - ID of the tab to remove
     */
    removeTab(tabId) {
        const tabButton = document.querySelector(`[data-target="${tabId}"]`);
        const tabPanel = document.getElementById(tabId);

        if (tabButton) {
            tabButton.remove();
        }

        if (tabPanel) {
            tabPanel.remove();
        }

        // Update internal arrays
        this.tabButtons = document.querySelectorAll('.tab-btn');
        this.tabPanels = document.querySelectorAll('.tab-panel');

        // If removed tab was active, switch to first available tab
        if (this.activeTab === tabId && this.tabButtons.length > 0) {
            const firstButton = this.tabButtons[0];
            const firstTargetId = firstButton.getAttribute('data-target');
            this.switchToTab(firstTargetId);
        }
    }

    /**
     * Update tab content
     * @param {string} tabId - ID of the tab to update
     * @param {string} content - New HTML content
     */
    updateTabContent(tabId, content) {
        const tabPanel = document.getElementById(tabId);
        if (tabPanel) {
            tabPanel.innerHTML = content;
            return true;
        }
        return false;
    }

    /**
     * Check if tab manager is initialized
     * @returns {boolean} True if initialized
     */
    isReady() {
        return this.isInitialized;
    }

    /**
     * Get all tab IDs
     * @returns {Array<string>} Array of tab IDs
     */
    getAllTabIds() {
        return Array.from(this.tabButtons).map(btn => 
            btn.getAttribute('data-target')
        ).filter(id => id);
    }

    /**
     * Enable or disable a tab
     * @param {string} tabId - Tab ID
     * @param {boolean} enabled - Whether tab should be enabled
     */
    setTabEnabled(tabId, enabled) {
        const tabButton = document.querySelector(`[data-target="${tabId}"]`);
        if (tabButton) {
            if (enabled) {
                tabButton.style.pointerEvents = 'auto';
                tabButton.style.opacity = this.isTabActive(tabId) ? '1' : '0.6';
            } else {
                tabButton.style.pointerEvents = 'none';
                tabButton.style.opacity = '0.3';
            }
        }
    }
}

// Export singleton instance
export const tabManager = new TabManager();