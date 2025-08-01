import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import errorTracker from './services/errorTracker';

// Initialize error tracking
errorTracker.init();

// Initialize accessibility testing in development
if (process.env.NODE_ENV !== 'production') {
  // Check if axe-core is available (it would be installed as a dev dependency)
  import('@axe-core/react')
    .then(axe => {
      axe.default(React, ReactDOM, 1000);
      console.log('Accessibility testing enabled');
    })
    .catch(err => {
      console.log('Accessibility testing not available: run npm install --save-dev @axe-core/react');
    });
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Track performance metrics
reportWebVitals(metric => {
  // Log metrics to console in development
  if (process.env.NODE_ENV !== 'production') {
    console.log(metric);
  }
  
  // Track important performance metrics
  if (metric.value > 1000) { // Only track slow metrics
    errorTracker.track('performance', `Slow ${metric.name}`, metric);
  }
});
