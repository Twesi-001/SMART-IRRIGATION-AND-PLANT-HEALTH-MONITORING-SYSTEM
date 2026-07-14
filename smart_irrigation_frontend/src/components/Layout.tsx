import React, { ReactNode, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { 
  HomeIcon, 
  PowerIcon,
  BellIcon,
  UserCircleIcon,
  Bars3Icon,
  XMarkIcon
} from '@heroicons/react/24/outline';

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Navbar */}
      <nav className="bg-white shadow-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo - Always visible */}
            <div className="flex items-center">
              <h1 className="text-lg sm:text-xl font-bold text-green-700">
                🌱 Smart Irrigation
              </h1>
            </div>

            {/* Desktop Navigation - Hidden on mobile */}
            <div className="hidden md:flex items-center space-x-4">
              <button 
                onClick={() => navigate('/dashboard')}
                className="text-gray-700 hover:text-green-700 px-3 py-2 rounded-md text-sm font-medium flex items-center"
              >
                <HomeIcon className="h-5 w-5 mr-1" />
                Dashboard
              </button>
            </div>

            {/* Right side - Always visible */}
            <div className="flex items-center space-x-2 sm:space-x-4">
              <BellIcon className="h-5 w-5 sm:h-6 sm:w-6 text-gray-500 hover:text-gray-700 cursor-pointer" />
              
              {/* User info - Hidden on very small screens */}
              <div className="hidden xs:flex items-center space-x-2">
                <UserCircleIcon className="h-6 w-6 sm:h-8 sm:w-8 text-gray-500" />
                <span className="text-xs sm:text-sm text-gray-700 hidden sm:inline">
                  {user?.username}
                </span>
              </div>

              {/* Logout button */}
              <button
                onClick={handleLogout}
                className="text-gray-500 hover:text-red-600 transition p-1"
              >
                <PowerIcon className="h-5 w-5 sm:h-6 sm:w-6" />
              </button>

              {/* Mobile menu button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-1 text-gray-500 hover:text-gray-700"
              >
                {mobileMenuOpen ? (
                  <XMarkIcon className="h-6 w-6" />
                ) : (
                  <Bars3Icon className="h-6 w-6" />
                )}
              </button>
            </div>
          </div>

          {/* Mobile Menu - Hidden on desktop */}
          {mobileMenuOpen && (
            <div className="md:hidden py-2 border-t border-gray-200">
              <button 
                onClick={() => {
                  navigate('/dashboard');
                  setMobileMenuOpen(false);
                }}
                className="block w-full text-left px-3 py-2 text-gray-700 hover:text-green-700 hover:bg-gray-50 rounded-md text-sm font-medium"
              >
                <HomeIcon className="h-5 w-5 inline mr-2" />
                Dashboard
              </button>
              <button
                onClick={() => {
                  handleLogout();
                  setMobileMenuOpen(false);
                }}
                className="block w-full text-left px-3 py-2 text-gray-700 hover:text-red-600 hover:bg-gray-50 rounded-md text-sm font-medium"
              >
                <PowerIcon className="h-5 w-5 inline mr-2" />
                Logout
              </button>
            </div>
          )}
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8 py-4 sm:py-6 md:py-8">
        {children}
      </main>
    </div>
  );
};

export default Layout;