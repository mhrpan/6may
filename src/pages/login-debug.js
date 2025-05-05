import React, { useState, useEffect } from 'react';

export default function LoginDebug() {
  const [loginStatus, setLoginStatus] = useState('Not started');
  const [userData, setUserData] = useState(null);
  const [authCheckResult, setAuthCheckResult] = useState(null);
  const [redirectResult, setRedirectResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  // Test credentials
  const credentials = {
    email: 'admin@recipekeeper.com',
    password: 'admin123'
  };

  async function checkAuthStatus() {
    setLoginStatus('Checking auth status...');
    try {
      const response = await fetch('http://localhost:5000/api/auth-status', {
        credentials: 'include'
      });
      
      const result = await response.json();
      setAuthCheckResult(result);
      
      if (result.authenticated) {
        setLoginStatus('Already authenticated!');
        setUserData(result.user);
        return true;
      } else {
        setLoginStatus('Not authenticated, will try to login');
        return false;
      }
    } catch (error) {
      console.error('Auth check error:', error);
      setErrorMessage(`Auth check error: ${error.message}`);
      setLoginStatus('Auth check failed');
      return false;
    }
  }

  async function attemptLogin() {
    setLoginStatus('Attempting login...');
    try {
      const response = await fetch('http://localhost:5000/auth/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
        credentials: 'include'
      });
      
      const result = await response.json();
      
      if (result.status === 'success') {
        setLoginStatus('Login successful!');
        setUserData(result.user);
        
        // Store in localStorage
        localStorage.setItem('user', JSON.stringify(result.user));
        localStorage.setItem('isLoggedIn', 'true');
        
        // Check auth status again to confirm
        setTimeout(() => {
          checkAuthStatus();
        }, 500);
        
        return true;
      } else {
        setLoginStatus('Login failed');
        setErrorMessage(result.message || 'Unknown error');
        return false;
      }
    } catch (error) {
      console.error('Login error:', error);
      setErrorMessage(`Login error: ${error.message}`);
      setLoginStatus('Login failed');
      return false;
    }
  }

  async function attemptRedirect() {
    setLoginStatus('Attempting redirect...');
    try {
      // Set a message in localStorage that we'll check for on the dashboard
      localStorage.setItem('redirectTest', new Date().toISOString());
      
      // Try to redirect
      window.location.href = '/dashboard';
      setRedirectResult('Redirect initiated');
      
      return true;
    } catch (error) {
      console.error('Redirect error:', error);
      setErrorMessage(`Redirect error: ${error.message}`);
      setLoginStatus('Redirect failed');
      return false;
    }
  }

  async function runLoginProcess() {
    // First check if already authenticated
    const isAuthenticated = await checkAuthStatus();
    
    if (!isAuthenticated) {
      // Try to login
      const loginSuccess = await attemptLogin();
      
      if (loginSuccess) {
        // Try to redirect to dashboard
        await attemptRedirect();
      }
    } else {
      // Already authenticated, just redirect
      await attemptRedirect();
    }
  }

  // Button handler
  function handleLoginClick() {
    runLoginProcess();
  }

  function handleClearLocalStorage() {
    localStorage.clear();
    setLoginStatus('Local storage cleared');
    setUserData(null);
    setAuthCheckResult(null);
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center py-12 px-4">
      <div className="max-w-md w-full space-y-8 bg-white p-6 rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-center">Login Debug Page</h1>
        
        <div className="text-center mb-4">
          <div className="font-semibold">Status: <span className="text-blue-600">{loginStatus}</span></div>
          {errorMessage && <div className="text-red-600 mt-2">{errorMessage}</div>}
        </div>
        
        <div className="space-y-4">
          <button
            onClick={handleLoginClick}
            className="w-full py-2 px-4 bg-green-600 text-white rounded-md hover:bg-green-700"
          >
            Login as Admin + Redirect
          </button>
          
          <button
            onClick={checkAuthStatus}
            className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Check Auth Status
          </button>
          
          <button
            onClick={handleClearLocalStorage}
            className="w-full py-2 px-4 bg-red-600 text-white rounded-md hover:bg-red-700"
          >
            Clear LocalStorage
          </button>
          
          <button
            onClick={attemptRedirect}
            className="w-full py-2 px-4 bg-purple-600 text-white rounded-md hover:bg-purple-700"
          >
            Direct Redirect
          </button>
        </div>
        
        {userData && (
          <div className="mt-6 border-t pt-4">
            <h2 className="text-lg font-semibold mb-2">User Data:</h2>
            <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto">
              {JSON.stringify(userData, null, 2)}
            </pre>
          </div>
        )}
        
        {authCheckResult && (
          <div className="mt-6 border-t pt-4">
            <h2 className="text-lg font-semibold mb-2">Auth Check Result:</h2>
            <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto">
              {JSON.stringify(authCheckResult, null, 2)}
            </pre>
          </div>
        )}
        
        <div className="mt-6 text-center text-sm text-gray-600">
          <p>Using credentials: {credentials.email} / {credentials.password}</p>
        </div>
      </div>
    </div>
  );
}