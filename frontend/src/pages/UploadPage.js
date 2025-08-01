import React from 'react';
import FileUpload from '../components/FileUpload';

const UploadPage = () => {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Upload Financial Document</h1>
        <p className="mt-2 text-gray-600">
          Upload your financial documents for processing and conversion to QuickBooks-compatible format.
        </p>
      </div>
      
      <FileUpload />
      
      <div className="mt-8 bg-white shadow sm:rounded-lg overflow-hidden">
        <div className="px-4 py-5 sm:p-6">
          <h2 className="text-lg font-medium text-gray-900">File Format Information</h2>
          <div className="mt-4 space-y-4">
            <div>
              <h3 className="font-medium text-gray-800">CSV Files</h3>
              <p className="text-sm text-gray-600">
                Our system accepts CSV files containing transaction data. The system will attempt to identify date, description, and amount columns automatically.
              </p>
            </div>
            
            <div>
              <h3 className="font-medium text-gray-800">PDF Bank Statements</h3>
              <p className="text-sm text-gray-600">
                Upload PDF bank statements and our system will extract transaction data automatically. For best results, ensure the PDF is text-based rather than scanned.
              </p>
            </div>
            
            <div>
              <h3 className="font-medium text-gray-800">Images (JPEG, PNG)</h3>
              <p className="text-sm text-gray-600">
                Upload receipt images in JPEG or PNG format. Our OCR technology will extract the relevant transaction data.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
