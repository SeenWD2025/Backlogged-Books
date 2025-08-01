import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Header = () => {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path ? 'bg-primary-100 text-primary-800' : 'text-gray-600 hover:bg-gray-100';
  };

  return (
    <header className="bg-white shadow">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold text-primary-700">
              AFSP
            </Link>
            <span className="ml-2 text-sm text-gray-500">Financial Document Processor</span>
          </div>
          <nav className="flex space-x-1">
            <Link
              to="/"
              className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/')}`}
            >
              Home
            </Link>
            <Link
              to="/upload"
              className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/upload')}`}
            >
              Upload
            </Link>
            <Link
              to="/jobs"
              className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/jobs')}`}
            >
              Jobs
            </Link>
            <Link
              to="/settings"
              className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/settings')}`}
            >
              Settings
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
