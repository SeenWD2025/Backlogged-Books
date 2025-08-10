import React, { useState, useEffect } from 'react';
import { useSearchParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const EmailVerificationPage = () => {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState('verifying'); // 'verifying', 'success', 'error', 'expired'
  const [message, setMessage] = useState('');
  const { verifyEmail } = useAuth();
  const navigate = useNavigate();

  const token = searchParams.get('token');
  const userId = searchParams.get('user');

  useEffect(() => {
    const performVerification = async () => {
      if (!token) {
        setStatus('error');
        setMessage('Verification token is missing from the URL.');
        return;
      }

      try {
        setStatus('verifying');
        const result = await verifyEmail(token);
        
        if (result.success) {
          setStatus('success');
          setMessage('Your email has been successfully verified! You can now log in to your account.');
          
          // Redirect to login page after 3 seconds
          setTimeout(() => {
            navigate('/login', { 
              state: { 
                message: 'Email verified successfully! Please log in.',
                type: 'success'
              }
            });
          }, 3000);
        } else {
          setStatus('error');
          if (result.error.includes('expired') || result.error.includes('invalid')) {
            setStatus('expired');
            setMessage('This verification link has expired or is invalid. Please request a new verification email.');
          } else {
            setMessage(result.error || 'Email verification failed. Please try again.');
          }
        }
      } catch (error) {
        setStatus('error');
        setMessage('An unexpected error occurred during verification. Please try again.');
        console.error('Email verification error:', error);
      }
    };

    performVerification();
  }, [token, verifyEmail, navigate]);

  const handleResendVerification = async () => {
    if (!userId) {
      setMessage('Cannot resend verification - user ID is missing.');
      return;
    }

    try {
      // This would call an API endpoint to resend verification
      setMessage('A new verification email has been sent to your email address.');
    } catch (error) {
      setMessage('Failed to resend verification email. Please try again later.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Email Verification
        </h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {status === 'verifying' && (
            <div className="text-center">
              <div className="flex justify-center mb-4">
                <svg className="animate-spin h-12 w-12 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Verifying your email...
              </h3>
              <p className="text-gray-600">
                Please wait while we verify your email address.
              </p>
            </div>
          )}

          {status === 'success' && (
            <div className="text-center">
              <div className="flex justify-center mb-4">
                <svg className="h-12 w-12 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Email Verified Successfully!
              </h3>
              <p className="text-gray-600 mb-4">
                {message}
              </p>
              <p className="text-sm text-gray-500">
                You will be redirected to the login page in a few seconds...
              </p>
            </div>
          )}

          {(status === 'error' || status === 'expired') && (
            <div className="text-center">
              <div className="flex justify-center mb-4">
                <svg className="h-12 w-12 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {status === 'expired' ? 'Verification Link Expired' : 'Verification Failed'}
              </h3>
              <p className="text-gray-600 mb-6">
                {message}
              </p>
              
              <div className="space-y-4">
                {status === 'expired' && (
                  <button
                    onClick={handleResendVerification}
                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Resend Verification Email
                  </button>
                )}
                
                <Link
                  to="/register"
                  className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Create New Account
                </Link>
              </div>
            </div>
          )}

          <div className="mt-6 text-center">
            <Link
              to="/"
              className="text-sm text-gray-600 hover:text-gray-500"
            >
              Back to home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailVerificationPage;
