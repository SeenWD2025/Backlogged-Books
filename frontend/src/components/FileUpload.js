import React, { useState, useRef } from 'react';
import { uploadFile } from '../services/api';
import { useNavigate } from 'react-router-dom';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [csvFormat, setCsvFormat] = useState('3-column');
  const [dateFormat, setDateFormat] = useState('MM/DD/YYYY');
  const fileInputRef = useRef(null);
  const navigate = useNavigate();
  
  const allowedFileTypes = ['csv', 'pdf', 'docx', 'jpg', 'jpeg', 'png'];

  const onFileChange = (event) => {
    const selectedFile = event.target.files[0];
    validateAndSetFile(selectedFile);
  };

  const validateAndSetFile = (selectedFile) => {
    setErrorMessage('');

    if (!selectedFile) {
      return;
    }

    // Check file type
    const fileExtension = selectedFile.name.split('.').pop().toLowerCase();
    if (!allowedFileTypes.includes(fileExtension)) {
      setErrorMessage(`Invalid file type. Allowed types: ${allowedFileTypes.join(', ')}`);
      return;
    }

    // Check file size (10MB max)
    if (selectedFile.size > 10 * 1024 * 1024) {
      setErrorMessage('File too large. Maximum size: 10MB');
      return;
    }

    setFile(selectedFile);
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    const droppedFile = e.dataTransfer.files[0];
    validateAndSetFile(droppedFile);
  };

  const handleUpload = async () => {
    if (!file) {
      setErrorMessage('Please select a file to upload');
      return;
    }

    setIsUploading(true);
    setErrorMessage('');

    try {
      const response = await uploadFile(file, csvFormat, dateFormat);
      // Redirect to job status page
      navigate(`/jobs/${response.job_id}`);
    } catch (error) {
      setErrorMessage(error.message || 'Failed to upload file');
    } finally {
      setIsUploading(false);
    }
  };

  const removeFile = () => {
    setFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="max-w-xl mx-auto">
      <div className="bg-white shadow sm:rounded-lg overflow-hidden">
        <div className="px-4 py-5 sm:p-6">
          <h2 className="text-lg font-medium text-gray-900">Upload Financial Document</h2>
          <p className="mt-1 text-sm text-gray-500">
            Upload a bank statement or receipt for processing. We support CSV, PDF, DOCX, JPEG, and PNG files.
          </p>

          {/* Drag & Drop Area */}
          <div 
            className={`mt-6 border-2 border-dashed rounded-md px-6 pt-5 pb-6 ${
              isDragging ? 'border-primary-500 bg-primary-50' : 'border-gray-300'
            }`}
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            <div className="space-y-1 text-center">
              <svg 
                className="mx-auto h-12 w-12 text-gray-400" 
                stroke="currentColor" 
                fill="none" 
                viewBox="0 0 48 48"
              >
                <path 
                  d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" 
                  strokeWidth="2" 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                />
              </svg>
              <div className="flex text-sm text-gray-600">
                <label 
                  htmlFor="file-upload" 
                  className="relative cursor-pointer rounded-md font-medium text-primary-600 hover:text-primary-500 focus-within:outline-none"
                >
                  <span>Upload a file</span>
                  <input 
                    id="file-upload" 
                    name="file-upload" 
                    type="file" 
                    className="sr-only" 
                    onChange={onFileChange} 
                    ref={fileInputRef}
                    accept={allowedFileTypes.map(ext => `.${ext}`).join(',')}
                  />
                </label>
                <p className="pl-1">or drag and drop</p>
              </div>
              <p className="text-xs text-gray-500">
                CSV, PDF, DOCX, JPEG, PNG up to 10MB
              </p>
            </div>

            {/* Selected file preview */}
            {file && (
              <div className="mt-4 flex items-center justify-between bg-gray-50 p-2 rounded">
                <div className="flex items-center">
                  <svg className="h-5 w-5 text-gray-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                  </svg>
                  <span className="text-sm font-medium text-gray-900 truncate" style={{ maxWidth: '250px' }}>
                    {file.name}
                  </span>
                </div>
                <button
                  type="button"
                  className="text-red-500 hover:text-red-700"
                  onClick={removeFile}
                >
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            )}
          </div>

          {/* Format options */}
          <div className="mt-6 grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
            <div>
              <label htmlFor="csv-format" className="block text-sm font-medium text-gray-700">
                QuickBooks CSV Format
              </label>
              <select
                id="csv-format"
                name="csv-format"
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                value={csvFormat}
                onChange={(e) => setCsvFormat(e.target.value)}
              >
                <option value="3-column">3-Column (Date, Description, Amount)</option>
                <option value="4-column">4-Column (Date, Description, Debit, Credit)</option>
              </select>
            </div>
            
            <div>
              <label htmlFor="date-format" className="block text-sm font-medium text-gray-700">
                Date Format
              </label>
              <select
                id="date-format"
                name="date-format"
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                value={dateFormat}
                onChange={(e) => setDateFormat(e.target.value)}
              >
                <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                <option value="DD/MM/YYYY">DD/MM/YYYY</option>
              </select>
            </div>
          </div>

          {/* Error message */}
          {errorMessage && (
            <div className="mt-4 text-sm text-red-600">
              {errorMessage}
            </div>
          )}

          {/* Upload button */}
          <div className="mt-6">
            <button
              type="button"
              className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 ${
                isUploading ? 'opacity-70 cursor-not-allowed' : ''
              }`}
              onClick={handleUpload}
              disabled={isUploading || !file}
            >
              {isUploading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Uploading...
                </>
              ) : 'Upload Document'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;
