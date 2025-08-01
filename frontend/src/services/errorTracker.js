// Frontend Error Monitoring Setup
// This file sets up error tracking for the AFSP frontend

// Error tracking wrapper class
class ErrorTracker {
  constructor() {
    this.initialized = false;
    this.errors = [];
    this.maxStoredErrors = 100;
    this.storageKey = 'afsp_error_logs';
    this.reportEndpoint = '/api/log-error'; // Replace with actual endpoint if available
  }

  // Initialize the error tracker
  init() {
    if (this.initialized) return;
    
    console.log('Initializing AFSP Error Tracker');
    
    // Load previously stored errors from localStorage
    this.loadStoredErrors();
    
    // Set up global error handler
    window.addEventListener('error', (event) => {
      this.trackError({
        type: 'uncaught',
        message: event.message,
        stack: event.error?.stack,
        source: event.filename,
        line: event.lineno,
        column: event.colno,
        timestamp: new Date().toISOString(),
        url: window.location.href,
      });
      
      // Let the default error handler run
      return false;
    });
    
    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.trackError({
        type: 'unhandledrejection',
        message: event.reason?.message || 'Unhandled Promise Rejection',
        stack: event.reason?.stack,
        timestamp: new Date().toISOString(),
        url: window.location.href,
      });
    });
    
    // Set up console error tracking
    const originalConsoleError = console.error;
    console.error = (...args) => {
      const message = args.map(arg => {
        if (typeof arg === 'object' && arg !== null) {
          try {
            return JSON.stringify(arg);
          } catch (e) {
            return String(arg);
          }
        }
        return String(arg);
      }).join(' ');
      
      this.trackError({
        type: 'console',
        message,
        timestamp: new Date().toISOString(),
        url: window.location.href,
      });
      
      // Call the original console.error
      originalConsoleError.apply(console, args);
    };
    
    // Mark as initialized
    this.initialized = true;
    
    // Set up periodic error reporting
    this.setupPeriodicReporting();
  }
  
  // Track an error
  trackError(error) {
    // Add to in-memory error list
    this.errors.push(error);
    if (this.errors.length > this.maxStoredErrors) {
      this.errors.shift();
    }
    
    // Store in localStorage
    this.storeErrors();
    
    // Report immediately if critical error
    if (error.type === 'uncaught') {
      this.reportErrors([error]);
    }
  }
  
  // Store errors in localStorage
  storeErrors() {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.errors));
    } catch (e) {
      console.warn('Failed to store errors in localStorage', e);
    }
  }
  
  // Load stored errors from localStorage
  loadStoredErrors() {
    try {
      const storedErrors = localStorage.getItem(this.storageKey);
      if (storedErrors) {
        this.errors = JSON.parse(storedErrors);
      }
    } catch (e) {
      console.warn('Failed to load stored errors from localStorage', e);
    }
  }
  
  // Set up periodic error reporting
  setupPeriodicReporting() {
    setInterval(() => {
      if (this.errors.length > 0) {
        this.reportErrors(this.errors);
      }
    }, 60000); // Report every minute if there are errors
  }
  
  // Report errors to the backend
  reportErrors(errors) {
    // Skip if no errors to report or no network connection
    if (errors.length === 0 || !navigator.onLine) return;
    
    // Add user agent and other metadata
    const payload = {
      errors,
      metadata: {
        userAgent: navigator.userAgent,
        timestamp: new Date().toISOString(),
        url: window.location.href,
        screenSize: {
          width: window.innerWidth,
          height: window.innerHeight,
        },
      },
    };
    
    // Send to backend if available, otherwise just log
    try {
      fetch(this.reportEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      }).then(response => {
        if (response.ok) {
          // Clear reported errors on successful report
          this.errors = [];
          this.storeErrors();
        }
      }).catch(e => {
        console.warn('Failed to report errors to backend', e);
      });
    } catch (e) {
      console.warn('Failed to send error report', e);
    }
  }
  
  // Manually track an error or event
  track(category, message, data = {}) {
    this.trackError({
      type: 'manual',
      category,
      message,
      data,
      timestamp: new Date().toISOString(),
      url: window.location.href,
    });
  }
  
  // Get all stored errors
  getErrors() {
    return [...this.errors];
  }
  
  // Clear all stored errors
  clearErrors() {
    this.errors = [];
    this.storeErrors();
  }
}

// Create singleton instance
const errorTracker = new ErrorTracker();

// Export for use in the application
export default errorTracker;
