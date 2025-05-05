import React, { useState, useEffect } from 'react';

export default function DashboardDebug() {
  const [userStatus, setUserStatus] = useState('Checking...');
  const [localStorageData, setLocalStorageData] = useState({});
  const [apiResults, setApiResults] = useState({});
  const [errorMessages, setErrorMessages] = useState([]);

  useEffect(() => {
    // Check localStorage on load
    checkLocalStorage();
    
    // Check if we got here via the redirect test
    const redirectTest = localStorage.getItem('redirectTest');
    if (redirectTest) {
      setUserStatus(`Redirect test successful! Timestamp: ${redirectTest}`);
      
      // Clear the test flag
      localStorage.removeItem('redirectTest');
    }
  }, []);

  function checkLocalStorage() {
    const user = localStorage.getItem('user');
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    
    setLocalStorageData({
      user: user ? JSON.parse(user) : null,
      isLoggedIn: isLoggedIn === 'true'
    });
    
    if (isLoggedIn === 'true' && user) {
      setUserStatus('User found in localStorage');
    } else {
      setUserStatus('No user found in localStorage');
    }
  }

  async function checkApiAuth() {
    try {
      const results = {};
      
      // Check auth status endpoint
      try {
        const authResponse = await fetch('http://localhost:5000/api/auth-status', {
          credentials: 'include'
        });
        
        results.authStatus = {
          status: authResponse.status,
          data: await authResponse.json()
        };
      } catch (error) {
        results.authStatus = {
          error: error.message
        };
        setErrorMessages(prev => [...prev, `Auth status check failed: ${error.message}`]);
      }
      
      // Check the API user endpoint
      try {
        const userResponse = await fetch('http://localhost:5000/auth/api/user', {
          credentials: 'include'
        });
        
        if (userResponse.ok) {
          results.userApi = {
            status: userResponse.status,
            data: await userResponse.json()
          };
        } else {
          results.userApi = {
            status: userResponse.status,
            error: 'Failed to fetch user data'
          };
        }
      } catch (error) {
        results.userApi = {
          error: error.message
        };
        setErrorMessages(prev => [...prev, `User API check failed: ${error.message}`]);
      }
      
      // Try the test recipes endpoint
      try {
        const recipesResponse = await fetch('http://localhost:5000/api/test-recipes', {
          credentials: 'include'
        });
        
        results.testRecipes = {
          status: recipesResponse.status,
          data: await recipesResponse.json()
        };
      } catch (error) {
        results.testRecipes = {
          error: error.message
        };
        setErrorMessages(prev => [...prev, `Test recipes check failed: ${error.message}`]);
      }
      
      setApiResults(results);
      
      // Update status based on results
      if (results.authStatus?.data?.authenticated) {
        setUserStatus('Authenticated with API');
      } else if (results.userApi?.data) {
        setUserStatus('User API returned data');
      } else {
        setUserStatus('Not authenticated with API');
      }
      
    } catch (error) {
      console.error('API check error:', error);
      setErrorMessages(prev => [...prev, `Overall API check failed: ${error.message}`]);
    }
  }

  function clearErrors() {
    setErrorMessages([]);
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center py-12 px-4">
      <div className="max-w-2xl w-full space-y-8 bg-white p-6 rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-center">Dashboard Debug Page</h1>
        
        <div className="text-center mb-4">
          <div className="font-semibold">Status: <span className="text-blue-600">{userStatus}</span></div>
          
          {errorMessages.length > 0 && (
            <div className="mt-2 text-red-600 text-sm">
              {errorMessages.map((msg, i) => (
                <div key={i}>{msg}</div>
              ))}
              <button 
                onClick={clearErrors}
                className="text-xs text-gray-500 underline mt-1"
              >
                Clear Errors
              </button>
            </div>
          )}
        </div>
        
        <div className="space-y-4">
          <button
            onClick={checkLocalStorage}
            className="w-full py-2 px-4 bg-green-600 text-white rounded-md hover:bg-green-700"
          >
            Check LocalStorage
          </button>
          
          <button
            onClick={checkApiAuth}
            className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Check API Authentication
          </button>
          
          <a
            href="/dashboard"
            className="block w-full py-2 px-4 bg-purple-600 text-white rounded-md hover:bg-purple-700 text-center"
          >
            Go to Dashboard
          </a>
          
          <a
            href="/login-debug"
            className="block w-full py-2 px-4 bg-gray-600 text-white rounded-md hover:bg-gray-700 text-center"
          >
            Go to Login Debug
          </a>
        </div>
        
        {localStorageData.user && (
          <div className="mt-6 border-t pt-4">
            <h2 className="text-lg font-semibold mb-2">LocalStorage User Data:</h2>
            <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto">
              {JSON.stringify(localStorageData.user, null, 2)}
            </pre>
            <div className="mt-2 text-sm">
              <span className="font-medium">isLoggedIn flag:</span> {String(localStorageData.isLoggedIn)}
            </div>
          </div>
        )}
        
        {Object.keys(apiResults).length > 0 && (
          <div className="mt-6 border-t pt-4">
            <h2 className="text-lg font-semibold mb-2">API Check Results:</h2>
            <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto">
              {JSON.stringify(apiResults, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}