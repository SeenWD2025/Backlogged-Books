import React, { useState, useEffect } from 'react';

const SettingsPage = () => {
  const [settings, setSettings] = useState({
    defaultCsvFormat: '3-column',
    defaultDateFormat: 'MM/DD/YYYY',
    autoRefresh: true,
    refreshInterval: 3,
  });

  const [isSaving, setIsSaving] = useState(false);
  const [isSaved, setIsSaved] = useState(false);

  // Load settings from localStorage on component mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('afspSettings');
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings));
    }
  }, []);

  const handleSettingChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSettings({
      ...settings,
      [name]: type === 'checkbox' ? checked : value,
    });
    // Clear saved message when user makes changes
    setIsSaved(false);
  };

  const handleSaveSettings = () => {
    setIsSaving(true);
    
    // Simulate API call with timeout
    setTimeout(() => {
      // Save settings to localStorage
      localStorage.setItem('afspSettings', JSON.stringify(settings));
      
      setIsSaving(false);
      setIsSaved(true);
      
      // Hide success message after 3 seconds
      setTimeout(() => {
        setIsSaved(false);
      }, 3000);
    }, 1000);
  };

  const handleResetToDefaults = () => {
    const defaultSettings = {
      defaultCsvFormat: '3-column',
      defaultDateFormat: 'MM/DD/YYYY',
      autoRefresh: true,
      refreshInterval: 3,
    };
    
    setSettings(defaultSettings);
    localStorage.setItem('afspSettings', JSON.stringify(defaultSettings));
    setIsSaved(true);
    
    // Hide success message after 3 seconds
    setTimeout(() => {
      setIsSaved(false);
    }, 3000);
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-gray-600">
          Configure your preferences for the application
        </p>
      </div>
      
      <div className="bg-white shadow sm:rounded-lg overflow-hidden">
        <div className="px-4 py-5 sm:p-6">
          <div className="grid grid-cols-1 gap-y-6">
            <div>
              <h2 className="text-lg font-medium text-gray-900">File Processing</h2>
              
              <div className="mt-4 space-y-4">
                <div className="flex flex-col">
                  <label htmlFor="defaultCsvFormat" className="block text-sm font-medium text-gray-700 mb-1">
                    Default CSV Format
                  </label>
                  <select
                    id="defaultCsvFormat"
                    name="defaultCsvFormat"
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                    value={settings.defaultCsvFormat}
                    onChange={handleSettingChange}
                  >
                    <option value="3-column">3-Column (Date, Description, Amount)</option>
                    <option value="4-column">4-Column (Date, Description, Debit, Credit)</option>
                  </select>
                  <p className="mt-1 text-sm text-gray-500">
                    Choose the default CSV format for QuickBooks imports
                  </p>
                </div>
                
                <div className="flex flex-col">
                  <label htmlFor="defaultDateFormat" className="block text-sm font-medium text-gray-700 mb-1">
                    Default Date Format
                  </label>
                  <select
                    id="defaultDateFormat"
                    name="defaultDateFormat"
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                    value={settings.defaultDateFormat}
                    onChange={handleSettingChange}
                  >
                    <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                    <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                  </select>
                  <p className="mt-1 text-sm text-gray-500">
                    Choose the default date format for output files
                  </p>
                </div>
              </div>
            </div>
            
            <div className="pt-6 border-t border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">Job Monitoring</h2>
              
              <div className="mt-4 space-y-4">
                <div className="flex items-start">
                  <div className="flex items-center h-5">
                    <input
                      id="autoRefresh"
                      name="autoRefresh"
                      type="checkbox"
                      className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
                      checked={settings.autoRefresh}
                      onChange={handleSettingChange}
                    />
                  </div>
                  <div className="ml-3 text-sm">
                    <label htmlFor="autoRefresh" className="font-medium text-gray-700">
                      Auto-refresh job status
                    </label>
                    <p className="text-gray-500">
                      Automatically refresh the job status page at regular intervals
                    </p>
                  </div>
                </div>
                
                {settings.autoRefresh && (
                  <div className="flex flex-col">
                    <label htmlFor="refreshInterval" className="block text-sm font-medium text-gray-700 mb-1">
                      Refresh Interval (seconds)
                    </label>
                    <input
                      type="number"
                      name="refreshInterval"
                      id="refreshInterval"
                      min="1"
                      max="30"
                      className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                      value={settings.refreshInterval}
                      onChange={handleSettingChange}
                    />
                  </div>
                )}
              </div>
            </div>
          </div>
          
          <div className="mt-8 flex justify-between">
            <button
              type="button"
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              onClick={handleResetToDefaults}
            >
              Reset to Defaults
            </button>
            <button
              type="button"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              onClick={handleSaveSettings}
              disabled={isSaving}
            >
              {isSaving ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Saving...
                </>
              ) : 'Save Settings'}
            </button>
          </div>
          
          {/* Success message */}
          {isSaved && (
            <div className="mt-4 bg-green-50 border border-green-200 rounded-md p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-green-800">
                    Settings saved successfully
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
