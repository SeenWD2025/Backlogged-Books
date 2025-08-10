import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Header = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout, isLoading } = useAuth();

  const isActive = (path) => {
    return location.pathname === path ? 'bg-primary-100 text-primary-800' : 'text-gray-600 hover:bg-gray-100';
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
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
          
          {/* Navigation */}
          <nav className="flex space-x-1 items-center">
            {/* Always show Home */}
            <Link
              to="/"
              className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/')}`}
            >
              Home
            </Link>
            
            {/* Authenticated User Navigation */}
            {user && (
              <>
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
                
                {/* User Menu */}
                <div className="flex items-center space-x-2 ml-4 pl-4 border-l border-gray-200">
                  <span className="text-sm text-gray-600">
                    Welcome, {user.email}
                  </span>
                  <button
                    onClick={handleLogout}
                    disabled={isLoading}
                    className="px-3 py-2 rounded-md text-sm font-medium text-red-600 hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? 'Logging out...' : 'Logout'}
                  </button>
                </div>
              </>
            )}
            
            {/* Unauthenticated User Navigation */}
            {!user && !isLoading && (
              <div className="flex items-center space-x-2 ml-4">
                <Link
                  to="/login"
                  className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/login')}`}
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="px-3 py-2 rounded-md text-sm font-medium bg-primary-600 text-white hover:bg-primary-700"
                >
                  Register
                </Link>
              </div>
            )}
            
            {/* Loading State */}
            {isLoading && (
              <div className="flex items-center space-x-2 ml-4">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
                <span className="text-sm text-gray-500">Loading...</span>
              </div>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
