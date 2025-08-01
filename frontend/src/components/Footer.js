import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-white py-6 shadow-inner">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <p className="text-sm text-gray-500">
              &copy; {new Date().getFullYear()} Automated Financial Statement Processor
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">
              <span className="font-medium">Local Application</span> - No data is sent to external servers
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
