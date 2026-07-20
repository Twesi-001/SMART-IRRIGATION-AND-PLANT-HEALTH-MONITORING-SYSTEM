/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import toast from 'react-hot-toast';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    
    // Basic validation
    if (!username.trim() || !password.trim()) {
      setError('Please enter both username and password');
      setLoading(false);
      return;
    }

    try {
      await login(username, password);
      toast.success('Login successful! Welcome back.');
      navigate('/dashboard');
    } catch (error: any) {
      console.error('Login failed:', error);
      
      // Handle different error types
      if (error.response?.status === 401) {
        setError('Invalid username or password. Please try again.');
        toast.error('Invalid credentials');
      } else if (error.response?.status === 404) {
        setError('User not found. Please check your username.');
        toast.error('User not found');
      } else if (error.response?.data?.error) {
        setError(error.response.data.error);
        toast.error(error.response.data.error);
      } else if (error.message === 'Network Error') {
        setError('Cannot connect to server. Please check your internet connection.');
        toast.error('Network error');
      } else {
        setError('Login failed. Please try again later.');
        toast.error('Login failed');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-500 to-green-700">
      <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">🌱 Smart Irrigation</h1>
          <p className="text-gray-600 mt-2">Plant Health Monitoring System</p>
        </div>
        
        {/* Error Message */}
        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg text-sm">
            ❌ {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 ${
                error ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Enter username"
              required
              disabled={loading}
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 ${
                error ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Enter password"
              required
              disabled={loading}
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-green-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-green-700 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        
        <div className="mt-4 text-center text-sm text-gray-600">
          <p>Demo: <span className="font-medium">testuser</span> / <span className="font-medium">test123</span></p>
        </div>

        {/* Signup Link */}
        <div className="mt-4 text-center text-sm text-gray-600 border-t pt-4">
          Don't have an account?{' '}
          <Link to="/signup" className="text-green-600 hover:text-green-800 font-medium">
            Sign up
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Login;